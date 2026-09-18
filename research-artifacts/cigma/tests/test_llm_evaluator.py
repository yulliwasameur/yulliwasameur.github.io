from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ARTIFACT_ROOT = Path(__file__).resolve().parents[1]


class ArchivedLLMEvaluatorTests(unittest.TestCase):
    def test_archived_runs_replay_against_no_path_cigma_base(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evaluation"
            environment = {
                "PATH": os.defpath,
                "PYTHONPATH": str(ARTIFACT_ROOT / "src"),
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            }
            subprocess.run(
                [
                    sys.executable,
                    str(ARTIFACT_ROOT / "scripts" / "evaluate_llm_runs.py"),
                    "--public",
                    str(
                        ARTIFACT_ROOT
                        / "results/default/data/public/observations.json"
                    ),
                    "--oracle",
                    str(ARTIFACT_ROOT / "results/default/data/oracle/oracle.json"),
                    "--base-graph",
                    str(ARTIFACT_ROOT / "results/default/graphs/cigma_no_paths.json"),
                    "--validation-graph",
                    str(ARTIFACT_ROOT / "results/default/graphs/cigma_no_paths.json"),
                    "--runs-root",
                    str(ARTIFACT_ROOT / "results/llm"),
                    "--output",
                    str(output),
                ],
                check=True,
                cwd=ARTIFACT_ROOT,
                env=environment,
            )
            summary = json.loads((output / "summary.json").read_text())
            self.assertTrue(summary["all_raw_hashes_match"])
            self.assertTrue(summary["all_replays_match"])
            self.assertTrue(summary["all_partitions_match"])
            self.assertTrue(summary["all_graph_mutated_false"])
            self.assertTrue(summary["all_archived_trace_hashes_match"])
            self.assertEqual(
                summary["archived_live_input_sha256"],
                "51b01bd64fa9a6a3580e0018b1b61e38f934f46bb463d1ad8efa6b061a20547d",
            )
            self.assertEqual(summary["base_graph_method"], "cigma_no_paths")
            self.assertEqual(summary["validation_graph_method"], "cigma_no_paths")
            self.assertEqual(summary["base_predicted_edges"], 29)
            self.assertEqual(summary["base_true_positive_edges"], 29)
            self.assertEqual(summary["base_false_positive_edges"], 0)
            self.assertEqual(summary["incremental_truth_edges"], 5)
            self.assertIn("cigma_no_paths", summary["hybrid_definition"])
            self.assertIn("shared canonical node IDs", summary["hybrid_definition"])
            self.assertAlmostEqual(summary["means"]["raw_precision"], 0.92846990483253)
            self.assertAlmostEqual(summary["means"]["raw_recall"], 0.8725490196078431)
            self.assertAlmostEqual(summary["means"]["raw_f1"], 0.8977614977614978)
            self.assertAlmostEqual(summary["means"]["accepted_f1"], 0.9305087465896325)
            self.assertAlmostEqual(summary["means"]["hybrid_f1"], 0.947089947089947)
            self.assertAlmostEqual(
                summary["means"]["incremental_edge_recall"], 1.0 / 3.0
            )
            self.assertAlmostEqual(
                summary["pairwise_accepted_jaccard_mean"], 0.8989898989898991
            )

            manifest = json.loads((output / "manifest.json").read_text())
            self.assertFalse(manifest["network_required"])
            for name, expected in manifest["outputs"].items():
                actual = hashlib.sha256((output / name).read_bytes()).hexdigest()
                self.assertEqual(actual, expected)

    def test_trace_registry_rejects_replacement_run(self) -> None:
        evaluator = (
            ARTIFACT_ROOT / "scripts" / "evaluate_llm_runs.py"
        ).read_text(encoding="utf-8")
        for digest in [
            "640fe6ae1ec0f28e215ae6866f5c6627456a87316eb1230fb5d27d3512ca2ada",
            "25618713befae32f2a01bfd29060274f1cc682ea1e36797bfa259292905637c7",
            "d56e6483ff25b6893d4e02013c97fcb0ca4dcdc7b61bb184381e299e02095309",
        ]:
            self.assertIn(digest, evaluator)


if __name__ == "__main__":
    unittest.main()
