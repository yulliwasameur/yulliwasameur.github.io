"""Conservative, explainable entity resolution for CIGMA observations."""

from __future__ import annotations

import hashlib
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

from .model import GraphNode
from .ontology import ALIAS_IDENTIFIER_KEYS, STRONG_IDENTIFIER_KEYS


@dataclass(frozen=True)
class ResolutionResult:
    nodes: dict[str, GraphNode]
    observation_to_node: dict[str, str]
    links: list[dict[str, str]]
    quarantined: list[dict[str, Any]]


class UnionFind:
    def __init__(self, values: Iterable[str]) -> None:
        self.parent = {value: value for value in values}

    def find(self, value: str) -> str:
        root = value
        while self.parent[root] != root:
            root = self.parent[root]
        while value != root:
            parent = self.parent[value]
            self.parent[value] = root
            value = parent
        return root

    def union(self, left: str, right: str) -> bool:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return False
        winner, loser = sorted((left_root, right_root))
        self.parent[loser] = winner
        return True


def resolve_entities(
    entities: list[dict[str, Any]],
    *,
    mode: str,
    min_quality: float,
    source_reliability: dict[str, float],
) -> ResolutionResult:
    """Cluster records using strong identifiers, then non-conflicting aliases.

    ``mode`` is one of ``none``, ``strong``, or ``strong_alias``. Alias links
    never override conflicting strong identifiers, and every accepted link is
    exported with its rule for auditability.
    """

    if mode not in {"none", "strong", "strong_alias"}:
        raise ValueError(f"unknown resolution mode: {mode}")
    retained = [item for item in entities if float(item["quality"]) >= min_quality]
    quarantined = [
        {
            "observation_id": item["observation_id"],
            "reason": "entity_quality_below_threshold",
            "quality": float(item["quality"]),
        }
        for item in entities
        if float(item["quality"]) < min_quality
    ]
    by_id = {item["observation_id"]: item for item in retained}
    union = UnionFind(by_id)
    links: list[dict[str, str]] = []

    if mode in {"strong", "strong_alias"}:
        _link_by_identifiers(
            by_id,
            union,
            STRONG_IDENTIFIER_KEYS,
            "strong_identifier",
            links,
            require_compatible=False,
        )
    if mode == "strong_alias":
        _link_by_identifiers(
            by_id,
            union,
            ALIAS_IDENTIFIER_KEYS,
            "alias_identifier",
            links,
            require_compatible=True,
        )

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for observation_id, item in by_id.items():
        groups[union.find(observation_id)].append(item)

    nodes: dict[str, GraphNode] = {}
    observation_to_node: dict[str, str] = {}
    for members in sorted(groups.values(), key=lambda values: min(x["observation_id"] for x in values)):
        # In the no-resolution baseline every observation is deliberately a
        # separate predicted cluster.  Strong identifiers must therefore not
        # be used as node-ID anchors: doing so made distinct observations
        # collide in ``nodes`` and silently turned SourceUnion into a partial
        # ExactDirect baseline.
        node = _make_node(
            members,
            source_reliability,
            force_observation_anchor=(mode == "none"),
        )
        nodes[node.node_id] = node
        for observation_id in node.member_observation_ids:
            observation_to_node[observation_id] = node.node_id

    return ResolutionResult(
        nodes=nodes,
        observation_to_node=observation_to_node,
        links=sorted(
            links,
            key=lambda row: (row["left"], row["right"], row["rule"], row["key"]),
        ),
        quarantined=sorted(quarantined, key=lambda row: row["observation_id"]),
    )


def _link_by_identifiers(
    by_id: dict[str, dict[str, Any]],
    union: UnionFind,
    keys: set[str],
    rule: str,
    links: list[dict[str, str]],
    *,
    require_compatible: bool,
) -> None:
    index: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for observation_id, item in sorted(by_id.items()):
        for key in sorted(keys & set(item["identifiers"])):
            value = str(item["identifiers"][key])
            index[(item["entity_type"], key, value)].append(observation_id)
    for (_, key, value), observation_ids in sorted(index.items()):
        anchor = observation_ids[0]
        for candidate in observation_ids[1:]:
            if require_compatible and not _strongly_compatible(
                _cluster_items(anchor, by_id, union),
                _cluster_items(candidate, by_id, union),
            ):
                continue
            left, right = sorted((anchor, candidate))
            if union.union(left, right):
                links.append(
                    {
                        "left": left,
                        "right": right,
                        "rule": rule,
                        "key": key,
                        "value": value,
                    }
                )


def _cluster_items(
    observation_id: str,
    by_id: dict[str, dict[str, Any]],
    union: UnionFind,
) -> list[dict[str, Any]]:
    root = union.find(observation_id)
    return [item for key, item in by_id.items() if union.find(key) == root]


def _strongly_compatible(
    left_items: list[dict[str, Any]], right_items: list[dict[str, Any]]
) -> bool:
    for key in sorted(STRONG_IDENTIFIER_KEYS):
        left_values = {
            item["identifiers"][key]
            for item in left_items
            if key in item["identifiers"]
        }
        right_values = {
            item["identifiers"][key]
            for item in right_items
            if key in item["identifiers"]
        }
        if left_values and right_values and left_values.isdisjoint(right_values):
            return False
    return True


def _make_node(
    members: list[dict[str, Any]],
    source_reliability: dict[str, float],
    *,
    force_observation_anchor: bool = False,
) -> GraphNode:
    members = sorted(members, key=lambda item: item["observation_id"])
    entity_types = {item["entity_type"] for item in members}
    if len(entity_types) != 1:
        raise ValueError(f"mixed entity types in cluster: {sorted(entity_types)}")
    entity_type = next(iter(entity_types))
    member_ids = [item["observation_id"] for item in members]
    identifier_anchor = (
        f"observation_id={member_ids[0]}"
        if force_observation_anchor
        else _anchor_identifier(members)
    )
    digest_input = f"{entity_type}|{identifier_anchor or '|'.join(member_ids)}"
    digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()[:16]
    node_id = f"node:{entity_type}:{digest}"

    attributes, provenance = _aggregate_attributes(members, source_reliability)
    identifier_values: dict[str, list[str]] = defaultdict(list)
    for item in members:
        for key, value in item["identifiers"].items():
            identifier_values[key].append(str(value))
    attributes["identifiers"] = {
        key: sorted(set(values)) for key, values in sorted(identifier_values.items())
    }
    provenance["identifiers"] = member_ids

    probabilities = [
        max(
            0.0,
            min(
                1.0,
                float(item["quality"])
                * float(source_reliability.get(item["source"], 0.5)),
            ),
        )
        for item in members
    ]
    confidence = 1.0 - math.prod(1.0 - probability for probability in probabilities)
    return GraphNode(
        node_id=node_id,
        entity_type=entity_type,
        member_observation_ids=member_ids,
        attributes=attributes,
        confidence=round(confidence, 10),
        sources=sorted({item["source"] for item in members}),
        attribute_provenance=provenance,
    )


def _anchor_identifier(members: list[dict[str, Any]]) -> str | None:
    candidates: list[str] = []
    for item in members:
        for key in sorted(STRONG_IDENTIFIER_KEYS & set(item["identifiers"])):
            candidates.append(f"{key}={item['identifiers'][key]}")
    return sorted(candidates)[0] if candidates else None


def _aggregate_attributes(
    members: list[dict[str, Any]], source_reliability: dict[str, float]
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    values: dict[str, list[tuple[Any, float, str]]] = defaultdict(list)
    for item in members:
        weight = float(item["quality"]) * float(
            source_reliability.get(item["source"], 0.5)
        )
        for key, value in item["attributes"].items():
            values[key].append((value, weight, item["observation_id"]))
    attributes: dict[str, Any] = {}
    provenance: dict[str, list[str]] = {}
    for key, observations in sorted(values.items()):
        provenance[key] = sorted({observation_id for _, _, observation_id in observations})
        raw_values = [value for value, _, _ in observations]
        if all(isinstance(value, bool) for value in raw_values):
            true_weight = sum(weight for value, weight, _ in observations if value)
            total = sum(weight for _, weight, _ in observations)
            attributes[key] = true_weight >= total / 2.0
        elif all(
            isinstance(value, (int, float)) and not isinstance(value, bool)
            for value in raw_values
        ):
            numerator = sum(float(value) * weight for value, weight, _ in observations)
            denominator = sum(weight for _, weight, _ in observations)
            attributes[key] = round(numerator / denominator, 10) if denominator else 0.0
        else:
            weighted: Counter[str] = Counter()
            originals: dict[str, Any] = {}
            for value, weight, _ in observations:
                token = repr(value)
                weighted[token] += weight
                originals[token] = value
            winner = sorted(weighted, key=lambda item: (-weighted[item], item))[0]
            attributes[key] = originals[winner]
    return attributes, provenance
