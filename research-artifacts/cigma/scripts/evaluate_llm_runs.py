#!/usr/bin/env python3
"""Post-hoc oracle evaluation of archived, bounded LLM candidate runs.

The live adapter never imports or receives the oracle.  This script is invoked
only after raw responses and deterministic validation decisions are frozen.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import statistics
import sys
from pathlib import Path
from typing import Any

from cigma.io import canonical_json_bytes
from cigma.evaluation import map_graph_nodes_to_truth, prediction_edge_set, truth_edge_set
from cigma.model import graph_result_from_dict
from cigma.openai_adapter import (
    _extract_output_text,
    candidate_json_schema,
    validate_candidate_batch,
)


# Immutable registry for the first, manuscript-synchronized live triplicate.
# Keeping these trace identities in versioned implementation code prevents a
# later live call from silently replacing the archived experiment while still
# allowing deterministic validation/evaluation outputs to be regenerated.
ARCHIVED_LIVE_INPUT_SHA256 = (
    "51b01bd64fa9a6a3580e0018b1b61e38f934f46bb463d1ad8efa6b061a20547d"
)
ARCHIVED_RUN_HASHES = {
    "run01": {
        "raw_response.json": "640fe6ae1ec0f28e215ae6866f5c6627456a87316eb1230fb5d27d3512ca2ada",
        "request_manifest.json": "e7f782b49476b20649b93d0c7721552366ea6f26bb723aa2b187545c06e36e04",
    },
    "run02": {
        "raw_response.json": "25618713befae32f2a01bfd29060274f1cc682ea1e36797bfa259292905637c7",
        "request_manifest.json": "e4042595c55e6a322871cf7dc59103ee035e662e553cb9df49efda29398a005c",
    },
    "run03": {
        "raw_response.json": "d56e6483ff25b6893d4e02013c97fcb0ca4dcdc7b61bb184381e299e02095309",
        "request_manifest.json": "20bb72432c4fdde18e131a0056a6790a614e0392efff5e91f8cb7fd6a7eaa983",
    },
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prf(predicted: set[tuple[str, ...]], truth: set[tuple[str, ...]]) -> dict[str, float | int]:
    tp = len(predicted & truth)
    fp = len(predicted - truth)
    fn = len(truth - predicted)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def jaccard(left: set[Any], right: set[Any]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def mapped_triples(
    candidates: list[dict[str, Any]],
    node_truth: dict[str, str | None],
    namespace: str,
) -> set[tuple[str, str, str]]:
    """Map candidates to oracle triples; retain unmappable candidates as FPs."""

    triples: set[tuple[str, str, str]] = set()
    for index, candidate in enumerate(candidates):
        subject = node_truth.get(str(candidate.get("subject")))
        obj = node_truth.get(str(candidate.get("object")))
        predicate = candidate.get("predicate")
        if subject and obj and isinstance(predicate, str):
            triples.add((subject, predicate, obj))
        else:
            claim_id = str(candidate.get("claim_id", index))
            triples.add(
                (
                    f"__unmapped__:{namespace}:{claim_id}:subject",
                    str(predicate),
                    f"__unmapped__:{namespace}:{claim_id}:object",
                )
            )
    return triples


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", required=True, type=Path)
    parser.add_argument("--oracle", required=True, type=Path)
    parser.add_argument("--base-graph", required=True, type=Path)
    parser.add_argument("--validation-graph", required=True, type=Path)
    parser.add_argument("--runs-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    public = read_json(args.public)
    oracle = read_json(args.oracle)
    base_graph = graph_result_from_dict(read_json(args.base_graph))
    validation_graph = graph_result_from_dict(read_json(args.validation_graph))
    if base_graph.method != "cigma_no_paths" or validation_graph.method != "cigma_no_paths":
        raise SystemExit(
            "the frozen LLM evaluation requires cigma_no_paths for both base and validation"
        )
    if set(base_graph.nodes) != set(validation_graph.nodes):
        raise SystemExit("base and validation graphs must share canonical node IDs")
    validation_node_truth, _ = map_graph_nodes_to_truth(validation_graph, oracle)
    base_node_truth, _ = map_graph_nodes_to_truth(base_graph, oracle)

    truth = set(truth_edge_set(oracle))
    base_triples = set(prediction_edge_set(base_graph, base_node_truth))
    incremental_truth = truth - base_triples
    false_evidence_ids = {
        observation_id
        for observation_id, mapped in oracle["claim_observation_map"].items()
        if mapped is None
    }

    run_dirs = sorted(path for path in args.runs_root.glob("run*") if path.is_dir())
    if {path.name for path in run_dirs} != set(ARCHIVED_RUN_HASHES):
        raise SystemExit("run directories do not match the frozen live triplicate")

    rows: list[dict[str, Any]] = []
    raw_sets: dict[str, set[tuple[str, str, str]]] = {}
    accepted_sets: dict[str, set[tuple[str, str, str]]] = {}
    detail: dict[str, Any] = {}
    for run_dir in run_dirs:
        registered_hashes = ARCHIVED_RUN_HASHES[run_dir.name]
        if any(
            sha256_path(run_dir / name) != expected
            for name, expected in registered_hashes.items()
        ):
            raise SystemExit(f"archived trace hash mismatch: {run_dir.name}")
        raw_response = read_json(run_dir / "raw_response.json")
        validated = read_json(run_dir / "validated_candidates.json")
        manifest = read_json(run_dir / "request_manifest.json")
        if manifest.get("input_sha256") != ARCHIVED_LIVE_INPUT_SHA256:
            raise SystemExit(f"archived live-input hash mismatch: {run_dir.name}")
        try:
            batch = json.loads(_extract_output_text(raw_response))
        except json.JSONDecodeError as exc:
            batch = {"candidates": []}
            replay_parse_error = f"invalid_json:{exc.msg}"
        else:
            replay_parse_error = None
        replay_accepted, replay_rejected = validate_candidate_batch(
            batch, public, validation_graph
        )
        raw_hash_match = validated.get("raw_response_sha256") == sha256_path(
            run_dir / "raw_response.json"
        )
        replay_match = (
            replay_accepted == validated.get("accepted")
            and replay_rejected == validated.get("rejected")
            and replay_parse_error == validated.get("parse_error")
        )
        raw_candidates = list(batch.get("candidates", []))
        partitioned = [
            *replay_accepted,
            *(item.get("candidate") for item in replay_rejected),
        ]
        partition_match = sorted(json.dumps(item, sort_keys=True) for item in raw_candidates) == sorted(
            json.dumps(item, sort_keys=True) for item in partitioned
        )
        if (
            not raw_hash_match
            or not replay_match
            or not partition_match
            or validated.get("graph_mutated") is not False
        ):
            raise SystemExit(f"saved validation integrity failure: {run_dir.name}")
        accepted = list(replay_accepted)
        rejected = list(replay_rejected)
        raw_triples = mapped_triples(
            raw_candidates, validation_node_truth, f"{run_dir.name}:raw"
        )
        accepted_triples = mapped_triples(
            accepted, validation_node_truth, f"{run_dir.name}:accepted"
        )
        union_triples = base_triples | accepted_triples
        raw_sets[run_dir.name] = raw_triples
        accepted_sets[run_dir.name] = accepted_triples
        raw_metrics = prf(raw_triples, truth)
        accepted_metrics = prf(accepted_triples, truth)
        hybrid_metrics = prf(union_triples, truth)
        injection_followed = sum(
            any(evidence_id in false_evidence_ids for evidence_id in candidate.get("evidence_ids", []))
            for candidate in raw_candidates
        )
        usage = raw_response.get("usage", {})
        added_correct = len((accepted_triples - base_triples) & incremental_truth)
        row = {
            "run": run_dir.name,
            "requested_model": manifest.get("model"),
            "returned_model": raw_response.get("model"),
            "response_status": raw_response.get("status"),
            "parse_error": validated.get("parse_error") or "",
            "raw_hash_match": raw_hash_match,
            "replay_match": replay_match,
            "partition_match": partition_match,
            "graph_mutated": validated.get("graph_mutated"),
            "raw_candidates": len(raw_candidates),
            "accepted_candidates": len(accepted),
            "rejected_candidates": len(rejected),
            "validator_rejection_rate": len(rejected) / len(raw_candidates) if raw_candidates else 0.0,
            "raw_false_triple_rate": 1.0 - float(raw_metrics["precision"]),
            "accepted_false_triple_rate": 1.0 - float(accepted_metrics["precision"]),
            "raw_precision": raw_metrics["precision"],
            "raw_recall": raw_metrics["recall"],
            "raw_f1": raw_metrics["f1"],
            "accepted_precision": accepted_metrics["precision"],
            "accepted_recall": accepted_metrics["recall"],
            "accepted_f1": accepted_metrics["f1"],
            "hybrid_precision": hybrid_metrics["precision"],
            "hybrid_recall": hybrid_metrics["recall"],
            "hybrid_f1": hybrid_metrics["f1"],
            "incremental_correct_edges": added_correct,
            "incremental_edge_recall": added_correct / len(incremental_truth) if incremental_truth else 0.0,
            "false_evidence_candidates": injection_followed,
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_seconds": manifest.get("latency_seconds", 0.0),
        }
        rows.append(row)
        detail[run_dir.name] = {
            "raw_metrics": raw_metrics,
            "accepted_metrics": accepted_metrics,
            "hybrid_metrics": hybrid_metrics,
            "rejection_reasons": sorted(item.get("reason", "unknown") for item in rejected),
            "raw_triples": sorted([list(item) for item in raw_triples]),
            "accepted_triples": sorted([list(item) for item in accepted_triples]),
        }

    if not rows:
        raise SystemExit("no run directories found")

    pairwise_rows: list[dict[str, Any]] = []
    for left, right in itertools.combinations(sorted(raw_sets), 2):
        pairwise_rows.append({
            "left": left,
            "right": right,
            "raw_triple_jaccard": jaccard(raw_sets[left], raw_sets[right]),
            "accepted_triple_jaccard": jaccard(accepted_sets[left], accepted_sets[right]),
        })

    numeric_mean_fields = [
        "raw_candidates", "accepted_candidates", "rejected_candidates",
        "validator_rejection_rate", "raw_false_triple_rate",
        "accepted_false_triple_rate", "raw_precision",
        "raw_recall", "raw_f1", "accepted_precision", "accepted_recall",
        "accepted_f1", "hybrid_precision", "hybrid_recall", "hybrid_f1",
        "incremental_correct_edges", "incremental_edge_recall",
        "false_evidence_candidates", "input_tokens", "output_tokens",
        "total_tokens", "latency_seconds",
    ]
    means = {
        field: statistics.fmean(float(row[field]) for row in rows)
        for field in numeric_mean_fields
    }
    summary = {
        "runs": len(rows),
        "requested_models": sorted({str(row["requested_model"]) for row in rows}),
        "returned_models": sorted({str(row["returned_model"]) for row in rows}),
        "all_completed": all(row["response_status"] == "completed" for row in rows),
        "all_parseable": all(not row["parse_error"] for row in rows),
        "all_raw_hashes_match": all(row["raw_hash_match"] for row in rows),
        "all_replays_match": all(row["replay_match"] for row in rows),
        "all_partitions_match": all(row["partition_match"] for row in rows),
        "all_graph_mutated_false": all(row["graph_mutated"] is False for row in rows),
        "all_archived_trace_hashes_match": True,
        "archived_live_input_sha256": ARCHIVED_LIVE_INPUT_SHA256,
        "live_fixture_correction": (
            "The live requests used the pre-correction synthetic root-certificate "
            "metadata key_bits=3072 while its algorithm identifier was RSA-2048. "
            "The current fixture corrects key_bits to 2048; relation observations, "
            "canonical node IDs, and the replay partitions are unchanged."
        ),
        "oracle_edges": len(truth),
        "base_graph_method": base_graph.method,
        "validation_graph_method": validation_graph.method,
        "base_predicted_edges": len(base_triples),
        "base_true_positive_edges": len(base_triples & truth),
        "base_false_positive_edges": len(base_triples - truth),
        "base_recall": len(base_triples & truth) / len(truth) if truth else 0.0,
        "incremental_truth_edges": len(incremental_truth),
        "hybrid_definition": (
            f"union of supplied base graph ({base_graph.method}) predictions and validated "
            "LLM candidates on shared "
            "canonical node IDs; executable after CIGMA entity resolution but not an "
            "independent end-to-end LLM pipeline"
        ),
        "means": means,
        "pairwise_raw_jaccard_mean": statistics.fmean(row["raw_triple_jaccard"] for row in pairwise_rows),
        "pairwise_accepted_jaccard_mean": statistics.fmean(row["accepted_triple_jaccard"] for row in pairwise_rows),
        "aggregate_usage": {
            key: int(sum(int(row[key]) for row in rows))
            for key in ["input_tokens", "output_tokens", "total_tokens"]
        },
        "caveat": (
            "Three repeated calls on one synthetic fixture measure service variability, "
            "not generalization. The model saw no oracle, existing graph edges, computed "
            "scores, or structured attributes; verbatim public evidence excerpts did contain "
            "observed business context including criticality, exposure, lifetime, and agility. "
            "The archived live input preceded a correction of the synthetic root certificate "
            "from key_bits=3072 to 2048 so that it matches RSA-2048; deterministic replay uses "
            "the corrected fixture, with unchanged relation observations and node IDs. "
            f"Deterministic candidate validation and the union use the same supplied "
            f"{base_graph.method} graph and shared node IDs. The union isolates candidate "
            "path composition, "
            "is executable after CIGMA entity resolution, and is not an independent end-to-end "
            "LLM pipeline."
        ),
        "per_run": detail,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "runs.csv", rows)
    write_csv(args.output / "pairwise_jaccard.csv", pairwise_rows)
    write_json(args.output / "summary.json", summary)
    macros = [
        "% Auto-generated by scripts/evaluate_llm_runs.py; do not edit.",
        f"\\newcommand{{\\LLMRuns}}{{{len(rows)}}}",
        f"\\newcommand{{\\LLMBasePrecision}}{{{len(base_triples & truth) / len(base_triples) if base_triples else 0.0:.4f}}}",
        f"\\newcommand{{\\LLMBaseRecall}}{{{len(base_triples & truth) / len(truth) if truth else 0.0:.4f}}}",
        f"\\newcommand{{\\LLMBaseFOne}}{{{prf(base_triples, truth)['f1']:.4f}}}",
        f"\\newcommand{{\\LLMRawPrecision}}{{{means['raw_precision']:.4f}}}",
        f"\\newcommand{{\\LLMRawRecall}}{{{means['raw_recall']:.4f}}}",
        f"\\newcommand{{\\LLMRawFOne}}{{{means['raw_f1']:.4f}}}",
        f"\\newcommand{{\\LLMValidatedPrecision}}{{{means['accepted_precision']:.4f}}}",
        f"\\newcommand{{\\LLMValidatedRecall}}{{{means['accepted_recall']:.4f}}}",
        f"\\newcommand{{\\LLMValidatedFOne}}{{{means['accepted_f1']:.4f}}}",
        f"\\newcommand{{\\LLMHybridPrecision}}{{{means['hybrid_precision']:.4f}}}",
        f"\\newcommand{{\\LLMHybridRecall}}{{{means['hybrid_recall']:.4f}}}",
        f"\\newcommand{{\\LLMHybridFOne}}{{{means['hybrid_f1']:.4f}}}",
        f"\\newcommand{{\\LLMValidatorRejection}}{{{100 * means['validator_rejection_rate']:.1f}\\%}}",
        f"\\newcommand{{\\LLMRawFalseTripleRate}}{{{100 * means['raw_false_triple_rate']:.1f}\\%}}",
        f"\\newcommand{{\\LLMAcceptedFalseTripleRate}}{{{100 * means['accepted_false_triple_rate']:.1f}\\%}}",
        f"\\newcommand{{\\LLMIncrementalRecall}}{{{means['incremental_edge_recall']:.4f}}}",
        f"\\newcommand{{\\LLMAcceptedJaccard}}{{{summary['pairwise_accepted_jaccard_mean']:.4f}}}",
        f"\\newcommand{{\\LLMInputTokens}}{{{summary['aggregate_usage']['input_tokens']}}}",
        f"\\newcommand{{\\LLMOutputTokens}}{{{summary['aggregate_usage']['output_tokens']}}}",
    ]
    (args.output / "paper_macros.tex").write_text("\n".join(macros) + "\n", encoding="utf-8")
    output_files = [
        args.output / "runs.csv",
        args.output / "pairwise_jaccard.csv",
        args.output / "summary.json",
        args.output / "paper_macros.tex",
    ]
    artifact_root = Path(__file__).resolve().parents[1]
    implementation_paths = [
        Path(__file__).resolve(),
        artifact_root / "src/cigma/evaluation.py",
        artifact_root / "src/cigma/io.py",
        artifact_root / "src/cigma/model.py",
        artifact_root / "src/cigma/ontology.py",
        artifact_root / "src/cigma/openai_adapter.py",
        artifact_root / "src/cigma/validation.py",
    ]
    evaluation_manifest = {
        "network_required": False,
        "oracle_usage": "post-hoc evaluation only; never supplied to the live adapter",
        "argv": sys.argv,
        "script_sha256": sha256_path(Path(__file__)),
        "implementation_files": {
            str(path.relative_to(artifact_root)): sha256_path(path)
            for path in implementation_paths
        },
        "schema_sha256": hashlib.sha256(
            canonical_json_bytes(candidate_json_schema())
        ).hexdigest(),
        "base_graph_method": base_graph.method,
        "validation_graph_method": validation_graph.method,
        "inputs": {
            "public": {"path": str(args.public), "sha256": sha256_path(args.public)},
            "oracle": {"path": str(args.oracle), "sha256": sha256_path(args.oracle)},
            "base_graph": {"path": str(args.base_graph), "sha256": sha256_path(args.base_graph)},
            "validation_graph": {"path": str(args.validation_graph), "sha256": sha256_path(args.validation_graph)},
            "runs": {
                run_dir.name: {
                    name: sha256_path(run_dir / name)
                    for name in (
                        "raw_response.json",
                        "request_manifest.json",
                        "validated_candidates.json",
                    )
                }
                for run_dir in run_dirs
            },
        },
        "outputs": {
            path.name: sha256_path(path)
            for path in output_files
        },
    }
    write_json(args.output / "manifest.json", evaluation_manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
