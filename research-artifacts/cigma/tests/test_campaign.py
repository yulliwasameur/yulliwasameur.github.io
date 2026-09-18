from __future__ import annotations

import json
import csv
import shutil
import unittest
from pathlib import Path

from cigma.experiment import load_config, run_campaign


ARTIFACT_ROOT = Path(__file__).resolve().parents[1]


class CampaignTests(unittest.TestCase):
    def test_campaign_smoke(self) -> None:
        output = ARTIFACT_ROOT / "results" / "test-smoke"
        if output.exists():
            shutil.rmtree(output)
        try:
            config = load_config(ARTIFACT_ROOT / "configs" / "default.yaml")
            summary = run_campaign(config, output)
            self.assertTrue((output / "summary.json").is_file())
            self.assertTrue((output / "metrics" / "nodes.csv").is_file())
            self.assertTrue((output / "metrics" / "edges.csv").is_file())
            self.assertTrue((output / "metrics" / "ranking.csv").is_file())
            self.assertTrue((output / "metrics" / "calibration.csv").is_file())
            self.assertTrue((output / "metrics" / "robustness_runs.csv").is_file())
            self.assertTrue((output / "metrics" / "robustness_aggregate.csv").is_file())
            self.assertTrue((output / "metrics" / "leave_one_source_out.csv").is_file())
            self.assertTrue((output / "paper_macros.tex").is_file())
            self.assertTrue((output / "figures" / "campaign_metrics.png").is_file())
            persisted = json.loads((output / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["cigma"]["node_f1"], persisted["cigma"]["node_f1"])
            for key in ["node_f1", "b3_f1", "edge_f1", "ranking_ndcg", "edge_brier"]:
                self.assertGreaterEqual(float(summary["cigma"][key]), 0.0)
                self.assertLessEqual(float(summary["cigma"][key]), 1.0)
            self.assertNotIn("runtime_seconds", summary["cigma"])
            self.assertEqual(summary["robustness"]["total_runs"], 384)
            self.assertEqual(summary["robustness"]["scenario_runs"], 128)
            self.assertEqual(summary["robustness"]["leave_one_source_out_runs"], 6)
            with (output / "metrics" / "robustness_runs.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                robustness_rows = list(csv.DictReader(handle))
                self.assertEqual(len(robustness_rows), 384)
                self.assertTrue(all("runtime_seconds" not in row for row in robustness_rows))
            with (output / "metrics" / "robustness_aggregate.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                aggregate_rows = list(csv.DictReader(handle))
                self.assertEqual(len(aggregate_rows), 120)
                self.assertEqual({int(row["n"]) for row in aggregate_rows}, {32})
            with (output / "metrics" / "statistics.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                statistics_rows = list(csv.DictReader(handle))
                self.assertEqual(len(statistics_rows), 72)
                self.assertFalse(
                    any(
                        row["analysis"] == "paired_cigma_difference"
                        and float(row["observation_dropout"]) == 0.0
                        for row in statistics_rows
                    )
                )
            with (output / "metrics" / "leave_one_source_out.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 6)
            manifest = json.loads(
                (output / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertIn(
                "scripts/evaluate_llm_runs.py", manifest["implementation_files"]
            )
            self.assertFalse(
                any(path.startswith("results/llm/") for path in manifest["files"])
            )
            macros = (output / "paper_macros.tex").read_text(encoding="utf-8")
            self.assertIn("\\CigmaNDCGFive", macros)
            self.assertIn("\\CigmaCriticalMissRate", macros)
        finally:
            if output.exists():
                shutil.rmtree(output)


if __name__ == "__main__":
    unittest.main()
