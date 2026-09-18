"""Schema, evidence-integrity, and oracle-isolation checks."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Mapping, Sequence
from typing import Any

from .ontology import NODE_TYPES, RELATION_SIGNATURES


FORBIDDEN_PUBLIC_KEYS = {
    "truth_id",
    "truth_edge",
    "priority",
    "migration_target",
    "entity_observation_map",
    "claim_observation_map",
    "detectable_nodes",
    "oracle",
}


class ValidationError(ValueError):
    """Raised when an observation or graph violates the artifact contract."""


def validate_source_reliability(config: Mapping[str, Any]) -> dict[str, float]:
    """Return finite source probabilities, rejecting malformed values.

    Source reliability participates in entity, edge, and calibration confidence.
    Accepting NaN or an out-of-range value would therefore contaminate multiple
    outputs.  Validate the complete mapping before any method-specific override
    so that an invalid configuration cannot bypass this contract.
    """

    confidence = config.get("confidence", {})
    if not isinstance(confidence, Mapping):
        raise ValidationError("confidence must be a mapping")
    values = confidence.get("source_reliability", {})
    if not isinstance(values, Mapping):
        raise ValidationError("confidence.source_reliability must be a mapping")

    validated: dict[str, float] = {}
    for source, value in values.items():
        if not isinstance(source, str) or not source.strip():
            raise ValidationError(
                "confidence.source_reliability keys must be non-empty strings"
            )
        if isinstance(value, bool):
            raise ValidationError(
                f"confidence.source_reliability.{source} must be numeric"
            )
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                f"confidence.source_reliability.{source} must be numeric"
            ) from exc
        if not math.isfinite(numeric):
            raise ValidationError(
                f"confidence.source_reliability.{source} must be finite"
            )
        if not 0.0 <= numeric <= 1.0:
            raise ValidationError(
                f"confidence.source_reliability.{source} is outside [0,1]"
            )
        validated[source] = numeric
    return validated


def ensure_oracle_isolation(payload: Any, *, path: str = "$public") -> None:
    """Fail closed if evaluator-only field names appear in a public payload."""

    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if str(key).lower() in FORBIDDEN_PUBLIC_KEYS:
                raise ValidationError(f"oracle field {key!r} leaked at {path}")
            ensure_oracle_isolation(value, path=f"{path}.{key}")
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        for index, value in enumerate(payload):
            ensure_oracle_isolation(value, path=f"{path}[{index}]")


def validate_public_observations(public: dict[str, Any]) -> None:
    ensure_oracle_isolation(public)
    if not isinstance(public.get("metadata"), dict):
        raise ValidationError("metadata must be a mapping")
    entities = public.get("entities")
    claims = public.get("claims")
    if not isinstance(entities, list) or not isinstance(claims, list):
        raise ValidationError("entities and claims must be arrays")

    entity_ids: set[str] = set()
    all_ids: set[str] = set()
    for entity in entities:
        _require_keys(
            entity,
            {
                "observation_id",
                "source",
                "local_key",
                "entity_type",
                "identifiers",
                "attributes",
                "quality",
                "collected_at",
                "evidence",
            },
            "entity",
        )
        observation_id = str(entity["observation_id"])
        _unique(observation_id, all_ids)
        entity_ids.add(observation_id)
        if entity["entity_type"] not in NODE_TYPES:
            raise ValidationError(f"unknown node type: {entity['entity_type']!r}")
        if not isinstance(entity["identifiers"], dict):
            raise ValidationError(f"identifiers must be a mapping: {observation_id}")
        if not isinstance(entity["attributes"], dict):
            raise ValidationError(f"attributes must be a mapping: {observation_id}")
        _probability(entity["quality"], f"quality of {observation_id}")
        _validate_evidence(entity["evidence"], observation_id)

    for claim in claims:
        _require_keys(
            claim,
            {
                "observation_id",
                "source",
                "subject_observation_id",
                "predicate",
                "object_observation_id",
                "quality",
                "collected_at",
                "evidence",
            },
            "claim",
        )
        observation_id = str(claim["observation_id"])
        _unique(observation_id, all_ids)
        subject = str(claim["subject_observation_id"])
        obj = str(claim["object_observation_id"])
        if subject not in entity_ids or obj not in entity_ids:
            raise ValidationError(
                f"claim {observation_id} references an unknown entity"
            )
        if claim["predicate"] not in RELATION_SIGNATURES:
            raise ValidationError(
                f"claim {observation_id} uses unknown predicate {claim['predicate']!r}"
            )
        _probability(claim["quality"], f"quality of {observation_id}")
        _validate_evidence(claim["evidence"], observation_id)


def validate_oracle(oracle: dict[str, Any], public: dict[str, Any]) -> None:
    nodes = oracle.get("nodes")
    edges = oracle.get("edges")
    entity_map = oracle.get("entity_observation_map")
    claim_map = oracle.get("claim_observation_map")
    if not all(isinstance(value, expected) for value, expected in [
        (nodes, list), (edges, list), (entity_map, dict), (claim_map, dict)
    ]):
        raise ValidationError("oracle structure is incomplete")
    truth_ids = {str(node["id"]) for node in nodes}
    for edge in edges:
        if len(edge) != 3 or edge[0] not in truth_ids or edge[2] not in truth_ids:
            raise ValidationError(f"invalid oracle edge: {edge!r}")
    public_entity_ids = {item["observation_id"] for item in public["entities"]}
    public_claim_ids = {item["observation_id"] for item in public["claims"]}
    if set(entity_map) != public_entity_ids or set(claim_map) != public_claim_ids:
        raise ValidationError("oracle maps do not exactly cover public observations")


def relation_is_valid(
    predicate: str, subject_type: str, object_type: str
) -> bool:
    return (subject_type, object_type) in RELATION_SIGNATURES.get(predicate, set())


def _validate_evidence(evidence: Any, observation_id: str) -> None:
    if not isinstance(evidence, dict):
        raise ValidationError(f"evidence must be a mapping: {observation_id}")
    _require_keys(evidence, {"locator", "excerpt", "raw_sha256"}, "evidence")
    excerpt = str(evidence["excerpt"])
    expected = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
    if evidence["raw_sha256"] != expected:
        raise ValidationError(f"evidence digest mismatch: {observation_id}")
    if not str(evidence["locator"]).strip():
        raise ValidationError(f"empty evidence locator: {observation_id}")


def _require_keys(payload: Any, keys: set[str], label: str) -> None:
    if not isinstance(payload, dict):
        raise ValidationError(f"{label} must be a mapping")
    missing = keys - set(payload)
    if missing:
        raise ValidationError(f"{label} missing fields: {sorted(missing)}")


def _unique(value: str, seen: set[str]) -> None:
    if value in seen:
        raise ValidationError(f"duplicate observation_id: {value}")
    seen.add(value)


def _probability(value: Any, label: str) -> None:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{label} is not numeric") from exc
    if not 0.0 <= numeric <= 1.0:
        raise ValidationError(f"{label} is outside [0,1]")
