"""Deterministic normalization of heterogeneous observation records."""

from __future__ import annotations

import copy
import re
from typing import Any


_ALGORITHM_ALIASES = {
    "rsa2048": "rsa-2048",
    "rsa-2048": "rsa-2048",
    "rsa 2048": "rsa-2048",
    "ecdsa-p256": "ecdsa-p256",
    "ecdsa p-256": "ecdsa-p256",
    "prime256v1": "ecdsa-p256",
    "secp256r1": "ecdsa-p256",
    "aes-256-gcm": "aes-256-gcm",
    "aes256-gcm": "aes-256-gcm",
}


def normalize_public(public: dict[str, Any]) -> dict[str, Any]:
    """Return a deep normalized copy; evidence bytes remain unchanged."""

    normalized = copy.deepcopy(public)
    normalized["entities"] = [normalize_entity(item) for item in public["entities"]]
    normalized["claims"] = [normalize_claim(item) for item in public["claims"]]
    normalized["metadata"] = copy.deepcopy(public["metadata"])
    normalized["metadata"]["normalization_profile"] = "cigma-v1"
    return normalized


def normalize_entity(entity: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(entity)
    result["source"] = _token(result["source"])
    result["entity_type"] = _token(result["entity_type"])
    identifiers: dict[str, str] = {}
    for raw_key, raw_value in result.get("identifiers", {}).items():
        key = _token(raw_key)
        value = _identifier_value(key, raw_value)
        if value:
            identifiers[key] = value
    result["identifiers"] = identifiers
    result["quality"] = float(result["quality"])
    return result


def normalize_claim(claim: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(claim)
    result["source"] = _token(result["source"])
    result["predicate"] = str(result["predicate"]).strip().upper()
    result["quality"] = float(result["quality"])
    return result


def _identifier_value(key: str, value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value).strip())
    if key in {"fingerprint_sha256", "spki_sha256", "serial_number", "uid", "pipeline_uid", "data_uid"}:
        return text.upper()
    if key == "algorithm_id":
        folded = text.casefold()
        return _ALGORITHM_ALIASES.get(folded, folded)
    if key == "endpoint_uri":
        return text.casefold().rstrip("/")
    if key == "hostname":
        return text.casefold().rstrip(".")
    if key == "purl":
        return text.casefold()
    if key in {"service_name", "repository_path", "deployment_name"}:
        return text.casefold().strip("/")
    return text.casefold()


def _token(value: Any) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", str(value).strip().casefold()).strip("_")
