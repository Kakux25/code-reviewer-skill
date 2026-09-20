"""K-2: independent second grading agreement.

Every smoke cell (20) and study cell (22) was first-graded K=1 by
the fixture author. K-2 adds one independent second grade per cell
(LLM agents blind to grades.json, reading review + key only).
These tests pin addendum integrity against the FROZEN runs (not
against k2-grades.json itself): full coverage, agreement
recomputed from frozen firsts via the protocol rule, adjudicated
means recomputed, RUN numbers pinned, raw outputs preserved with
a blindness tripwire, and documented adjudication of every
disagreement. Disagreements never rewrite frozen runs.
"""
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN = REPO / "evals" / "runs" / "k2-agreement"
RUNS = REPO / "evals" / "runs"

SMOKE = {"arch-smoke": ["a", "b", "c", "d"],
         "stpa-smoke": ["a", "b", "c", "d"],
         "memory-smoke": ["a", "b", "c", "d"],
         "dynamics-smoke": ["a", "b", "c", "d"],
         "socio-smoke": ["a", "b", "c", "d"]}
STUDY = (["%s-%s" % (c, a) for c in
          ["code", "arch", "stpa", "mem", "dyn", "soc"]
          for a in ["A", "B", "C"]] +
         ["abs-stpa-A", "abs-stpa-B", "abs-socio-A", "abs-socio-B"])
TOL = 0.34


def k2_cells():
    return json.loads((RUN / "k2-grades.json").read_text(
        encoding="utf-8"))["cells"]


def frozen(run, name="grades.json"):
    return json.loads((RUNS / run / name).read_text(encoding="utf-8"))


class K2Integrity(unittest.TestCase):
    def test_protocol_present(self):
        proto = (RUN / "PROTOCOL.md").read_text(encoding="utf-8")
        self.assertIn("Blind to `grades.json` by instruction", proto)
        self.assertIn("Post-hoc amendments", proto)
        self.assertTrue((RUN / "RUN.md").is_file())

    def test_full_coverage(self):
        cells = k2_cells()
        want = {"%s/%s" % (r, c) for r, subs in SMOKE.items()
                for c in subs}
        want |= {"abcd-study/%s" % c for c in STUDY}
        self.assertEqual(set(cells), want)
        self.assertEqual(len(cells), 42)

    def test_cell_schema(self):
        for cell, g in k2_cells().items():
            for k in ("second_verdict_correct", "second_substance",
                      "second_false_claim", "agree", "notes"):
                self.assertIn(k, g, cell)
            self.assertIsInstance(g["second_verdict_correct"], bool, cell)
            self.assertIsInstance(g["second_false_claim"], bool, cell)
            self.assertIsInstance(g["agree"], bool, cell)
            self.assertGreaterEqual(g["second_substance"], 0.0, cell)
            self.assertLessEqual(g["second_substance"], 1.0, cell)
            self.assertTrue(g["notes"], cell)

    def test_study_agree_recomputed_from_frozen(self):
        cells = k2_cells()
        firsts = frozen("abcd-study")["grades"]
        n = 0
        for c in STUDY:
            g = cells["abcd-study/%s" % c]
            f = firsts[c]
            expect = (g["second_verdict_correct"] == f["verdict_correct"]
                      and abs(g["second_substance"] - f["substance"]) <= TOL
                      and g["second_false_claim"] == f["false_claim"])
            self.assertEqual(g["agree"], expect, c)
            n += g["agree"]
        self.assertEqual(n, 18)

    def test_smoke_premise_in_frozen_files(self):
        cells = k2_cells()
        for run, subs in SMOKE.items():
            firsts = frozen(run)["grades"]
            for c in subs:
                f = firsts[c]
                self.assertTrue(f["matches_expected"], "%s/%s" % (run, c))
                self.assertTrue(f["notes"], "%s/%s" % (run, c))
                g = cells["%s/%s" % (run, c)]
                self.assertTrue(g["second_verdict_correct"])
                self.assertEqual(g["second_substance"], 1.0)
                self.assertFalse(g["second_false_claim"])
                self.assertTrue(g["agree"])

    def test_raw_outputs_preserved_and_blind(self):
        cells = k2_cells()
        for cell in cells:
            raw = RUN / "seconds" / (cell.replace("/", "_") + ".md")
            self.assertTrue(raw.is_file(), cell)
            text = raw.read_text(encoding="utf-8")
            self.assertGreater(len(text), 200, cell)
            self.assertNotIn("matches_expected", text, cell)
            self.assertNotIn("grades.json", text, cell)

    def test_disagreements_adjudicated(self):
        dis = {cell: g for cell, g in k2_cells().items() if not g["agree"]}
        self.assertEqual(len(dis), 4)
        for cell, g in dis.items():
            self.assertIn("adjudication", g, cell)
            adj = g["adjudication"]
            for k in ("upheld", "corrected_reading",
                      "corrected_substance", "impact"):
                self.assertIn(k, adj, cell)
            self.assertIn(adj["upheld"], ("first", "second", "neither"),
                          cell)
            self.assertGreaterEqual(adj["corrected_substance"], 0.0, cell)
            self.assertLessEqual(adj["corrected_substance"], 1.0, cell)
            self.assertTrue(adj["corrected_reading"], cell)
            self.assertTrue(adj["impact"], cell)

    def test_adjudicated_means(self):
        cells = k2_cells()
        firsts = frozen("abcd-study")["grades"]
        for arm in ("A", "B"):
            arm_cells = (["code-%s" % arm, "arch-%s" % arm, "stpa-%s" % arm,
                          "mem-%s" % arm, "dyn-%s" % arm, "soc-%s" % arm,
                          "abs-stpa-%s" % arm, "abs-socio-%s" % arm])
            vals = [cells["abcd-study/%s" % c].get(
                "adjudication", {}).get("corrected_substance",
                                        firsts[c]["substance"])
                    for c in arm_cells]
            self.assertAlmostEqual(sum(vals) / 8, 0.77, places=2,
                                   msg="arm %s: %r" % (arm, vals))

    def test_run_numbers_pinned(self):
        run = (RUN / "RUN.md").read_text(encoding="utf-8")
        for token in ("38/42", "0.77", "0.7712", "0.83", "37/42"):
            self.assertIn(token, run)

    def test_agreement_recomputes(self):
        k2 = json.loads((RUN / "k2-grades.json").read_text(
            encoding="utf-8"))
        agree = sum(1 for g in k2["cells"].values() if g["agree"])
        self.assertEqual(k2["agreement"]["cells"], 42)
        self.assertEqual(k2["agreement"]["agree"], agree)
        self.assertAlmostEqual(k2["agreement"]["rate"], agree / 42)


if __name__ == "__main__":
    unittest.main()
