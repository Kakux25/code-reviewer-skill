"""Gate 5: incident-memory case base + retrieval + envelope adapter.

Retrieval proposes (deterministic weighted scoring over structured
fields), judgment disposes (the skill may override ranking when the
mechanism does not transfer). Redaction is structural: restricted
fields never appear in public rendering.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "evals"))

CASES = REPO / "tests" / "incident-cases"
IDS = ["a", "b", "c", "d"]

EXPECTED_KEYS = {"case", "kind", "verdict", "must_cite", "must_state",
                 "must_not_claim", "rationale"}
KINDS = {"negative", "gold", "abstention", "adversarial"}
VERDICTS = {"blocked", "clear", "nomatch"}
CASE_KEYS = {"id", "title", "mechanism", "context", "failure", "lesson",
             "applies_when", "not_when", "restricted"}


class FixtureIntegrity(unittest.TestCase):
    def test_every_case_has_query_candidate_expected(self):
        for i in IDS:
            d = CASES / ("mem-%s" % i)
            self.assertTrue((d / "query.md").is_file(), i)
            self.assertTrue((d / "candidate").is_dir(), i)
            self.assertTrue((d / "expected.json").is_file(), i)

    def test_expected_schema(self):
        for i in IDS:
            exp = json.loads((CASES / ("mem-%s" % i) /
                              "expected.json").read_text(encoding="utf-8"))
            self.assertEqual(set(exp), EXPECTED_KEYS, i)
            self.assertEqual(exp["case"], "mem-%s" % i)
            self.assertIn(exp["kind"], KINDS, i)
            self.assertIn(exp["verdict"], VERDICTS, i)
            for k in ("must_cite", "must_state", "must_not_claim"):
                self.assertIsInstance(exp[k], list, (i, k))
                self.assertTrue(exp[k], (i, k))

    def test_kinds_cover_gate_criteria(self):
        kinds = {json.loads((CASES / ("mem-%s" % i) / "expected.json")
                            .read_text(encoding="utf-8"))["kind"] for i in IDS}
        self.assertEqual(kinds, KINDS)

    def test_case_base_schema(self):
        base = sorted((CASES / "cases").glob("*.json"))
        self.assertGreaterEqual(len(base), 3)
        for f in base:
            case = json.loads(f.read_text(encoding="utf-8"))
            self.assertEqual(set(case), CASE_KEYS, f.name)
            for k in ("mechanism", "context", "applies_when", "not_when"):
                self.assertIsInstance(case[k], list, (f.name, k))
                self.assertTrue(case[k], (f.name, k))


class RetrievalContract(unittest.TestCase):
    def test_scoring_is_deterministic(self):
        import incident_memory as mem
        q = {"tags": ["retry", "http"], "text": "client retries hammering"}
        s1 = mem.ranked(CASES / "cases", q)
        s2 = mem.ranked(CASES / "cases", q)
        self.assertEqual(s1, s2)
        self.assertTrue(all(isinstance(s, (int, float)) for _, s in s1))

    def test_mechanism_outweighs_context(self):
        import incident_memory as mem
        # Same context words, mechanism decides the order.
        q = {"tags": ["cache"], "text": "cache stampede synchronized expiry"}
        ranked = mem.ranked(CASES / "cases", q)
        self.assertEqual(ranked[0][0], "INC-002")

    def test_exact_scores_pinned(self):
        # P2 fix: exact scores on the recorded live queries, so any
        # weight regression (e.g. swapped 1/3) fails loudly.
        import incident_memory as mem
        qa = {"tags": ["retry", "payments"],
              "text": "payments client now retries failed charges in a "
                      "tight loop with no backoff, jitter, or breaker"}
        self.assertEqual(mem.ranked(CASES / "cases", qa), [("INC-001", 8)])
        qb = {"tags": ["pool", "overload", "cache"],
              "text": "raise DB connection pool from 20 to 200 backend "
                      "overload during traffic spikes cache hit rate dropped"}
        self.assertEqual(mem.ranked(CASES / "cases", qb),
                         [("INC-002", 5), ("INC-001", 4)])

    def test_no_match_returns_empty(self):
        import incident_memory as mem
        q = {"tags": ["css"], "text": "button color theme palette"}
        self.assertEqual(mem.ranked(CASES / "cases", q), [])

    def test_public_rendering_strips_restricted(self):
        import incident_memory as mem
        for f in sorted((CASES / "cases").glob("*.json")):
            case = json.loads(f.read_text(encoding="utf-8"))
            pub = mem.render_public(case)
            self.assertNotIn("restricted", pub)
            blob = json.dumps(pub)
            for secret in case["restricted"]:
                self.assertNotIn(secret, blob, f.name)


class AdapterContract(unittest.TestCase):
    def _build(self, case, verdict):
        import memory_envelope
        from validate_assurance import validate
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", prefix="review-mem-%s-" % case,
            delete=False, encoding="utf-8")
        tmp.write("stub review for %s grade %s" % (case, verdict))
        tmp.close()
        review = Path(tmp.name)
        self.addCleanup(review.unlink)
        grade = {"verdict": verdict, "grader": "unit-test"}
        acase = memory_envelope.build_case(case, str(review), grade,
                                           run_id="unit")
        validate(acase)  # raises unless schema-valid
        return acase

    def test_blocked_maps_to_defeated(self):
        acase = self._build("a", "blocked")
        claim = acase["claims"][0]
        self.assertEqual(claim["id"], "C4-a")
        self.assertEqual(claim["status"], "defeated")
        self.assertEqual(claim["supporting_evidence"], [])
        self.assertEqual(len(claim["counterevidence"]), 1)
        self.assertIn("Candidate mem-a", claim["statement"])

    def test_clear_maps_to_supported(self):
        acase = self._build("d", "clear")
        claim = acase["claims"][0]
        self.assertEqual(claim["status"], "supported")
        self.assertEqual(len(claim["supporting_evidence"]), 1)
        self.assertEqual(claim["counterevidence"], [])

    def test_nomatch_maps_to_unresolved(self):
        acase = self._build("c", "nomatch")
        claim = acase["claims"][0]
        self.assertEqual(claim["status"], "unresolved")

    def test_single_reviewer_never_accepts(self):
        acase = self._build("a", "blocked")
        self.assertEqual(acase["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(acase["authorization"], "not_granted")
        self.assertEqual(len(acase["required_reviewers"]), 7)

    def test_evidence_covers_review_grade_casebase(self):
        acase = self._build("b", "clear")
        arts = {e["artifact"] for e in acase["evidence"]}
        self.assertTrue(any("review-mem-b" in a for a in arts))
        self.assertTrue(any(a == "expected.json" for a in arts))
        self.assertTrue(any("incident-cases" in a for a in arts))


class FrozenRun(unittest.TestCase):
    RUN = REPO / "evals" / "runs" / "memory-smoke"

    def test_grades_match_expected(self):
        grades = json.loads((self.RUN / "grades.json").read_text(
            encoding="utf-8"))["grades"]
        for i in IDS:
            exp = json.loads((CASES / ("mem-%s" % i) / "expected.json")
                             .read_text(encoding="utf-8"))
            self.assertEqual(grades[i]["verdict"], exp["verdict"], i)
            self.assertTrue(grades[i]["matches_expected"], i)

    def test_frozen_envelopes_validate_and_mirror(self):
        from validate_assurance import validate
        grades = json.loads((self.RUN / "grades.json").read_text(
            encoding="utf-8"))["grades"]
        want = {"blocked": "defeated", "clear": "supported",
                "nomatch": "unresolved"}
        for i in IDS:
            acase = json.loads((self.RUN / "envelopes" / ("%s.json" % i))
                               .read_text(encoding="utf-8"))
            validate(acase)
            self.assertEqual(acase["claims"][0]["status"],
                             want[grades[i]["verdict"]], i)
            self.assertEqual(acase["decision"], "INSUFFICIENT_EVIDENCE", i)


if __name__ == "__main__":
    unittest.main()
