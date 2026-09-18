from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ARTIFACT_ROOT = Path(__file__).resolve().parents[1]
REVISION_ROOT = ARTIFACT_ROOT.parent
FROZEN_MACROS_SHA256 = (
    "47c8802139ece17db9851052779c71be3af9d5ce8273caa9fb17c16e97290847"
)


class PaperMacroExportTests(unittest.TestCase):
    def test_export_matches_checked_paper_and_covers_used_result_macros(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            generated = Path(directory) / "results_macros.tex"
            subprocess.run(
                [
                    sys.executable,
                    str(ARTIFACT_ROOT / "scripts/export_paper_macros.py"),
                    "--default-results",
                    str(ARTIFACT_ROOT / "results/default"),
                    "--llm-results",
                    str(ARTIFACT_ROOT / "results/llm/evaluation"),
                    "--output",
                    str(generated),
                ],
                check=True,
                cwd=ARTIFACT_ROOT,
            )
            generated_bytes = generated.read_bytes()
            self.assertEqual(
                hashlib.sha256(generated_bytes).hexdigest(),
                FROZEN_MACROS_SHA256,
            )
            checked = REVISION_ROOT / "paper/results_macros.tex"
            if checked.exists():
                self.assertEqual(generated_bytes, checked.read_bytes())

            generated_text = generated.read_text(encoding="utf-8")
            self.assertIn(
                r"\newcommand{\CigmaCalibrationCases}{36}", generated_text
            )
            self.assertIn(
                r"\newcommand{\CigmaCalibrationPositives}{34}", generated_text
            )
            names = re.findall(r"\\newcommand\{\\([A-Za-z]+)\}", generated_text)
            self.assertEqual(len(names), len(set(names)))
            main_path = REVISION_ROOT / "paper/main.tex"
            if not main_path.exists():
                return
            main_text = main_path.read_text(encoding="utf-8")
            result_prefixes = (
                "Cigma", "LLM", "TLS", "CBOM", "Union", "Exact", "NoAlias",
                "NoPaths", "NoGate", "Uniform", "Weighted", "RankAgg", "Drop",
                "Without", "Bootstrap", "Permutation",
            )
            used = set(re.findall(r"\\([A-Za-z]+)", main_text))
            missing = sorted(
                name
                for name in used
                if name.startswith(result_prefixes) and name not in set(names)
            )
            self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
