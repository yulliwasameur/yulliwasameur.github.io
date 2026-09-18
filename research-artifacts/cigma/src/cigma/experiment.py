"""End-to-end deterministic campaign, ablation, and robustness runner."""

from __future__ import annotations

import copy
import importlib.metadata
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ARTIFACT_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("MPLCONFIGDIR", str(ARTIFACT_ROOT / ".mplconfig"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

from .benchmark import generate_benchmark
from .evaluation import evaluate_method
from .io import (
    artifact_files,
    load_config as _load_config,
    mark_output,
    safe_clean_output,
    sha256_file,
    write_csv,
    write_json,
)
from .pipeline import run_pipeline, source_dropout_spec
from .scoring import fit_independent_calibrator, score_graph
from .statistics import bootstrap_mean_ci, paired_comparison
from .validation import (
    validate_oracle,
    validate_public_observations,
    validate_source_reliability,
)


BASE_METHODS = (
    "tls_inventory",
    "cbom_inventory",
    "source_union",
    "exact_direct",
    "cigma",
)
ABLATION_METHODS = (
    "cigma_no_alias",
    "cigma_no_paths",
    "cigma_no_quality_gate",
    "cigma_uniform_reliability",
)


def load_config(path: Path) -> dict[str, Any]:
    return _load_config(path)


def materialize_dataset(
    public: dict[str, Any], oracle: dict[str, Any], output: Path
) -> None:
    validate_public_observations(public)
    validate_oracle(oracle, public)
    write_json(output / "data" / "public" / "observations.json", public)
    write_json(output / "data" / "oracle" / "oracle.json", oracle)
    (output / "data").mkdir(parents=True, exist_ok=True)
    (output / "data" / "README.txt").write_text(
        "public/ is method input. oracle/ is evaluator-only and is passed only "
        "after graph construction and ranking have completed.\n",
        encoding="utf-8",
    )


def perturb_public(
    public: dict[str, Any], *, seed: int, observation_dropout: float
) -> dict[str, Any]:
    """Apply a seeded missing-observation perturbation without touching oracle."""

    if not 0.0 <= observation_dropout < 1.0:
        raise ValueError("observation_dropout must be in [0,1)")
    rng = np.random.default_rng(seed)
    result = copy.deepcopy(public)
    retained_entities = [
        item for item in result["entities"] if float(rng.random()) >= observation_dropout
    ]
    retained_ids = {item["observation_id"] for item in retained_entities}
    retained_claims = [
        item
        for item in result["claims"]
        if item["subject_observation_id"] in retained_ids
        and item["object_observation_id"] in retained_ids
        and float(rng.random()) >= observation_dropout
    ]
    result["entities"] = retained_entities
    result["claims"] = retained_claims
    result["metadata"]["perturbation"] = {
        "seed": seed,
        "observation_dropout": observation_dropout,
    }
    validate_public_observations(result)
    return result


def run_campaign(config: dict[str, Any], output: Path) -> dict[str, Any]:
    """Run primary methods, ablations, 32+ perturbations, and statistics."""

    validate_source_reliability(config)
    if output.exists():
        safe_clean_output(output)
    output.mkdir(parents=True, exist_ok=True)
    mark_output(output)
    public, oracle = generate_benchmark(config)
    materialize_dataset(public, oracle, output)
    config_text = yaml.safe_dump(config, sort_keys=True)
    (output / "config.snapshot.yaml").write_text(config_text, encoding="utf-8")

    calibrator = fit_independent_calibrator(
        ARTIFACT_ROOT
        / str(
            config.get("calibration", {}).get(
                "panel", "fixtures/calibration_panel.csv"
            )
        ),
        seed=int(config.get("seed", 586)),
    )
    write_json(output / "metrics" / "calibrator.json", calibrator)

    metrics_by_method: dict[str, dict[str, Any]] = {}
    details_by_method: dict[str, dict[str, Any]] = {}
    scores_by_method: dict[str, list[dict[str, Any]]] = {}
    graphs_by_method: dict[str, Any] = {}
    for method in BASE_METHODS + ABLATION_METHODS:
        graph, scores, metrics, details = _run_one(
            public, oracle, config, method, calibrator
        )
        graphs_by_method[graph.method] = graph
        scores_by_method[graph.method] = scores
        metrics_by_method[graph.method] = metrics
        details_by_method[graph.method] = details
        write_json(output / "graphs" / f"{graph.method}.json", graph.to_dict())
        write_json(output / "evaluation" / f"{graph.method}.json", details)
        write_csv(output / "rankings" / f"{graph.method}.csv", scores)

    source_dropout_rows: list[dict[str, Any]] = []
    for source in public["metadata"]["sources"]:
        spec = source_dropout_spec(source)
        graph, scores, metrics, details = _run_one(
            public, oracle, config, spec, calibrator
        )
        source_dropout_rows.append(
            {
                "dropped_source": source,
                "excluded_source": source,
                "graph_nodes": len(graph.nodes),
                "graph_edges": len(graph.edges),
                **metrics,
            }
        )
        write_json(output / "graphs" / f"{graph.method}.json", graph.to_dict())
        write_json(output / "evaluation" / f"{graph.method}.json", details)
        write_csv(output / "rankings" / f"{graph.method}.csv", scores)
    write_csv(output / "metrics" / "source_dropout.csv", source_dropout_rows)
    write_csv(output / "metrics" / "leave_one_source_out.csv", source_dropout_rows)

    metric_rows = [metrics_by_method[key] for key in sorted(metrics_by_method)]
    write_csv(output / "metrics" / "method_metrics.csv", metric_rows)
    _write_compatibility_metric_tables(output, metric_rows, scores_by_method)

    robustness_rows = _run_robustness(public, oracle, config, calibrator)
    write_csv(output / "metrics" / "robustness_runs.csv", robustness_rows)
    robustness_aggregate = _aggregate_robustness(robustness_rows, config)
    write_csv(
        output / "metrics" / "robustness_aggregate.csv",
        robustness_aggregate,
    )
    statistics_rows = _summarize_robustness(robustness_rows, config)
    write_csv(output / "metrics" / "statistics.csv", statistics_rows)

    _plot_primary_metrics(metric_rows, output / "figures" / "campaign_metrics.png")
    cigma = metrics_by_method["cigma"]
    cigma_graph = graphs_by_method["cigma"]
    rejection_reasons = Counter(
        item.get("reason", "unknown") for item in cigma_graph.rejected_claims
    )
    summary: dict[str, Any] = {
        "scenario": public["metadata"],
        "benchmark": {
            "public_entity_observations": len(public["entities"]),
            "public_claim_observations": len(public["claims"]),
            "oracle_nodes": len(oracle["nodes"]),
            "oracle_edges": len(oracle["edges"]),
            "source_families": len(public["metadata"]["sources"]),
        },
        "cigma": {
            "node_f1": float(cigma["asset_f1"]),
            "asset_f1": float(cigma["asset_f1"]),
            "entity_f1": float(cigma["entity_f1"]),
            "b3_f1": float(cigma["b3_f1"]),
            "edge_f1": float(cigma["edge_f1"]),
            "critical_misses": int(cigma["critical_misses"]),
            "critical_miss_rate": float(cigma["critical_miss_rate"]),
            "unsupported_edge_rate": float(cigma["unsupported_edge_rate"]),
            "ranking_ndcg": float(cigma["ndcg_primary"]),
            "ndcg_at_5": float(cigma["ndcg_at_5_primary"]),
            "ndcg_at_10": float(cigma["ndcg_at_10_primary"]),
            "kendall_tau_b": float(cigma["kendall_tau_b_primary"]),
            "calibration_brier": float(cigma["edge_brier"]),
            "edge_brier": float(cigma["edge_brier"]),
            "edge_ece": float(cigma["edge_ece"]),
            "urgency_brier": float(cigma["urgency_brier"]),
            "urgency_ece": float(cigma["urgency_ece"]),
            "accepted_nodes": len(cigma_graph.nodes),
            "accepted_edges": len(cigma_graph.edges),
            "rejected_claims": len(cigma_graph.rejected_claims),
            "rejection_reasons": dict(sorted(rejection_reasons.items())),
            "verification_queue_size": int(cigma["verification_queue_size"]),
            "provenance_invariant": bool(cigma["provenance_invariant"]),
        },
        "robustness": {
            "seeds": int(config.get("robustness", {}).get("seeds", 32)),
            "seeded_perturbations": int(
                config.get("robustness", {}).get("seeds", 32)
            ),
            "dropout_levels": list(
                config.get("robustness", {}).get(
                    "observation_dropout", [0.0, 0.10, 0.25, 0.50]
                )
            ),
            "total_runs": len(robustness_rows),
            "scenario_runs": len(robustness_rows) // 3,
            "methods_per_scenario": 3,
            "leave_one_source_out_runs": len(source_dropout_rows),
        },
        "calibration_scope": calibrator["training_scope"],
        "caveat": (
            "Results are measured on the deterministic synthetic CIGMA-Lab "
            "fixture and seeded missing-observation perturbations; they are not "
            "evidence of enterprise-wide generalization or expert agreement."
        ),
    }
    write_json(output / "summary.json", summary)
    write_json(
        output / "metrics" / "robustness_summary.json",
        {
            "design": summary["robustness"],
            "aggregate": robustness_aggregate,
        },
    )
    _write_paper_macros(output / "paper_macros.tex", summary)
    manifest = {
        "artifact_version": "0.2.0",
        "seed": int(config.get("seed", 586)),
        "packages": _package_versions(),
        "files": {
            str(path.relative_to(output)): sha256_file(path)
            for path in artifact_files(output)
        },
        "implementation_files": _implementation_hashes(),
        "oracle_isolation": (
            "construction and scoring functions receive public payload only"
        ),
        "network_required": False,
    }
    write_json(output / "manifest.json", manifest)
    return summary


def _run_one(
    public: dict[str, Any],
    oracle: dict[str, Any],
    config: dict[str, Any],
    method: Any,
    calibrator: dict[str, Any],
) -> tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    graph = run_pipeline(public, config, method)
    scores = score_graph(graph, config, calibrator=calibrator)
    metrics, details = evaluate_method(graph, scores, oracle, public, config)
    return graph, scores, metrics, details


def _run_robustness(
    public: dict[str, Any],
    oracle: dict[str, Any],
    config: dict[str, Any],
    calibrator: dict[str, Any],
) -> list[dict[str, Any]]:
    robustness = config.get("robustness", {})
    seed_count = int(robustness.get("seeds", 32))
    if seed_count < 2:
        raise ValueError("robustness.seeds must be at least 2")
    levels = [
        float(value)
        for value in robustness.get(
            "observation_dropout", [0.0, 0.10, 0.25, 0.50]
        )
    ]
    base_seed = int(config.get("seed", 586))
    methods = ("source_union", "exact_direct", "cigma")
    rows: list[dict[str, Any]] = []
    for level_index, level in enumerate(levels):
        for replicate in range(seed_count):
            perturbation_seed = base_seed + 10_000 + level_index * 1_000 + replicate
            perturbed = perturb_public(
                public,
                seed=perturbation_seed,
                observation_dropout=level,
            )
            for method in methods:
                _, _, metrics, _ = _run_one(
                    perturbed, oracle, config, method, calibrator
                )
                rows.append(
                    {
                        "replicate": replicate,
                        "perturbation_seed": perturbation_seed,
                        "observation_dropout": level,
                        **metrics,
                    }
                )
    return rows


def _aggregate_robustness(
    rows: list[dict[str, Any]], config: dict[str, Any]
) -> list[dict[str, Any]]:
    """Aggregate fixed outcomes with deterministic bootstrap intervals."""

    metric_names = (
        "asset_f1",
        "entity_f1",
        "b3_f1",
        "edge_f1",
        "critical_miss_rate",
        "ndcg_at_5_primary",
        "ndcg_at_10_primary",
        "kendall_tau_b_primary",
        "edge_brier",
        "urgency_brier",
    )
    grouped: dict[tuple[float, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(float(row["observation_dropout"]), str(row["method"]))].append(row)
    seed = int(config.get("seed", 586))
    resamples = int(config.get("evaluation", {}).get("bootstrap_resamples", 5000))
    aggregates: list[dict[str, Any]] = []
    for (dropout, method), group in sorted(grouped.items()):
        ordered = sorted(group, key=lambda row: int(row["replicate"]))
        for metric in metric_names:
            values = np.asarray([float(row[metric]) for row in ordered], dtype=float)
            interval = bootstrap_mean_ci(
                values,
                seed=seed + int(dropout * 10_000) + len(method) + len(metric),
                resamples=resamples,
            )
            aggregates.append(
                {
                    "observation_dropout": dropout,
                    "method": method,
                    "metric": metric,
                    "n": int(interval["n"]),
                    "mean": float(interval["mean"]),
                    "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
                    "ci95_low": float(interval["ci_low"]),
                    "ci95_high": float(interval["ci_high"]),
                }
            )
    return aggregates


def _summarize_robustness(
    rows: list[dict[str, Any]], config: dict[str, Any]
) -> list[dict[str, Any]]:
    grouped: dict[tuple[float, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(float(row["observation_dropout"]), str(row["method"]))].append(row)
    seed = int(config.get("seed", 586))
    resamples = int(config.get("evaluation", {}).get("bootstrap_resamples", 5000))
    permutations = int(config.get("evaluation", {}).get("permutations", 10000))
    metrics = ("asset_f1", "entity_f1", "edge_f1", "ndcg_primary")
    output: list[dict[str, Any]] = []
    for (level, method), group in sorted(grouped.items()):
        ordered = sorted(group, key=lambda row: int(row["replicate"]))
        for metric in metrics:
            interval = bootstrap_mean_ci(
                [float(row[metric]) for row in ordered],
                seed=seed + int(level * 10_000) + len(metric) + len(method),
                resamples=resamples,
            )
            output.append(
                {
                    "analysis": "bootstrap_mean",
                    "observation_dropout": level,
                    "method": method,
                    "baseline": "",
                    "metric": metric,
                    **interval,
                    "mean_difference": "",
                    "permutation_p": "",
                }
            )
    for level in sorted({key[0] for key in grouped}):
        # At zero dropout every replicate is the same deterministic fixture;
        # treating those copies as independent pairs would produce a spurious
        # p-value. We report the descriptive bootstrap row above and reserve
        # paired randomization for genuinely distinct perturbation masks.
        if level == 0.0:
            continue
        cigma = sorted(
            grouped[(level, "cigma")], key=lambda row: int(row["replicate"])
        )
        for baseline in ("source_union", "exact_direct"):
            reference = sorted(
                grouped[(level, baseline)], key=lambda row: int(row["replicate"])
            )
            for metric in metrics:
                comparison = paired_comparison(
                    [float(row[metric]) for row in cigma],
                    [float(row[metric]) for row in reference],
                    seed=seed + int(level * 10_000) + len(metric) + len(baseline),
                    resamples=resamples,
                    permutations=permutations,
                )
                output.append(
                    {
                        "analysis": "paired_cigma_difference",
                        "observation_dropout": level,
                        "method": "cigma",
                        "baseline": baseline,
                        "metric": metric,
                        "mean": "",
                        **comparison,
                    }
                )
    return output


def _write_compatibility_metric_tables(
    output: Path,
    metric_rows: list[dict[str, Any]],
    scores_by_method: dict[str, list[dict[str, Any]]],
) -> None:
    write_csv(
        output / "metrics" / "nodes.csv",
        [
            {
                "method": row["method"],
                "precision": row["asset_precision"],
                "recall": row["asset_recall"],
                "f1": row["asset_f1"],
                "entity_f1": row["entity_f1"],
            }
            for row in metric_rows
        ],
    )
    write_csv(
        output / "metrics" / "edges.csv",
        [
            {
                "method": row["method"],
                "precision": row["edge_precision"],
                "recall": row["edge_recall"],
                "f1": row["edge_f1"],
                "unsupported_edge_rate": row["unsupported_edge_rate"],
            }
            for row in metric_rows
        ],
    )
    write_csv(
        output / "metrics" / "ranking.csv",
        [
            {
                "method": row["method"],
                "ndcg": row["ndcg_primary"],
                "ndcg_weighted": row["ndcg_weighted"],
                "ndcg_rank_aggregation": row["ndcg_rank_aggregation"],
            }
            for row in metric_rows
        ],
    )
    write_csv(
        output / "metrics" / "calibration.csv",
        [
            {
                "method": row["method"],
                "brier": row["edge_brier"],
                "ece": row["edge_ece"],
                "urgency_brier": row["urgency_brier"],
                "urgency_ece": row["urgency_ece"],
            }
            for row in metric_rows
        ],
    )
    write_csv(
        output / "metrics" / "scores.csv",
        [
            row
            for method in sorted(scores_by_method)
            for row in scores_by_method[method]
        ],
    )


def _plot_primary_metrics(rows: list[dict[str, Any]], output: Path) -> None:
    methods = [
        name for name in BASE_METHODS if any(row["method"] == name for row in rows)
    ]
    index = {row["method"]: row for row in rows}
    x = np.arange(len(methods))
    width = 0.25
    fig, axis = plt.subplots(figsize=(10.5, 4.8))
    axis.bar(
        x - width,
        [index[name]["asset_f1"] for name in methods],
        width,
        label="Asset F1",
    )
    axis.bar(
        x,
        [index[name]["entity_f1"] for name in methods],
        width,
        label="Entity F1",
    )
    axis.bar(
        x + width,
        [index[name]["edge_f1"] for name in methods],
        width,
        label="Edge F1",
    )
    axis.set_xticks(x, methods, rotation=20, ha="right")
    axis.set_ylim(0.0, 1.05)
    axis.set_ylabel("Score")
    axis.set_title("CIGMA-Lab inventory and graph accuracy")
    axis.legend(frameon=False, ncols=3)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def _package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for package in (
        "numpy",
        "pandas",
        "scikit-learn",
        "scipy",
        "matplotlib",
        "PyYAML",
    ):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not-installed"
    return versions


def _implementation_hashes() -> dict[str, str]:
    roots = [
        ARTIFACT_ROOT / "src" / "cigma",
        ARTIFACT_ROOT / "scripts",
        ARTIFACT_ROOT / "configs",
        ARTIFACT_ROOT / "fixtures",
        ARTIFACT_ROOT / "prompts",
        ARTIFACT_ROOT / "tests",
    ]
    paths = [
        path
        for root in roots
        for path in root.rglob("*")
        if path.is_file() and path.suffix not in {".pyc", ".pyo"}
    ]
    paths.extend(
        [
            ARTIFACT_ROOT / "pyproject.toml",
            ARTIFACT_ROOT / "requirements-lock.txt",
            ARTIFACT_ROOT / "Makefile",
            ARTIFACT_ROOT / "README.md",
            ARTIFACT_ROOT / ".gitignore",
        ]
    )
    return {
        str(path.relative_to(ARTIFACT_ROOT)): sha256_file(path)
        for path in sorted(set(paths))
    }


def _write_paper_macros(path: Path, summary: dict[str, Any]) -> None:
    """Export measured values without editing or compiling the manuscript."""

    cigma = summary["cigma"]
    benchmark = summary["benchmark"]
    robustness = summary["robustness"]
    lines = [
        "% Auto-generated by the CIGMA artifact; do not edit manually.",
        f"\\newcommand{{\\CigmaEntityObs}}{{{benchmark['public_entity_observations']}}}",
        f"\\newcommand{{\\CigmaClaimObs}}{{{benchmark['public_claim_observations']}}}",
        f"\\newcommand{{\\CigmaAssetFOne}}{{{cigma['asset_f1']:.4f}}}",
        f"\\newcommand{{\\CigmaEntityFOne}}{{{cigma['entity_f1']:.4f}}}",
        f"\\newcommand{{\\CigmaBThreeFOne}}{{{cigma['b3_f1']:.4f}}}",
        f"\\newcommand{{\\CigmaEdgeFOne}}{{{cigma['edge_f1']:.4f}}}",
        f"\\newcommand{{\\CigmaPrimaryNDCG}}{{{cigma['ranking_ndcg']:.4f}}}",
        f"\\newcommand{{\\CigmaNDCGFive}}{{{cigma['ndcg_at_5']:.4f}}}",
        f"\\newcommand{{\\CigmaNDCGTen}}{{{cigma['ndcg_at_10']:.4f}}}",
        f"\\newcommand{{\\CigmaKendallTauB}}{{{cigma['kendall_tau_b']:.4f}}}",
        f"\\newcommand{{\\CigmaEdgeBrier}}{{{cigma['edge_brier']:.4f}}}",
        f"\\newcommand{{\\CigmaCriticalMissRate}}{{{cigma['critical_miss_rate']:.4f}}}",
        f"\\newcommand{{\\CigmaPerturbationSeeds}}{{{robustness['seeded_perturbations']}}}",
        f"\\newcommand{{\\CigmaRobustnessRuns}}{{{robustness['total_runs']}}}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
