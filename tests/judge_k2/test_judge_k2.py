"""Judge K-2 stability: independent re-run of the K-1 validation set.

K-1 measured judge-vs-hand agreement once (95/96 = 0.990, K=1, no
stability data). K-2 re-runs all 16 reviews with the identical
frozen instrument and scores replication (K2 vs gold, same 0.75
gate) plus stability (K1 vs K2 exact). These tests pin run
integrity: coverage, clean records, both reports recomputed from
the frozen inputs, and the pinned RUN headlines. K-1 files are
never rewritten.
"""
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "evals"))

RUN = REPO / "evals" / "runs" / "judge-k2-stability"
K1 = REPO / "evals" / "runs" / "2026-09-20-judge-k1"


def manifest_ids():
    jobs = json.loads((K1 / "manifest.json").read_text(encoding="utf-8"))
    return [j["id"] for j in jobs]


class JudgeK2Integrity(unittest.TestCase):
    def test_protocol_present(self):
        proto = (RUN / "PROTOCOL.md").read_text(encoding="utf-8")
        for marker in ("Replication", "Stability", "NEVER",
                       "measurement, not a bar"):
            self.assertIn(marker, proto)
        self.assertTrue((RUN / "RUN.md").is_file())

    def test_full_coverage(self):
        ids = manifest_ids()
        self.assertEqual(len(ids), 16)
        for rid in ids:
            p = RUN / "outputs" / ("%s.json" % rid)
            self.assertTrue(p.is_file(), rid)

    def test_clean_records(self):
        for rid in manifest_ids():
            rec = json.loads((RUN / "outputs" / ("%s.json" % rid)
                              ).read_text(encoding="utf-8"))
            self.assertNotIn("parse_error", rec, rid)
            self.assertNotIn("schema_problems", rec, rid)
            self.assertIn("scores", rec, rid)
            self.assertEqual(rec["attempts"], 1, rid)

    def test_replication_recomputed_from_frozen(self):
        from agreement import gold_items, judge_items
        gold = json.loads((REPO / "evals" / "hand_scores.json"
                           ).read_text(encoding="utf-8"))
        matches = total = 0
        for rid, greview in gold["reviews"].items():
            gitems = gold_items(greview)
            rec = json.loads((RUN / "outputs" / ("%s.json" % rid)
                              ).read_text(encoding="utf-8"))
            jitems = judge_items(rec)
            self.assertIsNotNone(jitems, rid)
            for key, gval in gitems.items():
                total += 1
                matches += (jitems.get(key) == gval)
        recorded = json.loads((RUN / "agreement-k2.json").read_text(
            encoding="utf-8"))
        self.assertEqual(recorded["matches"], matches)
        self.assertEqual(recorded["total"], total)
        self.assertEqual((matches, total), (96, 96))
        self.assertTrue(recorded["gate_met"])
        self.assertEqual(recorded["gate"], 0.75)

    def test_stability_recomputed_from_frozen(self):
        from agreement import gold_items, judge_items
        gold = json.loads((REPO / "evals" / "hand_scores.json"
                           ).read_text(encoding="utf-8"))
        matches = total = 0
        diffs = []
        for rid, greview in gold["reviews"].items():
            gitems = gold_items(greview)
            r1 = json.loads((K1 / "outputs" / ("%s.json" % rid)
                             ).read_text(encoding="utf-8"))
            r2 = json.loads((RUN / "outputs" / ("%s.json" % rid)
                             ).read_text(encoding="utf-8"))
            j1, j2 = judge_items(r1), judge_items(r2)
            for key in gitems:
                total += 1
                if j1 is not None and j2 is not None and \
                        j1.get(key) == j2.get(key):
                    matches += 1
                else:
                    diffs.append((rid, key))
        recorded = json.loads((RUN / "stability-k1-k2.json").read_text(
            encoding="utf-8"))
        self.assertEqual(recorded["matches"], matches)
        self.assertEqual(recorded["total"], total)
        self.assertEqual((matches, total), (95, 96))
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0][0], "with-b")

    def test_run_headline_pinned(self):
        text = (RUN / "RUN.md").read_text(encoding="utf-8")
        for marker in ("96/96 = 1.000", "95/96 = 0.990", "with-b",
                       "c52a045", "REPLICATES"):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
