"""Weight-free migration policy ranking with separate epistemic confidence."""

from __future__ import annotations

import math
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression

from .io import read_csv
from .model import GraphEdge, GraphResult


CANDIDATE_TYPES = {
    "service",
    "endpoint",
    "certificate",
    "software_component",
    "pipeline",
    "device",
}
IMPACT_FACTORS = (
    "quantum_vulnerability",
    "hndl_urgency",
    "criticality",
    "exposure",
    "blast_radius",
)
PRIMARY_RANKING_POLICY = (
    "bounded-policy-tier/intra-tier-pareto/lexicographic-v3"
)
ALGORITHM_QUANTUM_POLICY_VERSION = "cigma-qv-policy-v1"
ALGORITHM_QUANTUM_VULNERABILITY_V1 = {
    "rsa-2048": 1.0,
    "ecdsa-p256": 1.0,
    "aes-256-gcm": 0.15,
}


def fit_independent_calibrator(
    panel_path: str | Path, *, seed: int
) -> dict[str, Any]:
    """Fit Platt scaling on a separate, versioned synthetic policy panel."""

    rows = read_csv(panel_path)
    scores = np.asarray([[float(row["policy_score"])] for row in rows], dtype=float)
    labels = np.asarray([int(row["urgent"]) for row in rows], dtype=int)
    if len(set(labels.tolist())) != 2:
        raise ValueError("calibration panel must contain both classes")
    model = LogisticRegression(
        C=1_000_000.0,
        solver="lbfgs",
        random_state=seed,
        max_iter=10_000,
    )
    model.fit(scores, labels)
    probabilities = model.predict_proba(scores)[:, 1]
    brier = float(np.mean((probabilities - labels) ** 2))
    return {
        "intercept": float(model.intercept_[0]),
        "slope": float(model.coef_[0][0]),
        "panel_cases": int(len(rows)),
        "panel_sha256": _file_digest(panel_path),
        "panel_brier": brier,
        "training_scope": "independent synthetic policy panel; not benchmark oracle or expert data",
    }


def score_graph(
    graph: GraphResult,
    config: dict[str, Any],
    *,
    calibrator: dict[str, Any] | None = None,
    label: str | None = None,
    weights_override: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Score assets without consulting the evaluator oracle.

    The primary order is policy tier -> Pareto front -> deterministic
    lexicographic factors. A legacy weighted score and a calibrated probability
    are exported as explicit alternatives, never as epistemic confidence.
    """

    if calibrator is None:
        calibrator = fit_independent_calibrator(
            Path(__file__).resolve().parents[2] / "fixtures" / "calibration_panel.csv",
            seed=int(config.get("seed", 586)),
        )
    declared_policy = str(
        config.get("scoring", {}).get("primary_policy", PRIMARY_RANKING_POLICY)
    )
    if declared_policy != PRIMARY_RANKING_POLICY:
        raise ValueError(
            "scoring.primary_policy does not match the implemented ranking contract: "
            f"{PRIMARY_RANKING_POLICY}"
        )
    outgoing, incoming = _edge_indexes(graph.edges)
    service_dependents = _service_dependents(graph, incoming)
    horizon = float(config.get("scoring", {}).get("policy_horizon_years", 10.0))
    weights = dict(
        weights_override
        if weights_override is not None
        else config.get("scoring", {}).get("weights", {})
    )
    verification_threshold = float(
        config.get("confidence", {}).get(
            "verification_threshold",
            config.get("confidence", {}).get("action_threshold", 0.65),
        )
    )
    rows: list[dict[str, Any]] = []
    for node_id, node in sorted(graph.nodes.items()):
        if node.entity_type not in CANDIDATE_TYPES:
            continue
        contexts = _service_contexts(node_id, graph, outgoing, incoming)
        algorithm_edges = _algorithm_edges(
            node_id, contexts, graph, outgoing, incoming
        )
        algorithms = [graph.nodes[edge.object] for edge in algorithm_edges]
        qv, qv_known = _algorithm_quantum_vulnerability(algorithms)
        attribute_nodes = [node] + [graph.nodes[item] for item in sorted(contexts)]
        criticality_values = [
            _numeric(item.attributes["criticality"], 0.0)
            for item in attribute_nodes
            if "criticality" in item.attributes
        ]
        exposure_values = [
            _numeric(item.attributes["exposure"], 0.0)
            for item in attribute_nodes
            if "exposure" in item.attributes
        ]
        migration_values = [
            _numeric(item.attributes["migration_time_years"], 1.0)
            for item in attribute_nodes
            if "migration_time_years" in item.attributes
        ]
        agility_values = [
            _numeric(item.attributes["agility"], 0.5)
            for item in attribute_nodes
            if "agility" in item.attributes
        ]
        criticality = max(criticality_values or [0.0])
        exposure = max(exposure_values or [0.0])
        migration_time = max(migration_values or [1.0])
        agility = min(agility_values or [0.5])
        data_lifetime, data_lifetime_known = _data_lifetime(
            node_id, contexts, graph, outgoing, attribute_nodes
        )
        hndl = min(1.0, (data_lifetime + migration_time) / max(horizon, 0.001)) * qv
        blast = max(
            [service_dependents.get(service_id, 0.0) for service_id in contexts]
            or [service_dependents.get(node_id, 0.0)]
        )
        factor_values = {
            "quantum_vulnerability": _clip(qv),
            "hndl_urgency": _clip(hndl),
            "criticality": _clip(criticality),
            "exposure": _clip(exposure),
            "blast_radius": _clip(blast),
            "agility_penalty": _clip(1.0 - agility),
        }
        factor_known = {
            "quantum_vulnerability": qv_known,
            "hndl_urgency": qv_known
            and data_lifetime_known
            and bool(migration_values),
            "criticality": bool(criticality_values),
            "exposure": bool(exposure_values),
            "blast_radius": True,
        }
        lower_factors = {
            key: (factor_values[key] if factor_known[key] else 0.0)
            for key in IMPACT_FACTORS
        }
        upper_factors = {
            key: (factor_values[key] if factor_known[key] else 1.0)
            for key in IMPACT_FACTORS
        }
        policy_tier_lower = _policy_tier(lower_factors)
        policy_tier_upper = _policy_tier(upper_factors)
        missing_factors = sorted(key for key, known in factor_known.items() if not known)
        weighted_score = _weighted_baseline(factor_values, weights)
        epistemic_confidence = _epistemic_confidence(node.confidence, algorithm_edges)
        calibrated_probability = _sigmoid(
            float(calibrator["intercept"])
            + float(calibrator["slope"]) * weighted_score
        )
        row: dict[str, Any] = {
            "method": label or graph.method,
            "node_id": node_id,
            "entity_type": node.entity_type,
            **{key: round(value, 10) for key, value in factor_values.items()},
            "data_lifetime_years": round(data_lifetime, 10),
            "data_lifetime_known": data_lifetime_known,
            "migration_time_years": round(migration_time, 10),
            "migration_time_known": bool(migration_values),
            "feasibility_agility": round(agility, 10),
            "feasibility_known": bool(agility_values),
            "policy_tier": policy_tier_lower,
            "policy_tier_lower_bound": policy_tier_lower,
            "policy_tier_upper_bound": policy_tier_upper,
            "policy_tier_confirmed": policy_tier_lower == policy_tier_upper,
            "missing_impact_factors": missing_factors,
            "impact_assessment_complete": not missing_factors,
            **{
                f"impact_lower_{key}": round(value, 10)
                for key, value in lower_factors.items()
            },
            **{
                f"impact_upper_{key}": round(value, 10)
                for key, value in upper_factors.items()
            },
            "weighted_baseline_score": round(weighted_score, 10),
            "calibrated_urgency_probability": round(calibrated_probability, 10),
            "calibrated_probability_valid": not missing_factors,
            "epistemic_confidence": round(epistemic_confidence, 10),
            "verification_required": bool(
                policy_tier_upper >= 2
                and (
                    policy_tier_lower != policy_tier_upper
                    or epistemic_confidence < verification_threshold
                )
            ),
            "service_contexts": sorted(contexts),
            "algorithm_nodes": sorted({edge.object for edge in algorithm_edges}),
            "evidence_ids": sorted(
                {item for edge in algorithm_edges for item in edge.evidence_ids}
            ),
        }
        rows.append(row)

    fronts = _pareto_fronts(rows)
    rank_percentiles = _rank_aggregation(rows)
    for row in rows:
        row["pareto_front"] = fronts[row["node_id"]]
        row["rank_aggregation_score"] = round(rank_percentiles[row["node_id"]], 10)
    ordered = sorted(rows, key=_primary_sort_key)
    denominator = max(1, len(ordered) - 1)
    for index, row in enumerate(ordered, start=1):
        row["primary_rank"] = index
        row["primary_rank_score"] = round(1.0 - (index - 1) / denominator, 10)
        # Backward-compatible name consumed by the legacy metric module. It is
        # the weight-free primary rank score, not epistemic confidence.
        row["urgency"] = row["primary_rank_score"]
        row["ranking_policy"] = PRIMARY_RANKING_POLICY
    return ordered


def _policy_tier(factors: dict[str, float]) -> int:
    """Explicit, weight-free migration decision policy."""

    qv = factors["quantum_vulnerability"]
    hndl = factors["hndl_urgency"]
    criticality = factors["criticality"]
    exposure = factors["exposure"]
    blast = factors["blast_radius"]
    if qv >= 0.80 and (hndl >= 0.80 or criticality >= 0.90):
        return 3
    if qv >= 0.80 and (
        hndl >= 0.50 or criticality >= 0.70 or exposure >= 0.50 or blast >= 0.50
    ):
        return 2
    if qv >= 0.50 or (qv >= 0.20 and criticality >= 0.80):
        return 1
    return 0


def _weighted_baseline(
    factors: dict[str, float], weights: dict[str, float]
) -> float:
    supported = {
        "quantum_vulnerability": factors["quantum_vulnerability"],
        "hndl_urgency": factors["hndl_urgency"],
        "exposure": factors["exposure"],
        "criticality": factors["criticality"],
        "blast_radius": factors["blast_radius"],
        "agility_penalty": factors["agility_penalty"],
    }
    denominator = sum(max(0.0, float(weights.get(key, 0.0))) for key in supported)
    if denominator <= 0:
        return 0.0
    return sum(
        max(0.0, float(weights.get(key, 0.0))) * value
        for key, value in supported.items()
    ) / denominator


def _pareto_fronts(rows: list[dict[str, Any]]) -> dict[str, int]:
    fronts: dict[str, int] = {}
    # Policy bounds are the first two primary decisions. Pareto dominance is
    # therefore meaningful only among assets with the same conservative upper
    # and observed lower tier; an asset in another tier interval must not alter
    # a within-tier front number.
    tier_groups: dict[tuple[int, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        tier_key = (
            int(row["policy_tier_upper_bound"]),
            int(row["policy_tier_lower_bound"]),
        )
        tier_groups[tier_key][row["node_id"]] = row

    for tier_key in sorted(tier_groups, reverse=True):
        remaining = dict(tier_groups[tier_key])
        front = 1
        while remaining:
            non_dominated: list[str] = []
            for node_id, candidate in sorted(remaining.items()):
                dominated = any(
                    _dominates(other, candidate)
                    for other_id, other in remaining.items()
                    if other_id != node_id
                )
                if not dominated:
                    non_dominated.append(node_id)
            if not non_dominated:
                raise AssertionError("Pareto sorting failed to find a front")
            for node_id in non_dominated:
                fronts[node_id] = front
                del remaining[node_id]
            front += 1
    return fronts


def _dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    values = [
        (float(left[f"impact_upper_{key}"]), float(right[f"impact_upper_{key}"]))
        for key in IMPACT_FACTORS
    ]
    return all(a >= b for a, b in values) and any(a > b for a, b in values)


def _rank_aggregation(rows: list[dict[str, Any]]) -> dict[str, float]:
    if not rows:
        return {}
    scores = {row["node_id"]: 0.0 for row in rows}
    denominator = max(1, len(rows) - 1)
    for factor in IMPACT_FACTORS:
        ordered = sorted(
            rows,
            key=lambda row: (
                float(row[f"impact_upper_{factor}"]),
                row["node_id"],
            ),
        )
        for index, row in enumerate(ordered):
            scores[row["node_id"]] += index / denominator
    return {node_id: value / len(IMPACT_FACTORS) for node_id, value in scores.items()}


def _primary_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        -int(row["policy_tier_upper_bound"]),
        -int(row["policy_tier_lower_bound"]),
        int(row["pareto_front"]),
        -float(row["impact_upper_quantum_vulnerability"]),
        -float(row["impact_upper_hndl_urgency"]),
        -float(row["impact_upper_criticality"]),
        -float(row["impact_upper_blast_radius"]),
        -float(row["impact_upper_exposure"]),
        str(row["node_id"]),
    )


def _edge_indexes(
    edges: list[GraphEdge],
) -> tuple[dict[tuple[str, str], list[GraphEdge]], dict[tuple[str, str], list[GraphEdge]]]:
    outgoing: dict[tuple[str, str], list[GraphEdge]] = defaultdict(list)
    incoming: dict[tuple[str, str], list[GraphEdge]] = defaultdict(list)
    for edge in edges:
        outgoing[(edge.subject, edge.predicate)].append(edge)
        incoming[(edge.object, edge.predicate)].append(edge)
    return outgoing, incoming


def _service_contexts(
    node_id: str,
    graph: GraphResult,
    outgoing: dict[tuple[str, str], list[GraphEdge]],
    incoming: dict[tuple[str, str], list[GraphEdge]],
) -> set[str]:
    node_type = graph.nodes[node_id].entity_type
    if node_type == "service":
        return {node_id}
    contexts: set[str] = set()
    if node_type == "endpoint":
        contexts.update(edge.subject for edge in incoming.get((node_id, "HOSTS"), []))
    elif node_type == "certificate":
        certificates = {node_id}
        certificates.update(
            edge.subject for edge in incoming.get((node_id, "ISSUED_BY"), [])
        )
        endpoints = {
            edge.subject
            for certificate in certificates
            for edge in incoming.get((certificate, "PRESENTS"), [])
        }
        contexts.update(
            edge.subject
            for endpoint in endpoints
            for edge in incoming.get((endpoint, "HOSTS"), [])
        )
    elif node_type == "software_component":
        contexts.update(
            edge.subject
            for edge in incoming.get((node_id, "USES"), [])
            if graph.nodes[edge.subject].entity_type == "service"
        )
    elif node_type == "pipeline":
        contexts.update(edge.object for edge in outgoing.get((node_id, "DEPLOYS"), []))
    elif node_type == "device":
        contexts.update(
            edge.subject
            for edge in incoming.get((node_id, "DEPENDS_ON"), [])
            if graph.nodes[edge.subject].entity_type == "service"
        )
    return contexts


def _algorithm_edges(
    node_id: str,
    contexts: set[str],
    graph: GraphResult,
    outgoing: dict[tuple[str, str], list[GraphEdge]],
    incoming: dict[tuple[str, str], list[GraphEdge]],
) -> list[GraphEdge]:
    candidates: list[GraphEdge] = []
    for subject in {node_id} | contexts:
        candidates.extend(
            edge
            for edge in outgoing.get((subject, "USES"), [])
            if graph.nodes[edge.object].entity_type == "algorithm"
        )
    if graph.nodes[node_id].entity_type == "endpoint":
        for present in outgoing.get((node_id, "PRESENTS"), []):
            candidates.extend(
                edge
                for edge in outgoing.get((present.object, "USES"), [])
                if graph.nodes[edge.object].entity_type == "algorithm"
            )
    unique = {edge.claim_id: edge for edge in candidates}
    return [unique[key] for key in sorted(unique)]


def _algorithm_quantum_vulnerability(algorithms: list[Any]) -> tuple[float, bool]:
    """Apply the versioned policy to normalized algorithm identifiers.

    Source-provided risk attributes are deliberately ignored. If any referenced
    algorithm lacks a known normalized identifier, the aggregate is incomplete;
    the known mappings still form its observed lower bound and the generic
    missing-factor logic supplies the conservative upper bound.
    """

    values: list[float] = []
    complete = bool(algorithms)
    for algorithm in algorithms:
        identifiers = algorithm.attributes.get("identifiers", {})
        if not isinstance(identifiers, dict):
            complete = False
            continue
        raw_ids = identifiers.get("algorithm_id", [])
        if isinstance(raw_ids, str):
            algorithm_ids = [raw_ids]
        elif isinstance(raw_ids, (list, tuple, set)):
            algorithm_ids = [str(value) for value in raw_ids]
        else:
            algorithm_ids = []
        normalized_ids = sorted({value for value in algorithm_ids if value})
        if not normalized_ids:
            complete = False
            continue
        mapped = [
            ALGORITHM_QUANTUM_VULNERABILITY_V1[value]
            for value in normalized_ids
            if value in ALGORITHM_QUANTUM_VULNERABILITY_V1
        ]
        values.extend(mapped)
        if len(mapped) != len(normalized_ids):
            complete = False
    return max(values or [0.0]), complete


def _data_lifetime(
    node_id: str,
    contexts: set[str],
    graph: GraphResult,
    outgoing: dict[tuple[str, str], list[GraphEdge]],
    attribute_nodes: list[Any],
) -> tuple[float, bool]:
    values = [
        _numeric(item.attributes["data_lifetime_years"], 0.0)
        for item in attribute_nodes
        if "data_lifetime_years" in item.attributes
    ]
    for subject in {node_id} | contexts:
        for edge in outgoing.get((subject, "PROCESSES"), []):
            if "retention_years" in graph.nodes[edge.object].attributes:
                values.append(
                    _numeric(
                        graph.nodes[edge.object].attributes["retention_years"], 0.0
                    )
                )
    return max(values or [0.0]), bool(values)


def _service_dependents(
    graph: GraphResult,
    incoming: dict[tuple[str, str], list[GraphEdge]],
) -> dict[str, float]:
    services = sorted(
        node_id for node_id, node in graph.nodes.items() if node.entity_type == "service"
    )
    counts: dict[str, int] = {}
    for service in services:
        seen: set[str] = set()
        queue: deque[str] = deque([service])
        while queue:
            current = queue.popleft()
            for edge in incoming.get((current, "DEPENDS_ON"), []):
                if graph.nodes[edge.subject].entity_type != "service":
                    continue
                if edge.subject not in seen:
                    seen.add(edge.subject)
                    queue.append(edge.subject)
        counts[service] = len(seen)
    denominator = max(1, len(services) - 1)
    return {service: count / denominator for service, count in counts.items()}


def _epistemic_confidence(node_confidence: float, edges: list[GraphEdge]) -> float:
    if not edges:
        return _clip(node_confidence * 0.5)
    return _clip(min([node_confidence] + [edge.confidence for edge in edges]))


def _numeric(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _clip(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _file_digest(path: str | Path) -> str:
    import hashlib

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
