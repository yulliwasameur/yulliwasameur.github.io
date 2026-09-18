"""Optional bounded Responses API adapter; disabled by default.

The adapter only creates untrusted candidate files. It never mutates a graph,
never reads an env file, and never serializes the API credential.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .io import canonical_json_bytes, read_json, write_json
from .model import GraphResult
from .ontology import ALLOWED_PATH_RULES, RELATION_SIGNATURES
from .validation import relation_is_valid


RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses"
_CANDIDATE_FIELDS = {
    "claim_id",
    "subject",
    "predicate",
    "object",
    "evidence_ids",
    "method",
    "rule",
}
_MAX_CANDIDATES = 200


def candidate_json_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["candidates"],
        "properties": {
            "candidates": {
                "type": "array",
                "maxItems": _MAX_CANDIDATES,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": sorted(_CANDIDATE_FIELDS),
                    "properties": {
                        "claim_id": {"type": "string", "minLength": 1},
                        "subject": {"type": "string", "minLength": 1},
                        "predicate": {
                            "type": "string",
                            "enum": sorted(RELATION_SIGNATURES),
                        },
                        "object": {"type": "string", "minLength": 1},
                        "evidence_ids": {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string", "minLength": 1},
                        },
                        "method": {"type": "string", "enum": ["llm_candidate"]},
                        "rule": {
                            "anyOf": [
                                {"type": "null"},
                                {"type": "string", "enum": sorted(ALLOWED_PATH_RULES)},
                            ]
                        },
                    },
                },
            }
        },
    }


def generate_candidates(
    public: dict[str, Any],
    graph: GraphResult,
    config: dict[str, Any],
    output: str | Path,
    *,
    explicitly_enabled: bool = False,
) -> dict[str, Any]:
    """Call Responses API once and persist raw + deterministically validated output."""

    settings = dict(config.get("openai_adapter", {}))
    if not explicitly_enabled or not bool(settings.get("enabled", False)):
        raise RuntimeError(
            "OpenAI adapter is disabled; set openai_adapter.enabled=true and pass "
            "the explicit CLI enable flag"
        )
    # Read only the process environment. Never search, source, or parse env files.
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not present in the process environment")
    model = str(settings.get("model", "gpt-5.4-nano-2026-03-17"))
    max_output_tokens = int(settings.get("max_output_tokens", 4000))
    prompt_path = Path(__file__).resolve().parents[2] / "prompts" / "bounded_llm_system.txt"
    system_prompt = prompt_path.read_text(encoding="utf-8")
    request_input = _bounded_input(public, graph, settings)
    body = {
        "model": model,
        "store": False,
        "max_output_tokens": max_output_tokens,
        "input": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "Propose only evidence-supported candidate relations from this "
                    "untrusted JSON payload:\n" + json.dumps(request_input, sort_keys=True)
                ),
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "cigma_candidate_batch",
                "strict": True,
                "schema": candidate_json_schema(),
            }
        },
    }
    reasoning_effort = settings.get("reasoning_effort")
    if reasoning_effort:
        body["reasoning"] = {"effort": str(reasoning_effort)}
    request = urllib.request.Request(
        RESPONSES_ENDPOINT,
        data=canonical_json_bytes(body),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(
            request, timeout=float(settings.get("timeout_seconds", 60))
        ) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Report only the API's structured error classification. Do not echo
        # response headers or request material because authorization metadata
        # exists in memory.
        try:
            error_payload = json.loads(exc.read().decode("utf-8"))
            error = error_payload.get("error", {})
            detail = ": ".join(
                str(value)
                for value in [
                    error.get("type"),
                    error.get("code"),
                    error.get("param"),
                    error.get("message"),
                ]
                if value
            )
        except (UnicodeDecodeError, json.JSONDecodeError):
            detail = "unparseable error body"
        raise RuntimeError(
            f"Responses API returned HTTP {exc.code}: {detail}"
        ) from None
    finally:
        api_key = ""  # minimize credential lifetime; never log or persist it
    latency_seconds = time.perf_counter() - started

    target = Path(output)
    target.mkdir(parents=True, exist_ok=True)
    write_json(target / "raw_response.json", raw)
    manifest = {
        "adapter": "openai-responses-api-v1",
        "endpoint": RESPONSES_ENDPOINT,
        "model": model,
        "returned_model": raw.get("model"),
        "response_id": raw.get("id"),
        "response_status": raw.get("status"),
        "usage": raw.get("usage", {}),
        "latency_seconds": latency_seconds,
        "max_output_tokens": max_output_tokens,
        "reasoning_effort": reasoning_effort,
        "store": False,
        "schema_sha256": _payload_digest(candidate_json_schema()),
        "prompt_sha256": hashlib.sha256(system_prompt.encode("utf-8")).hexdigest(),
        "input_sha256": _payload_digest(request_input),
        "credential_source": "process environment only",
        "credential_persisted": False,
    }
    write_json(target / "request_manifest.json", manifest)
    result = replay_candidates(public, graph, target / "raw_response.json", target)
    return {"manifest": manifest, **result}


def replay_candidates(
    public: dict[str, Any],
    graph: GraphResult,
    raw_response_path: str | Path,
    output: str | Path,
) -> dict[str, Any]:
    """Replay validation without network or API credentials."""

    raw = read_json(raw_response_path)
    output_text = _extract_output_text(raw)
    try:
        batch = json.loads(output_text)
    except json.JSONDecodeError as exc:
        batch = {"candidates": []}
        parse_error = f"invalid_json:{exc.msg}"
    else:
        parse_error = None
    accepted, rejected = validate_candidate_batch(batch, public, graph)
    result = {
        "raw_response_sha256": sha256_path(raw_response_path),
        "parse_error": parse_error,
        "accepted": accepted,
        "rejected": rejected,
        "graph_mutated": False,
    }
    target = Path(output)
    target.mkdir(parents=True, exist_ok=True)
    write_json(target / "validated_candidates.json", result)
    return result


def validate_candidate_batch(
    batch: Any, public: dict[str, Any], graph: GraphResult
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Fail closed; accepted candidates remain separate from graph predictions."""

    if (
        not isinstance(batch, dict)
        or set(batch) != {"candidates"}
        or not isinstance(batch["candidates"], list)
        or len(batch["candidates"]) > _MAX_CANDIDATES
    ):
        return [], [{"candidate": None, "reason": "batch_schema"}]
    claim_by_id = {item["observation_id"]: item for item in public["claims"]}
    member_to_node = {
        observation_id: node_id
        for node_id, node in graph.nodes.items()
        for observation_id in node.member_observation_ids
    }
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for candidate in batch["candidates"]:
        reason = _candidate_rejection_reason(
            candidate,
            graph,
            claim_by_id,
            member_to_node,
            seen_ids,
        )
        if reason is None:
            seen_ids.add(candidate["claim_id"])
            accepted.append(candidate)
        else:
            rejected.append({"candidate": candidate, "reason": reason})
    accepted.sort(key=lambda item: item["claim_id"])
    rejected.sort(key=lambda item: json.dumps(item, sort_keys=True))
    return accepted, rejected


def _candidate_rejection_reason(
    candidate: Any,
    graph: GraphResult,
    claim_by_id: dict[str, dict[str, Any]],
    member_to_node: dict[str, str],
    seen_ids: set[str],
) -> str | None:
    if not isinstance(candidate, dict) or set(candidate) != _CANDIDATE_FIELDS:
        return "candidate_schema"
    for field in ("claim_id", "subject", "predicate", "object", "method"):
        if not isinstance(candidate[field], str) or not candidate[field]:
            return "candidate_schema"
    if candidate["rule"] is not None and (
        not isinstance(candidate["rule"], str) or not candidate["rule"]
    ):
        return "candidate_schema"
    if not isinstance(candidate["evidence_ids"], list) or any(
        not isinstance(item, str) or not item for item in candidate["evidence_ids"]
    ):
        return "candidate_schema"
    if candidate["claim_id"] in seen_ids:
        return "duplicate_claim_id"
    subject = candidate["subject"]
    obj = candidate["object"]
    predicate = candidate["predicate"]
    if subject not in graph.nodes or obj not in graph.nodes:
        return "unknown_node"
    if predicate not in RELATION_SIGNATURES or not relation_is_valid(
        predicate, graph.nodes[subject].entity_type, graph.nodes[obj].entity_type
    ):
        return "ontology_signature"
    evidence = candidate["evidence_ids"]
    if not evidence or any(item not in claim_by_id for item in evidence):
        return "unknown_or_empty_evidence"
    if candidate["method"] != "llm_candidate":
        return "method_schema"
    rule = candidate["rule"]
    if rule is None:
        # Every cited observation must support this exact canonical triple.
        # Accepting after the first match would allow an unrelated but existing
        # evidence ID to be laundered into the candidate provenance.
        for evidence_id in evidence:
            observation = claim_by_id[evidence_id]
            if not (
                member_to_node.get(observation["subject_observation_id"]) == subject
                and observation["predicate"] == predicate
                and member_to_node.get(observation["object_observation_id"]) == obj
            ):
                return "unsupported_direct_claim"
        return None
    if rule not in ALLOWED_PATH_RULES or predicate != "USES":
        return "unknown_path_rule"
    return (
        None
        if _path_is_supported(
            subject,
            obj,
            rule,
            set(evidence),
            graph,
            claim_by_id,
            member_to_node,
        )
        else "unsupported_path"
    )


def _path_is_supported(
    subject: str,
    obj: str,
    rule: str,
    evidence: set[str],
    graph: GraphResult,
    claim_by_id: dict[str, dict[str, Any]],
    member_to_node: dict[str, str],
) -> bool:
    """Validate a complete path from the cited claim observations.

    Graph edges can merge several corroborating observations. Requiring every
    merged evidence ID would reject a sufficient source-specific path. Instead,
    each cited ID must map to an accepted direct-edge step, every rule step must
    be covered, and all cited steps must belong to the same subject-to-object
    path. Redundant observations supporting one selected step are allowed.
    """

    pattern = ALLOWED_PATH_RULES[rule]
    accepted_direct = {
        (edge.subject, edge.predicate, edge.object)
        for edge in graph.edges
        if edge.method == "direct_observation"
    }
    cited_steps: list[tuple[str, str, str]] = []
    for evidence_id in sorted(evidence):
        observation = claim_by_id[evidence_id]
        step = (
            member_to_node.get(observation["subject_observation_id"]),
            observation["predicate"],
            member_to_node.get(observation["object_observation_id"]),
        )
        if None in step or step not in accepted_direct:
            return False
        cited_steps.append(step)  # type: ignore[arg-type]

    adjacency: dict[tuple[str, str], set[str]] = {}
    for step_subject, predicate, step_object in cited_steps:
        adjacency.setdefault((step_subject, predicate), set()).add(step_object)

    def walk(
        current: str,
        index: int,
        selected: tuple[tuple[str, str, str], ...],
    ) -> bool:
        if index == len(pattern):
            selected_set = set(selected)
            return current == obj and all(step in selected_set for step in cited_steps)
        return any(
            walk(
                next_node,
                index + 1,
                selected + ((current, pattern[index], next_node),),
            )
            for next_node in sorted(adjacency.get((current, pattern[index]), set()))
        )

    return walk(subject, 0, ())


def _bounded_input(
    public: dict[str, Any], graph: GraphResult, settings: dict[str, Any]
) -> dict[str, Any]:
    max_records = int(settings.get("max_input_records", 500))
    entities = [
        {
            "observation_id": item["observation_id"],
            "source": item["source"],
            "local_key": item["local_key"],
            "entity_type": item["entity_type"],
            "identifiers": item.get("identifiers", {}),
            "collected_at": item.get("collected_at"),
            "evidence": item.get("evidence", {}),
        }
        for item in public["entities"][:max_records]
    ]
    remaining = max(0, max_records - len(entities))
    claims = [
        {
            "observation_id": item["observation_id"],
            "source": item["source"],
            "subject_observation_id": item["subject_observation_id"],
            "predicate": item["predicate"],
            "object_observation_id": item["object_observation_id"],
            "collected_at": item.get("collected_at"),
            "evidence": item.get("evidence", {}),
        }
        for item in public["claims"][:remaining]
    ]
    return {
        "ontology_relations": sorted(RELATION_SIGNATURES),
        "allowed_path_rules": {
            key: list(value) for key, value in sorted(ALLOWED_PATH_RULES.items())
        },
        # Only graph identity/type information is exposed: existing graph
        # edges, computed scores, structured graph attributes, rankings, and
        # evaluator outputs are deliberately absent. The public evidence
        # excerpts remain verbatim observation input and may themselves state
        # observed business context such as criticality or exposure.
        "graph_nodes": [
            {
                "node_id": graph.nodes[key].node_id,
                "entity_type": graph.nodes[key].entity_type,
                "member_observation_ids": graph.nodes[key].member_observation_ids,
            }
            for key in sorted(graph.nodes)
        ],
        "observations": {"entities": entities, "claims": claims},
        "truncated": len(entities) + len(claims)
        < len(public["entities"]) + len(public["claims"]),
    }


def _extract_output_text(raw: dict[str, Any]) -> str:
    if isinstance(raw.get("output_text"), str):
        return raw["output_text"]
    for item in raw.get("output", []):
        for content in item.get("content", []):
            if isinstance(content.get("text"), str):
                return content["text"]
    return '{"candidates":[]}'


def _payload_digest(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def sha256_path(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
