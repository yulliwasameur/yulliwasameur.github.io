"""Small serializable data model; no database or external service is required."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class EntityObservation:
    observation_id: str
    source: str
    local_key: str
    entity_type: str
    identifiers: dict[str, str]
    attributes: dict[str, Any]
    quality: float
    collected_at: str
    evidence: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["kind"] = "entity"
        return payload


@dataclass(frozen=True)
class ClaimObservation:
    observation_id: str
    source: str
    subject_observation_id: str
    predicate: str
    object_observation_id: str
    quality: float
    collected_at: str
    evidence: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["kind"] = "claim"
        return payload


@dataclass
class GraphNode:
    node_id: str
    entity_type: str
    member_observation_ids: list[str]
    attributes: dict[str, Any]
    confidence: float
    sources: list[str]
    attribute_provenance: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GraphEdge:
    claim_id: str
    subject: str
    predicate: str
    object: str
    evidence_ids: list[str]
    confidence: float
    method: str
    rule: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CandidateClaim:
    claim_id: str
    subject: str
    predicate: str
    object: str
    evidence_ids: list[str]
    method: str = "llm"
    rule: str | None = None


@dataclass
class GraphResult:
    method: str
    nodes: dict[str, GraphNode]
    edges: list[GraphEdge]
    rejected_claims: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "nodes": [self.nodes[key].to_dict() for key in sorted(self.nodes)],
            "edges": [edge.to_dict() for edge in self.edges],
            "rejected_claims": self.rejected_claims,
            "metadata": self.metadata,
        }


def graph_result_from_dict(payload: dict[str, Any]) -> GraphResult:
    """Rehydrate a serialized graph for deterministic candidate replay."""

    nodes = {
        item["node_id"]: GraphNode(**item) for item in payload.get("nodes", [])
    }
    edges = [GraphEdge(**item) for item in payload.get("edges", [])]
    return GraphResult(
        method=str(payload.get("method", "replayed")),
        nodes=nodes,
        edges=edges,
        rejected_claims=list(payload.get("rejected_claims", [])),
        metadata=dict(payload.get("metadata", {})),
    )
