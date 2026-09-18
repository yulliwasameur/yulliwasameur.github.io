"""Compatibility views over the canonical :mod:`cigma.evaluation` module."""

from __future__ import annotations

from typing import Any

from .evaluation import (
    _asset_inventory_counts,
    _b3_entity_resolution,
    _edge_counts,
    _metrics_from_counts,
    _ranking_metrics,
    map_graph_nodes_to_truth,
)
from .model import GraphResult


def node_truth_map(
    graph: GraphResult, oracle: dict[str, Any]
) -> dict[str, str | None]:
    return map_graph_nodes_to_truth(graph, oracle)[0]


def evaluate_nodes(graph: GraphResult, oracle: dict[str, Any]) -> dict[str, Any]:
    mapping, conflicts = map_graph_nodes_to_truth(graph, oracle)
    counts = _asset_inventory_counts(graph, mapping, oracle)
    public_stub = {
        "entities": [
            {"observation_id": observation_id}
            for observation_id in oracle["entity_observation_map"]
        ]
    }
    return {
        "method": graph.method,
        **_metrics_from_counts("asset", counts),
        **_b3_entity_resolution(graph, oracle, public_stub),
        "f1": _metrics_from_counts("asset", counts)["asset_f1"],
        "node_truth_conflicts": conflicts,
    }


def evaluate_edges(graph: GraphResult, oracle: dict[str, Any]) -> dict[str, Any]:
    mapping, _ = map_graph_nodes_to_truth(graph, oracle)
    counts, _ = _edge_counts(graph, mapping, oracle)
    metrics = _metrics_from_counts("edge", counts)
    return {
        "method": graph.method,
        **metrics,
        "precision": metrics["edge_precision"],
        "recall": metrics["edge_recall"],
        "f1": metrics["edge_f1"],
    }


def evaluate_ranking(
    graph: GraphResult,
    scores: list[dict[str, Any]],
    oracle: dict[str, Any],
    k: int,
) -> dict[str, Any]:
    mapping, _ = map_graph_nodes_to_truth(graph, oracle)
    metrics, _ = _ranking_metrics(scores, mapping, oracle, k, 5)
    return {
        "method": scores[0]["method"] if scores else graph.method,
        "ndcg": metrics["ndcg_primary"],
        **metrics,
    }


def evaluate_calibration(
    graph: GraphResult, oracle: dict[str, Any], bins: int
) -> dict[str, Any]:
    from .evaluation import _brier, _ece

    mapping, _ = map_graph_nodes_to_truth(graph, oracle)
    _, rows = _edge_counts(graph, mapping, oracle)
    labels = [int(row["label"]) for row in rows]
    probabilities = [float(row["confidence"]) for row in rows]
    return {
        "method": graph.method,
        "brier": _brier(labels, probabilities),
        "ece": _ece(labels, probabilities, bins),
        "claims_evaluated": len(rows),
    }
