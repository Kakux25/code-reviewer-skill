"""K-3: independent third-grade tie-break of the 4 K-2 disagreements.

Every K-2 dispute (all study abstention probes, all substance
magnitudes) was adjudicated by the first-grade operator. K-3 adds
one blind headless third grade per disputed cell under the
pre-registered strict rule. These tests pin addendum integrity:
coverage, raw-transcription fidelity, exact-match recomputation
against the FROZEN study + K-2 files, the blindness tripwire,
and the pinned RUN headline. Thirds never rewrite frozen runs.
"""
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN = REPO / "evals" / "runs" / "k3-tiebreak"
FENCE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)
CELLS = ["abs-stpa-A", "abs-socio-A", "abs-stpa-B", "abs-socio-B"]


def k3_cells():
    return json.loads((RUN / "k3-grades.json").read_text(
        encoding="utf-8"))["cells"]


def raw_third(cell):
    text = (RUN / "thirds" / ("abcd-study_%s.md" % cell)).read_text(
        encoding="utf-8")
    return json.loads(FENCE.search(text).group(1))


class K3Integrity(unittest.TestCase):
    def test_protocol_present(self):
        proto = (RUN / "PROTOCOL.md").read_text(encoding="utf-8")
        for marker in ("tie-break evidence", "NEVER rewritten",
                       "tripwire test", "EXACT (no tolerance)"):
            self.assertIn(marker, proto)
        self.assertTrue((RUN / "RUN.md").is_file())
        for cell in CELLS:
            self.assertTrue(
                (RUN / "prompts" / ("abcd-study_%s.md" % cell)).is_file(),
                cell)

    def test_full_coverage(self):
        cells = k3_cells()
        self.assertEqual(set(cells),
                         {"abcd-study/%s" % c for c in CELLS})
        self.assertEqual(len(cells), 4)

    def test_cell_schema(self):
        for cell, g in k3_cells().items():
            for k in ("third_verdict_correct", "third_substance",
                      "third_false_claim", "matches_first",
                      "matches_second", "matches_adjudicated", "notes"):
                self.assertIn(k, g, cell)
            for k in ("third_verdict_correct", "third_false_claim",
                      "matches_first", "matches_second",
                      "matches_adjudicated"):
                self.assertIsInstance(g[k], bool, "%s/%s" % (cell, k))
            self.assertIn(g["third_substance"], (0.0, 0.5, 1.0), cell)
            self.assertTrue(g["notes"], cell)

    def test_thirds_transcribed_from_raw(self):
        for cell in CELLS:
            raw = raw_third(cell)
            g = k3_cells()["abcd-study/%s" % cell]
            self.assertEqual(g["third_verdict_correct"],
                             bool(raw["verdict_correct"]), cell)
            self.assertEqual(g["third_substance"],
                             float(raw["substance"]), cell)
            self.assertEqual(g["third_false_claim"],
                             bool(raw["false_claim"]), cell)

    def test_matches_recomputed_from_frozen(self):
        cells = k3_cells()
        firsts = json.loads((REPO / "evals" / "runs" / "abcd-study" /
                             "grades.json").read_text(
                                 encoding="utf-8"))["grades"]
        k2 = json.loads((REPO / "evals" / "runs" / "k2-agreement" /
                         "k2-grades.json").read_text(
                             encoding="utf-8"))["cells"]
        n_adj = 0
        for cell in CELLS:
            g = cells["abcd-study/%s" % cell]
            t = (g["third_verdict_correct"], g["third_substance"],
                 g["third_false_claim"])
            f = firsts[cell]
            ft = (f["verdict_correct"], float(f["substance"]),
                  f["false_claim"])
            s = k2["abcd-study/%s" % cell]
            st = (s["second_verdict_correct"],
                  float(s["second_substance"]), s["second_false_claim"])
            adj = s["adjudication"]
            at = (st[0], float(adj["corrected_substance"]), st[2])
            self.assertEqual(g["matches_first"], t == ft, cell)
            self.assertEqual(g["matches_second"], t == st, cell)
            self.assertEqual(g["matches_adjudicated"], t == at, cell)
            n_adj += g["matches_adjudicated"]
        self.assertEqual(n_adj, 4)
        agree = json.loads((RUN / "k3-grades.json").read_text(
            encoding="utf-8"))["agreement"]
        self.assertEqual(agree, {"cells": 4, "match_adjudicated": 4})

    def test_tripwire_no_grades_content(self):
        for cell in CELLS:
            raw = (RUN / "thirds" / ("abcd-study_%s.md" % cell)
                   ).read_text(encoding="utf-8")
            for token in ("grades.json", "k2-grades", "adjudicat",
                          "upheld"):
                self.assertNotIn(token, raw.lower(), cell)

    def test_run_headline_pinned(self):
        text = (RUN / "RUN.md").read_text(encoding="utf-8")
        for marker in ("4/4 match adjudicated", "A 0.77, B 0.77, C 1.00",
                       "CLOSED for", "b73000a"):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
