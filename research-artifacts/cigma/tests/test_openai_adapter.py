from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from cigma.benchmark import generate_benchmark
from cigma.io import write_json
from cigma.openai_adapter import (
    _bounded_input,
    generate_candidates,
    replay_candidates,
    validate_candidate_batch,
)
from cigma.pipeline import run_pipeline


ARTIFACT_ROOT = Path(__file__).resolve().parents[1]


class OpenAIAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = yaml.safe_load(
            (ARTIFACT_ROOT / "configs" / "default.yaml").read_text(encoding="utf-8")
        )
        cls.public, _ = generate_benchmark(cls.config)
        cls.graph = run_pipeline(cls.public, cls.config, "cigma")

    def test_default_adapter_fails_closed_before_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "disabled"):
                generate_candidates(
                    self.public,
                    self.graph,
                    self.config,
                    directory,
                    explicitly_enabled=False,
                )

    def test_saved_response_replays_without_graph_mutation(self) -> None:
        direct = next(edge for edge in self.graph.edges if edge.method == "direct_observation")
        batch = {
            "candidates": [
                {
                    "claim_id": "replay-001",
                    "subject": direct.subject,
                    "predicate": direct.predicate,
                    "object": direct.object,
                    "evidence_ids": direct.evidence_ids,
                    "method": "llm_candidate",
                    "rule": None,
                }
            ]
        }
        raw = {"output_text": json.dumps(batch, sort_keys=True)}
        before = copy.deepcopy(self.graph.to_dict())
        with tempfile.TemporaryDirectory() as directory:
            raw_path = Path(directory) / "raw.json"
            write_json(raw_path, raw)
            result = replay_candidates(
                self.public, self.graph, raw_path, Path(directory) / "replay"
            )
        self.assertEqual(len(result["accepted"]), 1)
        self.assertEqual(result["rejected"], [])
        self.assertFalse(result["graph_mutated"])
        self.assertEqual(before, self.graph.to_dict())

    def test_bounded_input_excludes_oracle_edges_scores_and_structured_attributes(self) -> None:
        payload = _bounded_input(self.public, self.graph, {"max_input_records": 500})
        self.assertNotIn("accepted_graph_edges", payload)
        structured_keys: set[str] = set()

        def collect_keys(value: object) -> None:
            if isinstance(value, dict):
                structured_keys.update(str(key) for key in value)
                for child in value.values():
                    collect_keys(child)
            elif isinstance(value, list):
                for child in value:
                    collect_keys(child)

        collect_keys(payload)
        for forbidden in [
            "oracle",
            "edges",
            "scores",
            "attributes",
            "confidence",
            "criticality",
            "priority",
            "urgency",
            "migration_target",
        ]:
            self.assertNotIn(forbidden, structured_keys)
        self.assertTrue(payload["graph_nodes"])
        self.assertEqual(
            set(payload["graph_nodes"][0]),
            {"node_id", "entity_type", "member_observation_ids"},
        )
        excerpts = [
            item["evidence"]["excerpt"]
            for kind in ("entities", "claims")
            for item in payload["observations"][kind]
        ]
        self.assertTrue(any("criticality" in excerpt for excerpt in excerpts))
        self.assertTrue(any("exposure" in excerpt for excerpt in excerpts))

    def test_path_accepts_sufficient_observations_not_all_merged_evidence(self) -> None:
        member_to_node = {
            observation_id: node_id
            for node_id, node in self.graph.nodes.items()
            for observation_id in node.member_observation_ids
        }
        candidate = {
            "claim_id": "minimal-hosted-path",
            "subject": member_to_node["cmdb:entity:001"],
            "predicate": "USES",
            "object": member_to_node["tls:entity:003"],
            "evidence_ids": [
                "cmdb:claim:001",
                "tls:claim:001",
                "tls:claim:002",
            ],
            "method": "llm_candidate",
            "rule": "hosted_certificate_algorithm",
        }
        accepted, rejected = validate_candidate_batch(
            {"candidates": [candidate]}, self.public, self.graph
        )
        self.assertEqual(accepted, [candidate])
        self.assertEqual(rejected, [])

        unrelated = copy.deepcopy(candidate)
        unrelated["claim_id"] = "path-with-unrelated-evidence"
        unrelated["evidence_ids"] = [*candidate["evidence_ids"], "cmdb:claim:004"]
        accepted, rejected = validate_candidate_batch(
            {"candidates": [unrelated]}, self.public, self.graph
        )
        self.assertEqual(accepted, [])
        self.assertEqual(rejected[0]["reason"], "unsupported_path")

    def test_direct_candidate_rejects_any_unrelated_cited_evidence(self) -> None:
        direct = next(edge for edge in self.graph.edges if edge.method == "direct_observation")
        unrelated_evidence = next(
            claim["observation_id"]
            for claim in self.public["claims"]
            if claim["observation_id"] not in direct.evidence_ids
        )
        candidate = {
            "claim_id": "direct-with-unrelated-evidence",
            "subject": direct.subject,
            "predicate": direct.predicate,
            "object": direct.object,
            "evidence_ids": [*direct.evidence_ids, unrelated_evidence],
            "method": "llm_candidate",
            "rule": None,
        }
        accepted, rejected = validate_candidate_batch(
            {"candidates": [candidate]}, self.public, self.graph
        )
        self.assertEqual(accepted, [])
        self.assertEqual(rejected[0]["reason"], "unsupported_direct_claim")

    def test_arbitrary_candidate_json_fails_closed_without_type_errors(self) -> None:
        direct = next(edge for edge in self.graph.edges if edge.method == "direct_observation")
        valid = {
            "claim_id": "typed-candidate",
            "subject": direct.subject,
            "predicate": direct.predicate,
            "object": direct.object,
            "evidence_ids": direct.evidence_ids,
            "method": "llm_candidate",
            "rule": None,
        }
        malformed = []
        for field, value in [
            ("claim_id", []),
            ("subject", None),
            ("predicate", []),
            ("object", {}),
            ("evidence_ids", [{}]),
            ("method", 1),
            ("rule", []),
        ]:
            candidate = copy.deepcopy(valid)
            candidate[field] = value
            malformed.append(candidate)
        accepted, rejected = validate_candidate_batch(
            {"candidates": malformed}, self.public, self.graph
        )
        self.assertEqual(accepted, [])
        self.assertEqual(
            [item["reason"] for item in rejected],
            ["candidate_schema"] * len(malformed),
        )

    def test_replay_enforces_schema_candidate_limit(self) -> None:
        accepted, rejected = validate_candidate_batch(
            {"candidates": [{} for _ in range(201)]}, self.public, self.graph
        )
        self.assertEqual(accepted, [])
        self.assertEqual(
            rejected, [{"candidate": None, "reason": "batch_schema"}]
        )


if __name__ == "__main__":
    unittest.main()
