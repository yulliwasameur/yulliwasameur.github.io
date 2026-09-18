"""Oracle-side evaluator for inventory, graph, ranking, and calibration quality."""

from __future__ import annotations

import itertools
import math
from collections import Counter
from typing import Any

import numpy as np
from scipy.stats import kendalltau, spearmanr
from sklearn.metrics import ndcg_score

from .model import GraphResult
from .validation import validate_source_reliability


def evaluate_method(
    graph: GraphResult,
    ranking: list[dict[str, Any]],
    oracle: dict[str, Any],
    public: dict[str, Any],
    config: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Evaluate a completed prediction; the construction pipeline never sees oracle."""

    node_truth, node_conflicts = map_graph_nodes_to_truth(graph, oracle)
    asset_counts = _asset_inventory_counts(graph, node_truth, oracle)
    entity_counts = _entity_resolution_counts(graph, oracle, public)
    b3_metrics = _b3_entity_resolution(graph, oracle, public)
    edge_counts, edge_rows = _edge_counts(graph, node_truth, oracle)
    edge_rows.extend(
        _rejected_claim_calibration_rows(graph, public, oracle, config)
    )
    ranking_metrics, ranking_rows = _ranking_metrics(
        ranking,
        node_truth,
        oracle,
        int(config.get("evaluation", {}).get("ranking_k", 5)),
        int(config.get("evaluation", {}).get("calibration_bins", 5)),
    )
    edge_labels = [row["label"] for row in edge_rows]
    edge_probabilities = [row["confidence"] for row in edge_rows]
    edge_brier = _brier(edge_labels, edge_probabilities)
    edge_ece = _ece(
        edge_labels,
        edge_probabilities,
        int(config.get("evaluation", {}).get("calibration_bins", 5)),
    )
    provenance_ok = all(edge.evidence_ids for edge in graph.edges) and all(
        node.member_observation_ids for node in graph.nodes.values()
    )
    oracle_nodes = {node["id"]: node for node in oracle["nodes"]}
    critical_truths = {
        truth_id
        for truth_id, node in oracle_nodes.items()
        if bool(node.get("migration_target")) and int(node.get("priority", 0)) >= 2
    }
    discovered_truths = {value for value in node_truth.values() if value is not None}
    critical_misses = len(critical_truths - discovered_truths)
    metrics: dict[str, Any] = {
        "method": graph.method,
        **_metrics_from_counts("asset", asset_counts),
        **_metrics_from_counts("entity", entity_counts),
        **b3_metrics,
        **_metrics_from_counts("edge", edge_counts),
        "critical_misses": critical_misses,
        "critical_miss_rate": _safe_div(critical_misses, len(critical_truths)),
        "unsupported_edge_rate": _safe_div(edge_counts["fp"], edge_counts["predicted"]),
        "edge_brier": edge_brier,
        "edge_ece": edge_ece,
        "edge_calibration_cases": len(edge_rows),
        "edge_calibration_positive_fraction": _safe_div(
            sum(edge_labels), len(edge_labels)
        ),
        "node_truth_conflicts": node_conflicts,
        "provenance_invariant": bool(provenance_ok),
        "verification_queue_size": sum(
            bool(row.get("verification_required")) for row in ranking
        ),
        **ranking_metrics,
    }
    details = {
        "asset_counts": asset_counts,
        "entity_counts": entity_counts,
        "edge_counts": edge_counts,
        "edge_rows": edge_rows,
        "ranking_rows": ranking_rows,
        "node_truth": node_truth,
    }
    return metrics, details


def _rejected_claim_calibration_rows(
    graph: GraphResult,
    public: dict[str, Any],
    oracle: dict[str, Any],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    """Include fail-closed claim decisions as calibration negatives/positives."""

    claims = {item["observation_id"]: item for item in public["claims"]}
    claim_truth = oracle["claim_observation_map"]
    reliability = validate_source_reliability(config)
    rows: list[dict[str, Any]] = []
    for rejection in graph.rejected_claims:
        observation_id = rejection.get("observation_id")
        if observation_id not in claims:
            continue
        claim = claims[observation_id]
        confidence = max(
            0.0,
            min(
                1.0,
                float(claim.get("quality", 0.0))
                * float(reliability.get(claim.get("source"), 0.5)),
            ),
        )
        rows.append(
            {
                "claim_id": observation_id,
                "triple": claim_truth.get(observation_id),
                "confidence": confidence,
                "label": int(claim_truth.get(observation_id) is not None),
                "duplicate": False,
                "decision": "rejected",
                "rejection_reason": rejection.get("reason"),
            }
        )
    return sorted(rows, key=lambda row: row["claim_id"])


def map_graph_nodes_to_truth(
    graph: GraphResult, oracle: dict[str, Any]
) -> tuple[dict[str, str | None], int]:
    observation_map = oracle["entity_observation_map"]
    result: dict[str, str | None] = {}
    conflicts = 0
    for node_id, node in graph.nodes.items():
        truths = [
            observation_map.get(observation_id)
            for observation_id in node.member_observation_ids
            if observation_map.get(observation_id) is not None
        ]
        if not truths:
            result[node_id] = None
            continue
        counts = Counter(truths)
        if len(counts) > 1:
            conflicts += 1
        result[node_id] = sorted(counts, key=lambda key: (-counts[key], key))[0]
    return result, conflicts


def prediction_edge_set(
    graph: GraphResult, node_truth: dict[str, str | None]
) -> set[tuple[str, str, str] | tuple[str, str, str, str]]:
    predictions: set[tuple[str, str, str] | tuple[str, str, str, str]] = set()
    for edge in graph.edges:
        subject_truth = node_truth.get(edge.subject)
        object_truth = node_truth.get(edge.object)
        if subject_truth is None or object_truth is None:
            predictions.add(("unmapped", edge.claim_id, edge.predicate, edge.object))
        else:
            predictions.add((subject_truth, edge.predicate, object_truth))
    return predictions


def truth_edge_set(oracle: dict[str, Any]) -> set[tuple[str, str, str]]:
    return {tuple(edge) for edge in oracle["edges"]}


def _asset_inventory_counts(
    graph: GraphResult,
    node_truth: dict[str, str | None],
    oracle: dict[str, Any],
) -> dict[str, int]:
    truth_assets = set(oracle["detectable_nodes"])
    mapped_clusters = [node_truth[node_id] for node_id in sorted(graph.nodes)]
    counts = Counter(value for value in mapped_clusters if value is not None)
    discovered = set(counts) & truth_assets
    duplicate_clusters = sum(max(0, count - 1) for count in counts.values())
    unmapped_clusters = sum(value is None for value in mapped_clusters)
    out_of_scope = len(set(counts) - truth_assets)
    tp = len(discovered)
    return {
        "tp": tp,
        "fp": duplicate_clusters + unmapped_clusters + out_of_scope,
        "fn": len(truth_assets - discovered),
        "predicted": len(graph.nodes),
        "truth": len(truth_assets),
    }


def _entity_resolution_counts(
    graph: GraphResult,
    oracle: dict[str, Any],
    public: dict[str, Any],
) -> dict[str, int]:
    truth_map = oracle["entity_observation_map"]
    prediction_map: dict[str, str] = {}
    for node_id, node in graph.nodes.items():
        for observation_id in node.member_observation_ids:
            prediction_map[observation_id] = node_id
    eligible = sorted(
        item["observation_id"]
        for item in public["entities"]
        if truth_map[item["observation_id"]] is not None
    )
    tp = fp = fn = 0
    for left, right in itertools.combinations(eligible, 2):
        truth_same = truth_map[left] == truth_map[right]
        prediction_same = prediction_map.get(left, f"missing:{left}") == prediction_map.get(
            right, f"missing:{right}"
        )
        if truth_same and prediction_same:
            tp += 1
        elif not truth_same and prediction_same:
            fp += 1
        elif truth_same and not prediction_same:
            fn += 1
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "predicted": tp + fp,
        "truth": tp + fn,
    }


def _b3_entity_resolution(
    graph: GraphResult,
    oracle: dict[str, Any],
    public: dict[str, Any],
) -> dict[str, float]:
    """B-cubed precision/recall over observable entity mentions."""

    truth_map = oracle["entity_observation_map"]
    eligible = {
        item["observation_id"]
        for item in public["entities"]
        if truth_map.get(item["observation_id"]) is not None
    }
    truth_clusters: dict[str, set[str]] = {}
    for observation_id in eligible:
        truth_clusters.setdefault(str(truth_map[observation_id]), set()).add(observation_id)
    predicted_clusters: dict[str, set[str]] = {}
    mention_to_prediction: dict[str, str] = {}
    for node_id, node in graph.nodes.items():
        predicted_clusters[node_id] = set(node.member_observation_ids)
        for observation_id in node.member_observation_ids:
            mention_to_prediction[observation_id] = node_id
    precision_values: list[float] = []
    recall_values: list[float] = []
    for observation_id in sorted(eligible):
        prediction_id = mention_to_prediction.get(observation_id)
        if prediction_id is None:
            precision_values.append(0.0)
            recall_values.append(0.0)
            continue
        truth_members = truth_clusters[str(truth_map[observation_id])]
        predicted_members = predicted_clusters[prediction_id]
        overlap = len(truth_members & predicted_members)
        precision_values.append(_safe_div(overlap, len(predicted_members)))
        recall_values.append(_safe_div(overlap, len(truth_members)))
    precision = float(np.mean(precision_values)) if precision_values else 0.0
    recall = float(np.mean(recall_values)) if recall_values else 0.0
    return {
        "b3_precision": precision,
        "b3_recall": recall,
        "b3_f1": _safe_div(2.0 * precision * recall, precision + recall),
    }


def _edge_counts(
    graph: GraphResult,
    node_truth: dict[str, str | None],
    oracle: dict[str, Any],
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    truth = truth_edge_set(oracle)
    seen_true: set[tuple[str, str, str]] = set()
    rows: list[dict[str, Any]] = []
    fp = 0
    for edge in graph.edges:
        subject_truth = node_truth.get(edge.subject)
        object_truth = node_truth.get(edge.object)
        triple = (
            subject_truth,
            edge.predicate,
            object_truth,
        ) if subject_truth is not None and object_truth is not None else None
        label = int(triple in truth) if triple is not None else 0
        duplicate = bool(label and triple in seen_true)
        if label and not duplicate:
            seen_true.add(triple)  # type: ignore[arg-type]
        else:
            fp += 1
        rows.append(
            {
                "claim_id": edge.claim_id,
                "triple": list(triple) if triple is not None else None,
                "confidence": float(edge.confidence),
                "label": label,
                "duplicate": duplicate,
            }
        )
    tp = len(seen_true)
    return (
        {
            "tp": tp,
            "fp": fp,
            "fn": len(truth - seen_true),
            "predicted": len(graph.edges),
            "truth": len(truth),
        },
        rows,
    )


def _ranking_metrics(
    ranking: list[dict[str, Any]],
    node_truth: dict[str, str | None],
    oracle: dict[str, Any],
    k: int,
    bins: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    oracle_nodes = {node["id"]: node for node in oracle["nodes"]}
    targets = {
        truth_id: int(node["priority"])
        for truth_id, node in oracle_nodes.items()
        if bool(node["migration_target"])
    }
    score_fields = {
        "primary": "primary_rank_score",
        "weighted": "weighted_baseline_score",
        "rank_aggregation": "rank_aggregation_score",
        "calibrated": "calibrated_urgency_probability",
    }
    prediction_by_truth: dict[str, dict[str, float]] = {}
    noise_rows: list[tuple[str, dict[str, Any]]] = []
    for row in ranking:
        truth_id = node_truth.get(row["node_id"])
        if truth_id is None or truth_id not in targets:
            noise_rows.append((f"noise:{row['node_id']}", row))
            continue
        scores = prediction_by_truth.setdefault(truth_id, {})
        for label, field in score_fields.items():
            scores[label] = max(scores.get(label, 0.0), float(row[field]))

    identifiers = sorted(targets) + [identifier for identifier, _ in noise_rows]
    relevance = np.asarray([targets.get(identifier, 0) for identifier in identifiers], dtype=float)
    metrics: dict[str, Any] = {}
    ranking_rows: list[dict[str, Any]] = []
    for label in score_fields:
        predicted: list[float] = []
        for identifier in sorted(targets):
            predicted.append(prediction_by_truth.get(identifier, {}).get(label, 0.0))
        for _, row in noise_rows:
            predicted.append(float(row[score_fields[label]]))
        predicted_array = np.asarray(predicted, dtype=float)
        if len(identifiers) > 1 and np.max(relevance) > 0:
            for cutoff in (5, 10):
                metrics[f"ndcg_at_{cutoff}_{label}"] = float(
                    ndcg_score(
                        relevance.reshape(1, -1),
                        predicted_array.reshape(1, -1),
                        k=min(cutoff, len(identifiers)),
                    )
                )
            metrics[f"ndcg_{label}"] = metrics[
                f"ndcg_at_{min(10, max(5, int(k)))}_{label}"
            ] if int(k) in {5, 10} else float(
                ndcg_score(
                    relevance.reshape(1, -1),
                    predicted_array.reshape(1, -1),
                    k=min(k, len(identifiers)),
                )
            )
        else:
            metrics[f"ndcg_{label}"] = 0.0
            metrics[f"ndcg_at_5_{label}"] = 0.0
            metrics[f"ndcg_at_10_{label}"] = 0.0
        correlation = spearmanr(relevance, predicted_array).statistic
        metrics[f"spearman_{label}"] = (
            0.0 if correlation is None or math.isnan(float(correlation)) else float(correlation)
        )
        tau = kendalltau(relevance, predicted_array, variant="b").statistic
        metrics[f"kendall_tau_b_{label}"] = (
            0.0 if tau is None or math.isnan(float(tau)) else float(tau)
        )
        order = sorted(
            range(len(identifiers)),
            key=lambda index: (-predicted_array[index], identifiers[index]),
        )
        urgent = {index for index, value in enumerate(relevance) if value >= 2}
        selected = set(order[: min(k, len(order))])
        metrics[f"top{k}_urgent_recall_{label}"] = _safe_div(
            len(urgent & selected), len(urgent)
        )

    urgent_labels: list[int] = []
    calibrated_scores: list[float] = []
    for identifier in sorted(targets):
        urgent_labels.append(int(targets[identifier] >= 2))
        calibrated_scores.append(
            prediction_by_truth.get(identifier, {}).get("calibrated", 0.0)
        )
    for _, row in noise_rows:
        urgent_labels.append(0)
        calibrated_scores.append(float(row[score_fields["calibrated"]]))
    metrics["urgency_brier"] = _brier(urgent_labels, calibrated_scores)
    metrics["urgency_ece"] = _ece(urgent_labels, calibrated_scores, bins)
    for index, identifier in enumerate(identifiers):
        ranking_rows.append(
            {
                "truth_or_noise_id": identifier,
                "priority": int(relevance[index]),
                **{
                    f"score_{label}": (
                        prediction_by_truth.get(identifier, {}).get(label, 0.0)
                        if identifier in targets
                        else float(noise_rows[index - len(targets)][1][field])
                    )
                    for label, field in score_fields.items()
                },
            }
        )
    return metrics, ranking_rows


def _metrics_from_counts(prefix: str, counts: dict[str, int]) -> dict[str, float]:
    precision = _safe_div(counts["tp"], counts["tp"] + counts["fp"])
    recall = _safe_div(counts["tp"], counts["tp"] + counts["fn"])
    f1 = _safe_div(2.0 * precision * recall, precision + recall)
    return {
        f"{prefix}_precision": precision,
        f"{prefix}_recall": recall,
        f"{prefix}_f1": f1,
    }


def _brier(labels: list[int], probabilities: list[float]) -> float:
    if not labels:
        return 0.0
    y = np.asarray(labels, dtype=float)
    p = np.asarray(probabilities, dtype=float)
    return float(np.mean((p - y) ** 2))


def _ece(labels: list[int], probabilities: list[float], bins: int) -> float:
    if not labels:
        return 0.0
    y = np.asarray(labels, dtype=float)
    p = np.asarray(probabilities, dtype=float)
    boundaries = np.linspace(0.0, 1.0, max(1, bins) + 1)
    ece = 0.0
    for index in range(len(boundaries) - 1):
        lower, upper = boundaries[index], boundaries[index + 1]
        mask = (p >= lower) & (p < upper if index < len(boundaries) - 2 else p <= upper)
        if not np.any(mask):
            continue
        ece += float(np.mean(mask)) * abs(float(np.mean(y[mask])) - float(np.mean(p[mask])))
    return ece


def _safe_div(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0
