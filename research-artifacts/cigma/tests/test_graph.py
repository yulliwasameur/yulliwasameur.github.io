from __future__ import annotations

import copy
import unittest
from pathlib import Path

import yaml

from cigma.benchmark import generate_benchmark
from cigma.evaluation import evaluate_method
from cigma.pipeline import run_pipeline
from cigma.scoring import (
    ALGORITHM_QUANTUM_VULNERABILITY_V1,
    IMPACT_FACTORS,
    PRIMARY_RANKING_POLICY,
    _pareto_fronts,
    fit_independent_calibrator,
    score_graph,
)


ARTIFACT_ROOT = Path(__file__).resolve().parents[1]


class GraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = yaml.safe_load(
            (ARTIFACT_ROOT / "configs" / "default.yaml").read_text(encoding="utf-8")
        )
        cls.public, cls.oracle = generate_benchmark(cls.config)
        cls.calibrator = fit_independent_calibrator(
            ARTIFACT_ROOT / "fixtures" / "calibration_panel.csv",
            seed=int(cls.config["seed"]),
        )

    def test_fusion_reduces_duplicates_and_adds_grounded_edges(self) -> None:
        flat = run_pipeline(self.public, self.config, "source_union")
        rules = run_pipeline(self.public, self.config, "exact_direct")
        cigma = run_pipeline(self.public, self.config, "cigma")
        self.assertLess(len(cigma.nodes), len(flat.nodes))
        self.assertGreaterEqual(len(cigma.edges), len(rules.edges))
        for edge in cigma.edges:
            self.assertTrue(edge.evidence_ids)
        flat_metrics, _ = evaluate_method(
            flat,
            score_graph(flat, self.config, calibrator=self.calibrator),
            self.oracle,
            self.public,
            self.config,
        )
        rules_metrics, _ = evaluate_method(
            rules,
            score_graph(rules, self.config, calibrator=self.calibrator),
            self.oracle,
            self.public,
            self.config,
        )
        cigma_metrics, _ = evaluate_method(
            cigma,
            score_graph(cigma, self.config, calibrator=self.calibrator),
            self.oracle,
            self.public,
            self.config,
        )
        self.assertGreater(cigma_metrics["asset_f1"], flat_metrics["asset_f1"])
        self.assertGreaterEqual(cigma_metrics["edge_recall"], rules_metrics["edge_recall"])
        self.assertTrue(cigma_metrics["provenance_invariant"])

    def test_validator_rejects_unsupported_claims(self) -> None:
        graph = run_pipeline(self.public, self.config, "cigma")
        reasons = {item["reason"] for item in graph.rejected_claims}
        self.assertIn("entity_quality_below_threshold", reasons)
        self.assertIn("claim_quality_below_threshold", reasons)
        metrics, _ = evaluate_method(
            graph,
            score_graph(graph, self.config, calibrator=self.calibrator),
            self.oracle,
            self.public,
            self.config,
        )
        self.assertEqual(metrics["unsupported_edge_rate"], 0.0)

    def test_confidence_does_not_change_urgency(self) -> None:
        graph = run_pipeline(self.public, self.config, "cigma")
        before = {
            row["node_id"]: (row["policy_tier"], row["primary_rank_score"])
            for row in score_graph(graph, self.config, calibrator=self.calibrator)
        }
        changed = copy.deepcopy(graph)
        for node in changed.nodes.values():
            node.confidence = 0.01
        after = {
            row["node_id"]: (row["policy_tier"], row["primary_rank_score"])
            for row in score_graph(changed, self.config, calibrator=self.calibrator)
        }
        self.assertEqual(before, after)

    def test_agility_cannot_change_primary_urgency_rank(self) -> None:
        graph = run_pipeline(self.public, self.config, "cigma")
        low_agility = copy.deepcopy(graph)
        high_agility = copy.deepcopy(graph)
        for node in low_agility.nodes.values():
            if "agility" in node.attributes:
                node.attributes["agility"] = 0.0
        for node in high_agility.nodes.values():
            if "agility" in node.attributes:
                node.attributes["agility"] = 1.0
        low = {
            row["node_id"]: (
                row["policy_tier_lower_bound"],
                row["policy_tier_upper_bound"],
                row["pareto_front"],
                row["primary_rank"],
            )
            for row in score_graph(
                low_agility, self.config, calibrator=self.calibrator
            )
        }
        high = {
            row["node_id"]: (
                row["policy_tier_lower_bound"],
                row["policy_tier_upper_bound"],
                row["pareto_front"],
                row["primary_rank"],
            )
            for row in score_graph(
                high_agility, self.config, calibrator=self.calibrator
            )
        }
        self.assertEqual(low, high)

    def test_pareto_fronts_are_isolated_by_policy_tier_bounds(self) -> None:
        def row(
            node_id: str,
            upper: int,
            lower: int,
            values: tuple[float, ...],
        ) -> dict[str, object]:
            return {
                "node_id": node_id,
                "policy_tier_upper_bound": upper,
                "policy_tier_lower_bound": lower,
                **{
                    f"impact_upper_{factor}": value
                    for factor, value in zip(IMPACT_FACTORS, values, strict=True)
                },
            }

        within_tier = [
            row("tier-2-front-1", 2, 2, (0.8, 0.7, 0.8, 0.5, 0.4)),
            row("tier-2-front-2", 2, 2, (0.8, 0.6, 0.7, 0.4, 0.3)),
        ]
        before = _pareto_fronts(within_tier)
        higher_tier_dominator = row(
            "tier-3-dominator", 3, 3, (1.0, 1.0, 1.0, 1.0, 1.0)
        )
        after = _pareto_fronts([*within_tier, higher_tier_dominator])

        self.assertEqual(before["tier-2-front-1"], 1)
        self.assertEqual(before["tier-2-front-2"], 2)
        self.assertEqual(
            {node_id: after[node_id] for node_id in before},
            before,
        )
        self.assertEqual(after["tier-3-dominator"], 1)

    def test_config_declares_the_implemented_primary_policy(self) -> None:
        self.assertEqual(
            self.config["scoring"]["primary_policy"],
            PRIMARY_RANKING_POLICY,
        )

    def test_high_impact_unknown_is_not_silently_downgraded(self) -> None:
        graph = run_pipeline(self.public, self.config, "cigma")
        target = next(
            node_id
            for node_id, node in graph.nodes.items()
            if node.entity_type == "service"
            and float(node.attributes.get("criticality", 0.0)) >= 0.9
        )
        incomplete = copy.deepcopy(graph)
        incomplete.edges = [
            edge
            for edge in incomplete.edges
            if not (edge.subject == target and edge.predicate == "USES")
        ]
        row = next(
            item
            for item in score_graph(
                incomplete, self.config, calibrator=self.calibrator
            )
            if item["node_id"] == target
        )
        self.assertIn("quantum_vulnerability", row["missing_impact_factors"])
        self.assertGreater(row["policy_tier_upper_bound"], row["policy_tier_lower_bound"])
        self.assertTrue(row["verification_required"])

    def test_unknown_impact_factors_export_zero_one_bounds(self) -> None:
        graph = run_pipeline(self.public, self.config, "cigma")
        incomplete = copy.deepcopy(graph)
        incomplete.edges = [
            edge
            for edge in incomplete.edges
            if not (
                edge.predicate == "USES"
                and incomplete.nodes[edge.object].entity_type == "algorithm"
            )
        ]
        for node in incomplete.nodes.values():
            node.attributes.pop("criticality", None)
            node.attributes.pop("exposure", None)
        row = next(
            item
            for item in score_graph(
                incomplete, self.config, calibrator=self.calibrator
            )
            if item["entity_type"] == "service"
        )
        self.assertGreaterEqual(
            set(row["missing_impact_factors"]),
            {
                "quantum_vulnerability",
                "hndl_urgency",
                "criticality",
                "exposure",
            },
        )
        for factor in IMPACT_FACTORS:
            if factor in row["missing_impact_factors"]:
                self.assertEqual(row[f"impact_lower_{factor}"], 0.0)
                self.assertEqual(row[f"impact_upper_{factor}"], 1.0)
            else:
                self.assertEqual(row[f"impact_lower_{factor}"], row[factor])
                self.assertEqual(row[f"impact_upper_{factor}"], row[factor])

    def test_unknown_hndl_lower_bound_ignores_diagnostic_imputation(self) -> None:
        graph = run_pipeline(self.public, self.config, "cigma")
        incomplete = copy.deepcopy(graph)
        for node in incomplete.nodes.values():
            node.attributes.pop("data_lifetime_years", None)
            node.attributes.pop("retention_years", None)
        row = next(
            item
            for item in score_graph(
                incomplete, self.config, calibrator=self.calibrator
            )
            if item["entity_type"] == "service"
            and item["quantum_vulnerability"] == 1.0
            and item["migration_time_known"]
        )
        self.assertFalse(row["data_lifetime_known"])
        self.assertIn("hndl_urgency", row["missing_impact_factors"])
        self.assertGreater(row["hndl_urgency"], 0.0)
        self.assertEqual(row["impact_lower_hndl_urgency"], 0.0)
        self.assertEqual(row["impact_upper_hndl_urgency"], 1.0)

    def test_no_algorithm_edges_apply_half_confidence_penalty(self) -> None:
        graph = run_pipeline(self.public, self.config, "cigma")
        without_algorithms = copy.deepcopy(graph)
        without_algorithms.edges = [
            edge
            for edge in without_algorithms.edges
            if not (
                edge.predicate == "USES"
                and without_algorithms.nodes[edge.object].entity_type == "algorithm"
            )
        ]
        target = next(
            node_id
            for node_id, node in without_algorithms.nodes.items()
            if node.entity_type == "service"
        )
        without_algorithms.nodes[target].confidence = 0.8
        row = next(
            item
            for item in score_graph(
                without_algorithms, self.config, calibrator=self.calibrator
            )
            if item["node_id"] == target
        )
        self.assertEqual(row["algorithm_nodes"], [])
        self.assertEqual(row["epistemic_confidence"], 0.4)

    def test_algorithm_policy_ignores_falsified_source_risk(self) -> None:
        self.assertEqual(
            ALGORITHM_QUANTUM_VULNERABILITY_V1,
            {"rsa-2048": 1.0, "ecdsa-p256": 1.0, "aes-256-gcm": 0.15},
        )
        graph = run_pipeline(self.public, self.config, "cigma")
        baseline = {
            row["node_id"]: (
                row["quantum_vulnerability"],
                row["policy_tier_lower_bound"],
                row["policy_tier_upper_bound"],
                row["pareto_front"],
                row["primary_rank"],
            )
            for row in score_graph(graph, self.config, calibrator=self.calibrator)
        }
        falsified = copy.deepcopy(graph)
        rsa_node = next(
            node
            for node in falsified.nodes.values()
            if "rsa-2048"
            in node.attributes.get("identifiers", {}).get("algorithm_id", [])
        )
        rsa_node.attributes["quantum_vulnerability"] = -999.0
        rescored = {
            row["node_id"]: (
                row["quantum_vulnerability"],
                row["policy_tier_lower_bound"],
                row["policy_tier_upper_bound"],
                row["pareto_front"],
                row["primary_rank"],
            )
            for row in score_graph(
                falsified, self.config, calibrator=self.calibrator
            )
        }
        self.assertEqual(baseline, rescored)

    def test_unknown_algorithm_policy_id_requires_verification(self) -> None:
        graph = run_pipeline(self.public, self.config, "cigma")
        unknown = copy.deepcopy(graph)
        aes_node_id = next(
            node_id
            for node_id, node in unknown.nodes.items()
            if "aes-256-gcm"
            in node.attributes.get("identifiers", {}).get("algorithm_id", [])
        )
        unknown.nodes[aes_node_id].attributes["identifiers"]["algorithm_id"] = [
            "unknown-aead"
        ]
        row = next(
            item
            for item in score_graph(
                unknown, self.config, calibrator=self.calibrator
            )
            if item["entity_type"] == "service"
            and item["algorithm_nodes"] == [aes_node_id]
        )
        self.assertIn("quantum_vulnerability", row["missing_impact_factors"])
        self.assertEqual(row["quantum_vulnerability"], 0.0)
        self.assertEqual(row["impact_lower_quantum_vulnerability"], 0.0)
        self.assertEqual(row["impact_upper_quantum_vulnerability"], 1.0)
        self.assertGreater(
            row["policy_tier_upper_bound"], row["policy_tier_lower_bound"]
        )
        self.assertTrue(row["verification_required"])


if __name__ == "__main__":
    unittest.main()
