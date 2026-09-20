"""Gate 9: A/B/C/D study artifact integrity.

The study is a frozen empirical run, not code: these tests pin its
pre-registered protocol compliance (cases x arms present, grades
reference frozen reviews, verdicts in vocabulary, D assembly
decisions recorded). They do not re-judge review quality.
"""
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

RUN = REPO / "evals" / "runs" / "abcd-study"
CASES = ["code", "arch", "stpa", "mem", "dyn", "soc"]
PROBES = ["abs-stpa", "abs-socio"]
ARMS = ["A", "B", "C"]


class StudyIntegrity(unittest.TestCase):
    def test_protocol_present(self):
        proto = (RUN / "PROTOCOL.md").read_text(encoding="utf-8")
        self.assertTrue((RUN / "RUN.md").is_file())
        for marker in ("pre-registered", "INSUFFICIENT_EVIDENCE",
                       "single-reviewer-never-accepts"):
            self.assertIn(marker, proto)

    def test_all_cells_have_frozen_reviews(self):
        for case in CASES:
            for arm in ARMS:
                p = RUN / "reviews" / ("%s-%s.md" % (case, arm))
                self.assertTrue(p.is_file(), p.name)
                self.assertGreater(len(p.read_text(encoding="utf-8")), 200,
                                   p.name)
        for probe in PROBES:
            for arm in ["A", "B"]:
                p = RUN / "reviews" / ("%s-%s.md" % (probe, arm))
                self.assertTrue(p.is_file(), p.name)

    def test_grades_cover_all_cells(self):
        grades = json.loads((RUN / "grades.json").read_text(
            encoding="utf-8"))["grades"]
        want = {"%s-%s" % (c, a) for c in CASES for a in ARMS}
        want |= {"%s-%s" % (p, a) for p in PROBES for a in ["A", "B"]}
        self.assertEqual(set(grades), want)
        for cell, g in grades.items():
            for k in ("verdict_correct", "substance", "false_claim", "notes"):
                self.assertIn(k, g, cell)
            self.assertIsInstance(g["verdict_correct"], bool, cell)
            self.assertIsInstance(g["false_claim"], bool, cell)
            self.assertGreaterEqual(g["substance"], 0.0, cell)
            self.assertLessEqual(g["substance"], 1.0, cell)
            self.assertTrue(g["notes"], cell)

    def test_d_arm_recorded(self):
        d = json.loads((RUN / "grades.json").read_text(encoding="utf-8"))["D"]
        self.assertEqual(set(d), {"fragments_valid", "assembly_decision",
                                  "assembly_defeaters", "notes"})
        self.assertTrue(d["fragments_valid"])
        self.assertTrue(d["assembly_defeaters"] >= 1)


if __name__ == "__main__":
    unittest.main()
