from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import yaml

from cigma.benchmark import generate_benchmark


ARTIFACT_ROOT = Path(__file__).resolve().parents[1]


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = yaml.safe_load(
            (ARTIFACT_ROOT / "configs" / "default.yaml").read_text(encoding="utf-8")
        )

    def test_generation_is_deterministic(self) -> None:
        first = generate_benchmark(self.config)
        second = generate_benchmark(self.config)
        self.assertEqual(first, second)

    def test_six_source_families_and_separate_oracle(self) -> None:
        public, oracle = generate_benchmark(self.config)
        self.assertEqual(set(public["metadata"]["sources"]), {"tls", "pki", "code", "cicd", "cmdb", "ot"})
        public_text = json.dumps(public, sort_keys=True)
        self.assertNotIn("entity_observation_map", public_text)
        self.assertNotIn("claim_observation_map", public_text)
        self.assertIn("entity_observation_map", oracle)
        self.assertIn("claim_observation_map", oracle)

    def test_every_observation_has_verifiable_evidence(self) -> None:
        public, _ = generate_benchmark(self.config)
        for record in public["entities"] + public["claims"]:
            evidence = record["evidence"]
            actual = hashlib.sha256(evidence["excerpt"].encode("utf-8")).hexdigest()
            self.assertEqual(actual, evidence["raw_sha256"])
            self.assertTrue(evidence["locator"])

    def test_certificate_key_size_matches_rsa_algorithm_identifier(self) -> None:
        public, _ = generate_benchmark(self.config)
        entities = {item["observation_id"]: item for item in public["entities"]}
        for claim in public["claims"]:
            if claim["predicate"] != "USES":
                continue
            subject = entities[claim["subject_observation_id"]]
            obj = entities[claim["object_observation_id"]]
            key_bits = subject.get("attributes", {}).get("key_bits")
            algorithm_id = obj.get("identifiers", {}).get("algorithm_id", "")
            if subject["entity_type"] == "certificate" and key_bits is not None and algorithm_id.startswith("RSA-"):
                self.assertEqual(int(key_bits), int(algorithm_id.removeprefix("RSA-")))


if __name__ == "__main__":
    unittest.main()
