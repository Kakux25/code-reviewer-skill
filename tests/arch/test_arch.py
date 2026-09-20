"""Gate 3: architecture-reviewer fixtures + envelope adapter.

Integrity: every arch fixture ships request + repo + candidate + expected
verdict contract. Adapter: human grade + review text -> valid assurance
fragment whose C2 claim mirrors the grade (human grade is the
measurement instrument here: no mechanical key exists for architecture
judgment, so expected.json is the frozen answer key).
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "evals"))

CASES = REPO / "tests" / "arch-cases"
IDS = ["a", "b", "c", "d"]

EXPECTED_KEYS = {"case", "kind", "verdict", "must_cite", "must_state",
                 "must_not_claim", "rationale"}
KINDS = {"negative", "gold", "abstention", "adversarial"}
VERDICTS = {"conforms", "violates", "uncertain"}


class FixtureIntegrity(unittest.TestCase):
    def test_every_case_has_request_repo_candidate_expected(self):
        for i in IDS:
            d = CASES / ("arch-%s" % i)
            self.assertTrue((d / "request.md").is_file(), i)
            self.assertTrue((d / "repo").is_dir(), i)
            self.assertTrue((d / "candidate").is_dir(), i)
            self.assertTrue((d / "expected.json").is_file(), i)

    def test_expected_schema(self):
        for i in IDS:
            exp = json.loads((CASES / ("arch-%s" % i) /
                              "expected.json").read_text(encoding="utf-8"))
            self.assertEqual(set(exp), EXPECTED_KEYS, i)
            self.assertEqual(exp["case"], "arch-%s" % i)
            self.assertIn(exp["kind"], KINDS, i)
            self.assertIn(exp["verdict"], VERDICTS, i)
            for k in ("must_cite", "must_state", "must_not_claim"):
                self.assertIsInstance(exp[k], list, (i, k))
                self.assertTrue(exp[k], (i, k))

    def test_kinds_cover_gate_criteria(self):
        kinds = {json.loads((CASES / ("arch-%s" % i) / "expected.json")
                            .read_text(encoding="utf-8"))["kind"] for i in IDS}
        self.assertEqual(kinds, KINDS)


class AdapterContract(unittest.TestCase):
    def _build(self, case, verdict):
        import arch_envelope
        from validate_assurance import validate
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", prefix="review-arch-%s-" % case,
            delete=False, encoding="utf-8")
        tmp.write("stub review for %s grade %s" % (case, verdict))
        tmp.close()
        review = Path(tmp.name)
        self.addCleanup(review.unlink)
        grade = {"verdict": verdict, "grader": "unit-test"}
        acase = arch_envelope.build_case(case, str(review), grade,
                                         run_id="unit")
        validate(acase)  # raises unless schema-valid
        return acase

    def test_conforms_maps_to_supported(self):
        acase = self._build("a", "conforms")
        claim = acase["claims"][0]
        self.assertEqual(claim["id"], "C2-a")
        self.assertEqual(claim["status"], "supported")
        self.assertEqual(len(claim["supporting_evidence"]), 1)
        self.assertEqual(claim["counterevidence"], [])
        self.assertIn("arch-a", claim["statement"])

    def test_violates_maps_to_defeated(self):
        acase = self._build("b", "violates")
        claim = acase["claims"][0]
        self.assertEqual(claim["status"], "defeated")
        self.assertEqual(claim["supporting_evidence"], [])
        self.assertEqual(len(claim["counterevidence"]), 1)

    def test_uncertain_maps_to_unresolved(self):
        acase = self._build("c", "uncertain")
        claim = acase["claims"][0]
        self.assertEqual(claim["status"], "unresolved")

    def test_claim_is_about_candidate_conformance(self):
        # P1 fix: status mirrors the graded verdict, so the claim must be
        # about the CANDIDATE (conforms), not about review-vs-expected
        # match (all grades match, yet b/d are defeated).
        acase = self._build("b", "violates")
        self.assertIn("Candidate arch-b", acase["claims"][0]["statement"])

    def test_single_reviewer_never_accepts(self):
        acase = self._build("a", "conforms")
        self.assertEqual(acase["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(acase["authorization"], "not_granted")
        self.assertEqual(len(acase["required_reviewers"]), 7)

    def test_evidence_covers_review_grade_repo(self):
        acase = self._build("d", "violates")
        roles = {e["artifact"] for e in acase["evidence"]}
        self.assertTrue(any("review-arch-d" in a for a in roles))
        self.assertTrue(any(a == "expected.json" for a in roles))
        self.assertTrue(any("arch-d" in a for a in roles))


class FrozenRun(unittest.TestCase):
    RUN = REPO / "evals" / "runs" / "arch-smoke"

    def test_grades_match_expected(self):
        grades = json.loads((self.RUN / "grades.json").read_text(
            encoding="utf-8"))["grades"]
        for i in IDS:
            exp = json.loads((CASES / ("arch-%s" % i) / "expected.json")
                             .read_text(encoding="utf-8"))
            self.assertEqual(grades[i]["verdict"], exp["verdict"], i)
            self.assertTrue(grades[i]["matches_expected"], i)

    def test_frozen_envelopes_validate_and_mirror(self):
        from validate_assurance import validate
        grades = json.loads((self.RUN / "grades.json").read_text(
            encoding="utf-8"))["grades"]
        want = {"conforms": "supported", "violates": "defeated",
                "uncertain": "unresolved"}
        for i in IDS:
            acase = json.loads((self.RUN / "envelopes" / ("%s.json" % i))
                               .read_text(encoding="utf-8"))
            validate(acase)
            self.assertEqual(acase["claims"][0]["status"],
                             want[grades[i]["verdict"]], i)
            self.assertEqual(acase["decision"], "INSUFFICIENT_EVIDENCE", i)

    def test_declared_suites_executed_green(self):
        # P2 fix: a frozen envelope must never record exit!=0 for a
        # declared suite (arch-a recorded exit=1 from a cwd-fragile
        # fixture test while the review claimed 2/2 pass).
        for i in IDS:
            acase = json.loads((self.RUN / "envelopes" / ("%s.json" % i))
                               .read_text(encoding="utf-8"))
            suite = [e for e in acase["evidence"]
                     if e["id"].endswith("suite")][0]
            if i == "c":
                self.assertEqual(suite["kind"], "static", i)
            else:
                self.assertEqual(suite["kind"], "dynamic", i)
                self.assertIn("exit=0", suite["observation"], i)


if __name__ == "__main__":
    unittest.main()
