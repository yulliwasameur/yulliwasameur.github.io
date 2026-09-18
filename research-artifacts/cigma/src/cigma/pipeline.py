"""Offline CIGMA ingest, correlate, validate, and graph pipeline."""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any

from .model import GraphEdge, GraphResult
from .normalize import normalize_public
from .ontology import ALLOWED_PATH_RULES
from .resolution import resolve_entities
from .validation import (
    ensure_oracle_isolation,
    relation_is_valid,
    validate_public_observations,
    validate_source_reliability,
)


@dataclass(frozen=True)
class MethodSpec:
    name: str
    sources: tuple[str, ...] | None
    resolution: str
    min_entity_quality: float
    min_claim_quality: float
    derive_paths: bool
    use_source_reliability: bool = True


METHODS: dict[str, MethodSpec] = {
    "tls_inventory": MethodSpec(
        "tls_inventory", ("tls",), "strong", 0.0, 0.0, False
    ),
    "cbom_inventory": MethodSpec(
        "cbom_inventory", ("code",), "strong", 0.0, 0.0, False
    ),
    "source_union": MethodSpec(
        "source_union", None, "none", 0.0, 0.0, False
    ),
    "exact_direct": MethodSpec(
        "exact_direct", None, "strong", 0.0, 0.0, False
    ),
    "cigma": MethodSpec(
        "cigma", None, "strong_alias", 0.40, 0.40, True
    ),
    "cigma_no_alias": MethodSpec(
        "cigma_no_alias", None, "strong", 0.40, 0.40, True
    ),
    "cigma_no_paths": MethodSpec(
        "cigma_no_paths", None, "strong_alias", 0.40, 0.40, False
    ),
    "cigma_no_quality_gate": MethodSpec(
        "cigma_no_quality_gate", None, "strong_alias", 0.0, 0.0, True
    ),
    "cigma_uniform_reliability": MethodSpec(
        "cigma_uniform_reliability",
        None,
        "strong_alias",
        0.40,
        0.40,
        True,
        False,
    ),
}


def source_dropout_spec(source: str) -> MethodSpec:
    return MethodSpec(
        name=f"cigma_without_{source}",
        sources=tuple(sorted(set(_KNOWN_SOURCES) - {source})),
        resolution="strong_alias",
        min_entity_quality=0.40,
        min_claim_quality=0.40,
        derive_paths=True,
    )


_KNOWN_SOURCES = ("tls", "pki", "code", "cicd", "cmdb", "ot")


def run_pipeline(
    public: dict[str, Any],
    config: dict[str, Any],
    method: str | MethodSpec = "cigma",
) -> GraphResult:
    """Build a graph without access to evaluator truth or external services."""

    spec = METHODS[method] if isinstance(method, str) else method
    reliability = validate_source_reliability(config)
    validate_public_observations(public)
    normalized = normalize_public(public)
    ensure_oracle_isolation(normalized)

    entities = normalized["entities"]
    claims = normalized["claims"]
    if spec.sources is not None:
        allowed = set(spec.sources)
        entities = [item for item in entities if item["source"] in allowed]
        retained_ids = {item["observation_id"] for item in entities}
        claims = [
            item
            for item in claims
            if item["source"] in allowed
            and item["subject_observation_id"] in retained_ids
            and item["object_observation_id"] in retained_ids
        ]

    if not spec.use_source_reliability:
        reliability = {source: 1.0 for source in _KNOWN_SOURCES}
    resolution = resolve_entities(
        entities,
        mode=spec.resolution,
        min_quality=spec.min_entity_quality,
        source_reliability=reliability,
    )
    graph = GraphResult(
        method=spec.name,
        nodes=resolution.nodes,
        edges=[],
        rejected_claims=list(resolution.quarantined),
        metadata={
            "method_spec": asdict(spec),
            "resolution_links": resolution.links,
            "normalization_profile": normalized["metadata"]["normalization_profile"],
            "oracle_access": False,
        },
    )
    direct_groups: dict[tuple[str, str, str], list[GraphEdge]] = defaultdict(list)
    for claim in sorted(claims, key=lambda item: item["observation_id"]):
        rejection = _validate_claim(
            claim,
            resolution.observation_to_node,
            graph,
            spec.min_claim_quality,
        )
        if rejection is not None:
            graph.rejected_claims.append(rejection)
            continue
        subject = resolution.observation_to_node[claim["subject_observation_id"]]
        obj = resolution.observation_to_node[claim["object_observation_id"]]
        source_probability = float(reliability.get(claim["source"], 0.5))
        confidence = max(
            0.0,
            min(
                1.0,
                source_probability
                * float(claim["quality"])
                * math.sqrt(
                    graph.nodes[subject].confidence * graph.nodes[obj].confidence
                ),
            ),
        )
        edge = GraphEdge(
            claim_id=claim["observation_id"],
            subject=subject,
            predicate=claim["predicate"],
            object=obj,
            evidence_ids=[claim["observation_id"]],
            confidence=round(confidence, 10),
            method="direct_observation",
        )
        direct_groups[(subject, claim["predicate"], obj)].append(edge)

    graph.edges = [
        _combine_direct_edges(key, edges)
        for key, edges in sorted(direct_groups.items())
    ]
    if spec.derive_paths:
        graph.edges.extend(_derive_allowed_paths(graph, config))
    graph.edges = sorted(
        _deduplicate_edges(graph.edges),
        key=lambda edge: (edge.subject, edge.predicate, edge.object, edge.claim_id),
    )
    graph.rejected_claims = sorted(
        graph.rejected_claims,
        key=lambda row: (str(row.get("observation_id", "")), str(row.get("reason", ""))),
    )
    _assert_provenance_invariant(graph, normalized)
    graph.metadata["counts"] = {
        "input_entities": len(entities),
        "input_claims": len(claims),
        "graph_nodes": len(graph.nodes),
        "graph_edges": len(graph.edges),
        "rejected": len(graph.rejected_claims),
    }
    return graph


def _validate_claim(
    claim: dict[str, Any],
    observation_to_node: dict[str, str],
    graph: GraphResult,
    min_quality: float,
) -> dict[str, Any] | None:
    observation_id = claim["observation_id"]
    if float(claim["quality"]) < min_quality:
        return {
            "observation_id": observation_id,
            "reason": "claim_quality_below_threshold",
            "quality": float(claim["quality"]),
        }
    subject = observation_to_node.get(claim["subject_observation_id"])
    obj = observation_to_node.get(claim["object_observation_id"])
    if subject is None or obj is None:
        return {"observation_id": observation_id, "reason": "quarantined_endpoint"}
    if subject == obj:
        return {"observation_id": observation_id, "reason": "self_loop"}
    if not relation_is_valid(
        claim["predicate"],
        graph.nodes[subject].entity_type,
        graph.nodes[obj].entity_type,
    ):
        return {"observation_id": observation_id, "reason": "ontology_signature"}
    return None


def _combine_direct_edges(
    key: tuple[str, str, str], edges: list[GraphEdge]
) -> GraphEdge:
    subject, predicate, obj = key
    evidence_ids = sorted({item for edge in edges for item in edge.evidence_ids})
    confidence = 1.0 - math.prod(1.0 - edge.confidence for edge in edges)
    identifier = hashlib.sha256(
        f"direct|{subject}|{predicate}|{obj}|{'|'.join(evidence_ids)}".encode("utf-8")
    ).hexdigest()[:16]
    return GraphEdge(
        claim_id=f"edge:direct:{identifier}",
        subject=subject,
        predicate=predicate,
        object=obj,
        evidence_ids=evidence_ids,
        confidence=round(confidence, 10),
        method="direct_observation",
    )


def _derive_allowed_paths(
    graph: GraphResult, config: dict[str, Any]
) -> list[GraphEdge]:
    path_penalty = float(config.get("confidence", {}).get("path_penalty", 0.92))
    by_subject_predicate: dict[tuple[str, str], list[GraphEdge]] = defaultdict(list)
    for edge in graph.edges:
        by_subject_predicate[(edge.subject, edge.predicate)].append(edge)
    derived: list[GraphEdge] = []
    for rule, predicates in sorted(ALLOWED_PATH_RULES.items()):
        paths: list[list[GraphEdge]] = [[]]
        starts = sorted(graph.nodes)
        paths = []
        for start in starts:
            paths.extend(
                _walk_predicate_path(start, predicates, by_subject_predicate, [])
            )
        for path in paths:
            subject = path[0].subject
            obj = path[-1].object
            predicate = "USES"
            if not relation_is_valid(
                predicate,
                graph.nodes[subject].entity_type,
                graph.nodes[obj].entity_type,
            ):
                continue
            evidence_ids = sorted(
                {item for edge in path for item in edge.evidence_ids}
            )
            confidence = min(edge.confidence for edge in path) * (
                path_penalty ** max(1, len(path) - 1)
            )
            identifier = hashlib.sha256(
                f"{rule}|{subject}|{predicate}|{obj}|{'|'.join(evidence_ids)}".encode(
                    "utf-8"
                )
            ).hexdigest()[:16]
            derived.append(
                GraphEdge(
                    claim_id=f"edge:derived:{identifier}",
                    subject=subject,
                    predicate=predicate,
                    object=obj,
                    evidence_ids=evidence_ids,
                    confidence=round(confidence, 10),
                    method="deterministic_path_rule",
                    rule=rule,
                )
            )
    return derived


def _walk_predicate_path(
    current: str,
    predicates: tuple[str, ...],
    index: dict[tuple[str, str], list[GraphEdge]],
    prefix: list[GraphEdge],
) -> list[list[GraphEdge]]:
    if not predicates:
        return [prefix]
    completed: list[list[GraphEdge]] = []
    for edge in sorted(
        index.get((current, predicates[0]), []),
        key=lambda item: (item.object, item.claim_id),
    ):
        if any(previous.subject == edge.object for previous in prefix):
            continue
        completed.extend(
            _walk_predicate_path(
                edge.object, predicates[1:], index, prefix + [edge]
            )
        )
    return completed


def _deduplicate_edges(edges: list[GraphEdge]) -> list[GraphEdge]:
    groups: dict[tuple[str, str, str], list[GraphEdge]] = defaultdict(list)
    for edge in edges:
        groups[(edge.subject, edge.predicate, edge.object)].append(edge)
    result: list[GraphEdge] = []
    for key, candidates in sorted(groups.items()):
        direct = [item for item in candidates if item.method == "direct_observation"]
        if direct:
            result.append(_combine_direct_edges(key, direct))
            continue
        winner = sorted(
            candidates,
            key=lambda item: (-item.confidence, item.rule or "", item.claim_id),
        )[0]
        evidence_ids = sorted(
            {item for candidate in candidates for item in candidate.evidence_ids}
        )
        winner.evidence_ids = evidence_ids
        result.append(winner)
    return result


def _assert_provenance_invariant(
    graph: GraphResult, normalized: dict[str, Any]
) -> None:
    entity_ids = {item["observation_id"] for item in normalized["entities"]}
    claim_ids = {item["observation_id"] for item in normalized["claims"]}
    for node in graph.nodes.values():
        if not node.member_observation_ids or not set(node.member_observation_ids) <= entity_ids:
            raise AssertionError(f"node provenance invariant failed: {node.node_id}")
        for evidence_ids in node.attribute_provenance.values():
            if not evidence_ids or not set(evidence_ids) <= entity_ids:
                raise AssertionError(
                    f"attribute provenance invariant failed: {node.node_id}"
                )
    for edge in graph.edges:
        if not edge.evidence_ids or not set(edge.evidence_ids) <= claim_ids:
            raise AssertionError(f"edge provenance invariant failed: {edge.claim_id}")
