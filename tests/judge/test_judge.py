"""Judge envelope: final-engineering-judge verdicts -> fragments.

The judge renders an independent verdict on an assembled assurance
case (concur/dissent/abstain) with written reasons, following
docs/assurance/judge-protocol.md. Claim C7 (assembly decision is
sound) mirrors the verdict: concur->supported, dissent->defeated,
abstain->unresolved. The judge fragment carries the assembly's own
scope, so a concur fragment merges back for a full-loop decision.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "evals"))

RUN = REPO / "evals" / "runs" / "judge-demo"
VERDICTS = {"concur", "dissent", "abstain"}


class AdapterContract(unittest.TestCase):
    def _build(self, verdict, tag="probe"):
        import judge_envelope
        from validate_assurance import validate
        assembly = RUN / "inputs" / "accept.json"
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", prefix="judge-verdict-",
            delete=False, encoding="utf-8")
        tmp.write("stub verdict %s" % verdict)
        tmp.close()
        record = Path(tmp.name)
        self.addCleanup(record.unlink)
        acase = judge_envelope.build_case(
            str(assembly), str(record), {"verdict": verdict}, tag,
            run_id="unit")
        validate(acase)  # raises unless schema-valid
        return acase

    def test_concur_maps_to_supported(self):
        acase = self._build("concur")
        claim = acase["claims"][0]
        self.assertEqual(claim["id"], "C7-probe")
        self.assertEqual(claim["status"], "supported")
        self.assertEqual(len(claim["supporting_evidence"]), 1)
        self.assertEqual(claim["counterevidence"], [])
        self.assertIn("Assembly", claim["statement"])

    def test_dissent_maps_to_defeated(self):
        acase = self._build("dissent")
        claim = acase["claims"][0]
        self.assertEqual(claim["status"], "defeated")
        self.assertEqual(claim["supporting_evidence"], [])
        self.assertEqual(len(claim["counterevidence"]), 1)

    def test_abstain_maps_to_unresolved(self):
        acase = self._build("abstain")
        claim = acase["claims"][0]
        self.assertEqual(claim["status"], "unresolved")

    def test_unknown_verdict_raises(self):
        import judge_envelope
        with self.assertRaises(ValueError):
            self._build("maybe")

    def test_empty_verdict_raises(self):
        # Protocol R5: a verdict without reasons is not a verdict.
        import judge_envelope
        from validate_assurance import validate
        assembly = RUN / "inputs" / "accept.json"
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", prefix="judge-verdict-empty-",
            delete=False, encoding="utf-8")
        tmp.write("   \n")
        tmp.close()
        record = Path(tmp.name)
        self.addCleanup(record.unlink)
        with self.assertRaises(ValueError):
            judge_envelope.build_case(
                str(assembly), str(record), {"verdict": "concur"},
                "empty", run_id="unit")

    def test_single_reviewer_never_accepts(self):
        acase = self._build("concur")
        self.assertEqual(acase["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(acase["authorization"], "not_granted")
        self.assertEqual(len(acase["required_reviewers"]), 7)

    def test_evidence_covers_assembly_verdict(self):
        acase = self._build("dissent")
        arts = {e["artifact"] for e in acase["evidence"]}
        self.assertTrue(any("accept.json" in a for a in arts))
        self.assertTrue(any("judge-verdict-" in a for a in arts))

    def test_scope_follows_assembly(self):
        import judge_envelope
        assembly = json.loads((RUN / "inputs" / "accept.json").read_text(
            encoding="utf-8"))
        acase = self._build("concur")
        self.assertEqual(acase["scope"], assembly["scope"])
        self.assertEqual(acase["claims"][0]["scope"], assembly["scope"])


class FrozenDemo(unittest.TestCase):
    def test_verdicts_frozen(self):
        for v in ("concur-defeated", "concur-refusal", "dissent-accept",
                  "concur-accept2"):
            p = RUN / "verdicts" / ("%s.md" % v)
            self.assertTrue(p.is_file(), v)
            self.assertGreater(len(p.read_text(encoding="utf-8")), 200, v)

    def test_fragments_validate_and_mirror(self):
        from validate_assurance import validate
        want = {"concur-defeated": "supported", "concur-refusal": "supported",
                "dissent-accept": "defeated", "concur-accept2": "supported"}
        for v, status in want.items():
            acase = json.loads((RUN / "fragments" / ("%s.json" % v))
                               .read_text(encoding="utf-8"))
            validate(acase)
            self.assertEqual(acase["claims"][0]["status"], status, v)
            self.assertEqual(acase["decision"], "INSUFFICIENT_EVIDENCE", v)

    def test_full_loop_one_assumption_away(self):
        # Honest ceiling: the judge claim carries the K=1 assumption
        # (like every human-grade claim), so the loop lands exactly
        # one named assumption from ACCEPT — everything else clean.
        from validate_assurance import validate
        acase = json.loads((RUN / "final-loop.json").read_text(
            encoding="utf-8"))
        validate(acase)
        self.assertEqual(acase["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(len(acase["defeaters"]), 1)
        self.assertIn("assumption",
                      acase["defeaters"][0]["statement"].lower())
        top = [c for c in acase["claims"] if c["id"] == "CTOP"][0]
        self.assertEqual(top["status"], "unresolved")
        mods = {r["module"] for r in acase["reviews"]}
        self.assertIn("final-engineering-judge", mods)
        subs = [c for c in acase["claims"] if c["id"] != "CTOP"]
        self.assertTrue(all(c["status"] == "supported" for c in subs))

    def test_dissent_blocks_loop(self):
        import assemble
        ok1 = json.loads((RUN / "inputs" / "ok1.json").read_text(
            encoding="utf-8"))
        ok2 = json.loads((RUN / "inputs" / "ok2.json").read_text(
            encoding="utf-8"))
        dis = json.loads((RUN / "fragments" / "dissent-accept.json")
                         .read_text(encoding="utf-8"))
        out = assemble.assemble(
            [ok1, ok2, dis],
            required_reviewers=["code-reviewer", "architecture-reviewer",
                                "final-engineering-judge"])
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")
        c7 = [c for c in out["claims"] if c["id"].startswith("C7-")][0]
        self.assertEqual(c7["status"], "defeated")


if __name__ == "__main__":
    unittest.main()
