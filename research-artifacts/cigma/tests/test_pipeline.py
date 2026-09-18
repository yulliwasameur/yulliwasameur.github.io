from __future__ import annotations

import copy
import unittest
from pathlib import Path

import yaml

from cigma.benchmark import generate_benchmark
from cigma.openai_adapter import validate_candidate_batch
from cigma.pipeline import run_pipeline
from cigma.evaluation import evaluate_method
from cigma.validation import ValidationError, validate_public_observations


ARTIFACT_ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = yaml.safe_load(
            (ARTIFACT_ROOT / "configs" / "default.yaml").read_text(
                encoding="utf-8"
            )
        )
        cls.public, cls.oracle = generate_benchmark(cls.config)
        cls.graph = run_pipeline(cls.public, cls.config, "cigma")

    def test_pipeline_has_no_oracle_access_and_preserves_provenance(self) -> None:
        self.assertFalse(self.graph.metadata["oracle_access"])
        entity_ids = {item["observation_id"] for item in self.public["entities"]}
        claim_ids = {item["observation_id"] for item in self.public["claims"]}
        for node in self.graph.nodes.values():
            self.assertTrue(node.member_observation_ids)
            self.assertLessEqual(set(node.member_observation_ids), entity_ids)
        for edge in self.graph.edges:
            self.assertTrue(edge.evidence_ids)
            self.assertLessEqual(set(edge.evidence_ids), claim_ids)

    def test_public_validator_rejects_oracle_leak_and_open_predicate(self) -> None:
        leaked = copy.deepcopy(self.public)
        leaked["metadata"]["oracle"] = {"truth_id": "forbidden"}
        with self.assertRaises(ValidationError):
            validate_public_observations(leaked)
        open_predicate = copy.deepcopy(self.public)
        open_predicate["claims"][0]["predicate"] = "INVENTED_RELATION"
        with self.assertRaises(ValidationError):
            validate_public_observations(open_predicate)

    def test_source_reliability_rejects_out_of_range_values(self) -> None:
        for value in (-1.0, 2.0):
            with self.subTest(value=value):
                config = copy.deepcopy(self.config)
                config["confidence"]["source_reliability"]["cmdb"] = value
                with self.assertRaisesRegex(
                    ValidationError,
                    r"confidence\.source_reliability\.cmdb is outside \[0,1\]",
                ):
                    run_pipeline(self.public, config, "cigma")

    def test_source_reliability_rejects_nonfinite_values(self) -> None:
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                config = copy.deepcopy(self.config)
                config["confidence"]["source_reliability"]["cmdb"] = value
                with self.assertRaisesRegex(
                    ValidationError,
                    r"confidence\.source_reliability\.cmdb must be finite",
                ):
                    run_pipeline(self.public, config, "cigma")

    def test_uniform_reliability_ablation_cannot_bypass_validation(self) -> None:
        config = copy.deepcopy(self.config)
        config["confidence"]["source_reliability"]["cmdb"] = float("nan")
        with self.assertRaisesRegex(ValidationError, r"must be finite"):
            run_pipeline(self.public, config, "cigma_uniform_reliability")

    def test_optional_candidate_claims_fail_closed(self) -> None:
        service = next(
            node_id
            for node_id, node in self.graph.nodes.items()
            if node.entity_type == "service"
        )
        algorithm = next(
            node_id
            for node_id, node in self.graph.nodes.items()
            if node.entity_type == "algorithm"
        )
        unrelated_evidence = next(
            item["observation_id"]
            for item in self.public["claims"]
            if item["predicate"] != "USES"
        )
        probes = [
            {
                "claim_id": "missing",
                "subject": service,
                "predicate": "USES",
                "object": algorithm,
                "evidence_ids": [],
                "method": "llm_candidate",
                "rule": None,
            },
            {
                "claim_id": "ontology",
                "subject": service,
                "predicate": "INVENTED_RELATION",
                "object": algorithm,
                "evidence_ids": [unrelated_evidence],
                "method": "llm_candidate",
                "rule": None,
            },
            {
                "claim_id": "unsupported",
                "subject": service,
                "predicate": "USES",
                "object": algorithm,
                "evidence_ids": [unrelated_evidence],
                "method": "llm_candidate",
                "rule": None,
            },
        ]
        accepted, rejected = validate_candidate_batch(
            {"candidates": probes}, self.public, self.graph
        )
        self.assertEqual(accepted, [])
        self.assertEqual(
            {item["reason"] for item in rejected},
            {
                "unknown_or_empty_evidence",
                "ontology_signature",
                "unsupported_direct_claim",
            },
        )

    def test_source_union_keeps_all_observations_as_distinct_clusters(self) -> None:
        graph = run_pipeline(self.public, self.config, "source_union")
        self.assertEqual(len(graph.nodes), len(self.public["entities"]))
        self.assertTrue(
            all(len(node.member_observation_ids) == 1 for node in graph.nodes.values())
        )
        metrics, details = evaluate_method(
            graph, [], self.oracle, self.public, self.config
        )
        self.assertEqual(details["asset_counts"], {
            "tp": 23, "fp": 23, "fn": 0, "predicted": 46, "truth": 23
        })
        self.assertAlmostEqual(metrics["asset_f1"], 2.0 / 3.0)
        self.assertEqual(details["edge_counts"], {
            "tp": 29, "fp": 5, "fn": 5, "predicted": 34, "truth": 34
        })
        self.assertAlmostEqual(metrics["edge_f1"], 29.0 / 34.0)
        self.assertAlmostEqual(metrics["unsupported_edge_rate"], 5.0 / 34.0)


if __name__ == "__main__":
    unittest.main()
