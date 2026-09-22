"""Gate 2: code-reviewer output -> shared ReviewEnvelope.

Gate criterion: existing fixtures plus guard-present, pre-existing-
defect, alias and abstention controls retain expected outcomes, i.e.
envelope claim status == mechanical grade pass for every fixture x
good/bad sample. This change adds guard-present (u) and
pre-existing-defect (v); alias (t) and abstention (c/o) pre-exist and
are covered by the same integration test. The adapter never ACCEPTs
alone: one reviewer is INSUFFICIENT_EVIDENCE by construction.
"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "evals"))
import review_envelope
import grader
import check_integrity
from validate_assurance import validate

MODULES = ["code-reviewer", "architecture-reviewer",
           "system-dynamics-reviewer", "safety-stpa-reviewer",
           "incident-memory", "sociotechnical-reviewer",
           "final-engineering-judge"]


def key_sha(case):
    return hashlib.sha256(
        (REPO / "tests" / "review-cases" / ("case-%s" % case)
         / "answer-key.json").read_bytes()).hexdigest()


class AdapterTest(unittest.TestCase):
    def test_good_sample_supported_and_valid(self):
        review = check_integrity.sample_path("a", "good")
        case = review_envelope.build_case("a", review, "test-run")
        validate(case)
        self.assertEqual(case["claims"][0]["status"], "supported")

    def test_bad_sample_defeated_and_valid(self):
        review = check_integrity.sample_path("a", "bad")
        case = review_envelope.build_case("a", review, "test-run")
        validate(case)
        self.assertEqual(case["claims"][0]["status"], "defeated")

    def test_claim_matches_grade_all_fixtures(self):
        keys_dir = REPO / "tests" / "review-cases"
        for case in grader.discover_cases(keys_dir):
            key = json.loads(
                (keys_dir / ("case-%s" % case)
                 / "answer-key.json").read_text(encoding="utf-8"))
            for kind, want in (("good", "supported"), ("bad", "defeated")):
                with self.subTest(case=case, kind=kind):
                    review = check_integrity.sample_path(case, kind)
                    text = review.read_text(encoding="utf-8")
                    graded = grader.grade_case(case, text, key)["pass"]
                    built = review_envelope.build_case(case, review, "t")
                    validate(built)
                    got = built["claims"][0]["status"]
                    self.assertEqual(got, want)
                    self.assertEqual(graded, want == "supported")

    def test_single_reviewer_never_accepts(self):
        review = check_integrity.sample_path("u", "good")
        case = review_envelope.build_case("u", review, "t")
        self.assertEqual(case["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(case["required_reviewers"], MODULES)
        self.assertEqual(case["authorization"], "not_granted")
        self.assertEqual(case["reviews"][0]["module"], "code-reviewer")
        self.assertEqual(case["reviews"][0]["status"], "complete")

    def test_provenance_defaults_to_ignorance(self):
        review = check_integrity.sample_path("v", "good")
        case = review_envelope.build_case("v", review, "run-42")
        envelope = case["reviews"][0]
        self.assertEqual(envelope["rubric_version"], key_sha("v"))
        self.assertFalse(envelope["criteria_before_candidate"])
        self.assertEqual(envelope["producer"]["session_id"], "run-42")
        self.assertEqual(envelope["producer"]["model_family"], "unknown")
        self.assertEqual(envelope["producer"]["model_version"], "unknown")
        self.assertIn("not verified", envelope["exposure_notes"])

    def test_provenance_round_trips_caller_assertions(self):
        review = check_integrity.sample_path("v", "good")
        case = review_envelope.build_case(
            "v", review, "run-42",
            producer={"model_family": "muse", "model_version": "9.9"},
            exposure_notes="keys frozen; reviewers blind (RUN.md)",
            criteria_first=True)
        envelope = case["reviews"][0]
        self.assertTrue(envelope["criteria_before_candidate"])
        self.assertEqual(envelope["producer"]["model_family"], "muse")
        self.assertEqual(envelope["producer"]["model_version"], "9.9")
        self.assertIn("blind", envelope["exposure_notes"])

    def test_evidence_kinds(self):
        kinds = {}
        suite_obs = {}
        for case in ("a", "c"):
            review = check_integrity.sample_path(case, "good")
            built = review_envelope.build_case(case, review, "t")
            kinds[case] = sorted(e["kind"] for e in built["evidence"])
            suite_obs[case] = [e["observation"] for e in built["evidence"]
                               if e["id"] == "E-%s-suite" % case][0]
        self.assertIn("dynamic", kinds["a"])  # suite executed
        self.assertIn("Ran 2 tests", suite_obs["a"])  # actually ran, not 0-test artifact
        self.assertNotIn("dynamic", kinds["c"])  # suite absent by design
        for case in ("a", "c"):
            self.assertIn("static", kinds[case])  # review text + grade

    def test_writes_file(self):
        review = check_integrity.sample_path("b", "good")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "case.json"
            review_envelope.build_case("b", review, "t", out_path=out)
            validate(json.loads(out.read_text(encoding="utf-8")))

    def test_dir_hash_distinguishes_framing(self):
        import envelope as shared
        with tempfile.TemporaryDirectory() as tmp:
            one, two = Path(tmp) / "one", Path(tmp) / "two"
            one.mkdir()
            two.mkdir()
            (one / "a").write_bytes(b"x\x00b\x00y")
            (two / "a").write_bytes(b"x")
            (two / "b").write_bytes(b"y")
            self.assertNotEqual(shared.dir_hash(one), shared.dir_hash(two))


if __name__ == "__main__":
    unittest.main()
