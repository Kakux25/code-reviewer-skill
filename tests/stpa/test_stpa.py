"""Gate 4: safety-stpa-reviewer fixtures + envelope adapter.

Same harness shape as Gate 3: fixture integrity + adapter mapping
(safe/unsafe/unanalyzable -> supported/defeated/unresolved) with the
claim about the CANDIDATE (P1 lesson), + frozen live run.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "evals"))

CASES = REPO / "tests" / "stpa-cases"
IDS = ["a", "b", "c", "d"]

EXPECTED_KEYS = {"case", "kind", "verdict", "must_cite", "must_state",
                 "must_not_claim", "rationale"}
KINDS = {"negative", "gold", "abstention", "adversarial"}
VERDICTS = {"safe", "unsafe", "unanalyzable"}


class FixtureIntegrity(unittest.TestCase):
    def test_every_case_has_request_repo_candidate_expected(self):
        for i in IDS:
            d = CASES / ("stpa-%s" % i)
            self.assertTrue((d / "request.md").is_file(), i)
            self.assertTrue((d / "repo").is_dir(), i)
            self.assertTrue((d / "candidate").is_dir(), i)
            self.assertTrue((d / "expected.json").is_file(), i)

    def test_expected_schema(self):
        for i in IDS:
            exp = json.loads((CASES / ("stpa-%s" % i) /
                              "expected.json").read_text(encoding="utf-8"))
            self.assertEqual(set(exp), EXPECTED_KEYS, i)
            self.assertEqual(exp["case"], "stpa-%s" % i)
            self.assertIn(exp["kind"], KINDS, i)
            self.assertIn(exp["verdict"], VERDICTS, i)
            for k in ("must_cite", "must_state", "must_not_claim"):
                self.assertIsInstance(exp[k], list, (i, k))
                self.assertTrue(exp[k], (i, k))

    def test_kinds_cover_gate_criteria(self):
        kinds = {json.loads((CASES / ("stpa-%s" % i) / "expected.json")
                            .read_text(encoding="utf-8"))["kind"] for i in IDS}
        self.assertEqual(kinds, KINDS)


class AdapterContract(unittest.TestCase):
    def _build(self, case, verdict):
        import stpa_envelope
        from validate_assurance import validate
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", prefix="review-stpa-%s-" % case,
            delete=False, encoding="utf-8")
        tmp.write("stub review for %s grade %s" % (case, verdict))
        tmp.close()
        review = Path(tmp.name)
        self.addCleanup(review.unlink)
        grade = {"verdict": verdict, "grader": "unit-test"}
        acase = stpa_envelope.build_case(case, str(review), grade,
                                         run_id="unit")
        validate(acase)  # raises unless schema-valid
        return acase

    def test_safe_maps_to_supported(self):
        acase = self._build("c", "safe")
        claim = acase["claims"][0]
        self.assertEqual(claim["id"], "C3-c")
        self.assertEqual(claim["status"], "supported")
        self.assertEqual(len(claim["supporting_evidence"]), 1)
        self.assertEqual(claim["counterevidence"], [])
        self.assertIn("Candidate stpa-c", claim["statement"])

    def test_unsafe_maps_to_defeated(self):
        acase = self._build("a", "unsafe")
        claim = acase["claims"][0]
        self.assertEqual(claim["status"], "defeated")
        self.assertEqual(claim["supporting_evidence"], [])
        self.assertEqual(len(claim["counterevidence"]), 1)

    def test_unanalyzable_maps_to_unresolved(self):
        acase = self._build("d", "unanalyzable")
        claim = acase["claims"][0]
        self.assertEqual(claim["status"], "unresolved")

    def test_single_reviewer_never_accepts(self):
        acase = self._build("c", "safe")
        self.assertEqual(acase["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(acase["authorization"], "not_granted")
        self.assertEqual(len(acase["required_reviewers"]), 7)

    def test_evidence_covers_review_grade_repo(self):
        acase = self._build("a", "unsafe")
        arts = {e["artifact"] for e in acase["evidence"]}
        self.assertTrue(any("review-stpa-a" in a for a in arts))
        self.assertTrue(any(a == "expected.json" for a in arts))
        self.assertTrue(any("stpa-a" in a for a in arts))

    def test_no_suite_means_static_absence_note(self):
        acase = self._build("a", "unsafe")
        suite = [e for e in acase["evidence"]
                 if e["id"].endswith("suite")][0]
        self.assertEqual(suite["kind"], "static")
        self.assertIn("no suite", suite["observation"].lower())


class FrozenRun(unittest.TestCase):
    RUN = REPO / "evals" / "runs" / "stpa-smoke"

    def test_grades_match_expected(self):
        grades = json.loads((self.RUN / "grades.json").read_text(
            encoding="utf-8"))["grades"]
        for i in IDS:
            exp = json.loads((CASES / ("stpa-%s" % i) / "expected.json")
                             .read_text(encoding="utf-8"))
            self.assertEqual(grades[i]["verdict"], exp["verdict"], i)
            self.assertTrue(grades[i]["matches_expected"], i)

    def test_frozen_envelopes_validate_and_mirror(self):
        from validate_assurance import validate
        grades = json.loads((self.RUN / "grades.json").read_text(
            encoding="utf-8"))["grades"]
        want = {"safe": "supported", "unsafe": "defeated",
                "unanalyzable": "unresolved"}
        for i in IDS:
            acase = json.loads((self.RUN / "envelopes" / ("%s.json" % i))
                               .read_text(encoding="utf-8"))
            validate(acase)
            self.assertEqual(acase["claims"][0]["status"],
                             want[grades[i]["verdict"]], i)
            self.assertEqual(acase["decision"], "INSUFFICIENT_EVIDENCE", i)

    def test_frozen_suites_are_absent_by_design(self):
        for i in IDS:
            acase = json.loads((self.RUN / "envelopes" / ("%s.json" % i))
                               .read_text(encoding="utf-8"))
            suite = [e for e in acase["evidence"]
                     if e["id"].endswith("suite")][0]
            self.assertEqual(suite["kind"], "static", i)
            self.assertIn("no suite", suite["observation"].lower(), i)


if __name__ == "__main__":
    unittest.main()
