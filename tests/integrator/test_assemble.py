"""Gate 8: assurance integrator (assemble + defeaters).

The integrator is deterministic: it judges structure, not substance.
ACCEPT requires coverage + scope agreement + all claims supported and
closed + verified evidence + no blocking doubts + no confirmed
findings. Anything else yields INSUFFICIENT_EVIDENCE with one
blocking defeater per reason. Structural merge failures (scope
mismatch, id collision, dependency cycle) yield a refusal case that
carries no fragment items, never a crash.
"""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "evals"))

SCOPE = {"base_revision": "base@1", "candidate_revision": "cand@1",
         "context_id": "chg-1", "operation": "integration",
         "risk_class": "low"}


def _ev(i, digest, scope):
    return {"id": i, "observation": "obs %s" % i, "artifact": "art",
            "method": "m", "collected_at": "2026-09-20T00:00:00+00:00",
            "revision": "r", "context_id": scope["context_id"],
            "applicability": "a", "limitations": ["l"], "kind": "static",
            "integrity": "verified", "digest": digest}


def _claim(i, status, scope, ev_ids, **kw):
    c = {"id": i, "statement": "s", "warrant": "w",
         "independence_notes": "n", "assumptions": [],
         "supporting_evidence": list(ev_ids) if status == "supported" else [],
         "counterevidence": list(ev_ids) if status == "defeated" else [],
         "defeaters": [], "dependencies": [], "residual_doubts": [],
         "scope": copy.deepcopy(scope), "status": status}
    c.update(kw)
    return c


def frag(module, claim_status="supported", scope=None, digest="d"):
    """Minimal valid single-reviewer fragment via the shared skeleton."""
    import envelope as shared
    scope = copy.deepcopy(scope or SCOPE)
    tag = "%s-%s" % (module[:3], claim_status[:3])
    ev = _ev("E-%s" % tag,
             hashlib.sha256(("%s-%s" % (digest, module)).encode()).hexdigest()
             if digest != "same" else hashlib.sha256(b"same").hexdigest(),
             scope)
    claim = _claim("C-%s" % tag, claim_status, scope, [ev["id"]])
    return shared.assemble(
        module=module, short="t", case_tag=tag, claim=claim,
        evidence=[ev], uncertainties=[], scope=scope,
        rubric_version="r", exposure_notes=None,
        status_rationale="s", criteria=["c"], run_id="u",
        producer={}, prompt_digest="p")


class AssemblyContract(unittest.TestCase):
    def test_accept_when_complete(self):
        import assemble
        out = assemble.assemble(
            [frag("code-reviewer"), frag("architecture-reviewer")],
            required_reviewers=["code-reviewer", "architecture-reviewer"])
        self.assertEqual(out["decision"], "ACCEPT")
        self.assertEqual(out["authorization"], "not_granted")
        top = [c for c in out["claims"] if c["id"] == "CTOP"][0]
        self.assertEqual(top["status"], "supported")
        self.assertEqual(out["top_claim"], "CTOP")

    def test_missing_reviewer_blocks(self):
        import assemble
        out = assemble.assemble(
            [frag("code-reviewer")],
            required_reviewers=["code-reviewer", "architecture-reviewer"])
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(out["authorization"], "not_granted")
        self.assertTrue(any("architecture-reviewer" in d["statement"]
                            for d in out["defeaters"]))
        self.assertTrue(all(d["blocking"] for d in out["defeaters"]))

    def test_defeated_claim_blocks(self):
        import assemble
        out = assemble.assemble(
            [frag("code-reviewer"), frag("architecture-reviewer", "defeated")],
            required_reviewers=["code-reviewer", "architecture-reviewer"])
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")
        top = [c for c in out["claims"] if c["id"] == "CTOP"][0]
        self.assertEqual(top["status"], "defeated")

    def test_unresolved_claim_blocks_without_defeat(self):
        import assemble
        out = assemble.assemble(
            [frag("code-reviewer", "unresolved")],
            required_reviewers=["code-reviewer"])
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")
        top = [c for c in out["claims"] if c["id"] == "CTOP"][0]
        self.assertEqual(top["status"], "unresolved")

    def test_shared_evidence_counted_once(self):
        import assemble
        f1 = frag("code-reviewer", digest="same")
        f2 = frag("architecture-reviewer", digest="same")
        out = assemble.assemble(
            [f1, f2],
            required_reviewers=["code-reviewer", "architecture-reviewer"])
        digests = [e["digest"] for e in out["evidence"]]
        self.assertEqual(len(digests), len(set(digests)))
        self.assertEqual(out["decision"], "ACCEPT")

    def test_cycle_blocks_without_crash(self):
        import assemble
        f1 = frag("code-reviewer")
        f2 = frag("architecture-reviewer")
        c1 = f1["claims"][0]["id"]
        c2 = f2["claims"][0]["id"]
        f1["claims"][0]["dependencies"] = [c2]
        f2["claims"][0]["dependencies"] = [c1]
        out = assemble.assemble(
            [f1, f2],
            required_reviewers=["code-reviewer", "architecture-reviewer"])
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertTrue(any("cycle" in d["statement"].lower()
                            for d in out["defeaters"]))

    def test_scope_mismatch_refuses_merge(self):
        import assemble
        other = copy.deepcopy(SCOPE)
        other["candidate_revision"] = "cand@2"
        out = assemble.assemble(
            [frag("code-reviewer"), frag("architecture-reviewer",
                                         scope=other)],
            required_reviewers=["code-reviewer", "architecture-reviewer"])
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual([c["id"] for c in out["claims"]], ["CTOP"])
        self.assertEqual(out["reviews"], [])
        self.assertTrue(any("scope" in d["statement"].lower()
                            for d in out["defeaters"]))

    def test_assumption_blocks_accept(self):
        import assemble
        f = frag("code-reviewer")
        f["claims"][0]["assumptions"] = ["human grader faithful"]
        out = assemble.assemble([f], required_reviewers=["code-reviewer"])
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertTrue(any("assumption" in d["statement"].lower()
                            for d in out["defeaters"]))

    def test_blocking_uncertainty_blocks(self):
        import assemble
        f = frag("code-reviewer")
        f["uncertainties"] = [{
            "id": "U-x", "missing_fact": "m", "consequence": "c",
            "owner": "o", "next_action": "n", "blocking": True,
            "status": "open"}]
        out = assemble.assemble([f], required_reviewers=["code-reviewer"])
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")

    def test_confirmed_finding_blocks(self):
        import assemble
        f = frag("code-reviewer")
        ev = f["evidence"][0]["id"]
        f["uncertainties"] = [{
            "id": "U-x", "missing_fact": "m", "consequence": "c",
            "owner": "o", "next_action": "n", "blocking": False,
            "status": "open"}]
        f["findings"] = [{
            "id": "F-x", "claim_id": f["claims"][0]["id"],
            "criterion_id": "c", "trigger": "t",
            "expected_invariant": "e", "observed_or_inferred": "o",
            "consequence": "q", "evidence": [ev],
            "refutation": {"procedure": "p", "attempted": True,
                           "result": "survived", "evidence": [ev]},
            "uncertainty": ["U-x"], "priority": "P1", "status": "confirmed"}]
        out = assemble.assemble([f], required_reviewers=["code-reviewer"])
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")

    def test_empty_input_refuses(self):
        import assemble
        out = assemble.assemble([], required_reviewers=["code-reviewer"])
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(out["top_claim"], "CTOP")

    def test_default_requires_all_seven(self):
        import assemble
        import envelope as shared
        out = assemble.assemble([frag("code-reviewer")])
        self.assertEqual(out["required_reviewers"], shared.MODULES)
        self.assertEqual(len(shared.MODULES), 7)
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")

    def test_output_always_validates(self):
        import assemble
        from validate_assurance import validate
        cases = [
            [frag("code-reviewer"), frag("architecture-reviewer")],
            [frag("code-reviewer", "defeated")],
            [],
        ]
        for fs in cases:
            mods = [r["module"] for f in fs for r in f["reviews"]]
            validate(assemble.assemble(fs, required_reviewers=mods or ["x"]))

    def _defeater(self, f, blocking=False):
        return {"id": "D-x-%s" % f["claims"][0]["id"], "claim_id": f["claims"][0]["id"],
                "statement": "s", "investigation": "i",
                "evidence": [f["evidence"][0]["id"]],
                "blocking": blocking, "status": "unresolved"}

    def test_defeater_evidence_aliased_across_dedupe(self):
        import assemble
        f1 = frag("code-reviewer", digest="same")
        f2 = frag("architecture-reviewer", digest="same")
        f2["defeaters"] = [self._defeater(f2)]
        out = assemble.assemble(
            [f1, f2],
            required_reviewers=["code-reviewer", "architecture-reviewer"])
        self.assertEqual(out["decision"], "ACCEPT")
        kept = {e["id"] for e in out["evidence"]}
        for d in out["defeaters"]:
            self.assertTrue(set(d["evidence"]) <= kept, d["id"])

    def test_causal_evidence_aliased_across_dedupe(self):
        import assemble
        f1 = frag("code-reviewer", digest="same")
        f2 = frag("architecture-reviewer", digest="same")
        f2["causal_links"] = [{
            "id": "L-x", "source_variable": "a", "target_variable": "b",
            "delay": "none", "confidence_basis": "sim",
            "polarity": "positive", "status": "observed",
            "evidence": [f2["evidence"][0]["id"]]}]
        out = assemble.assemble(
            [f1, f2],
            required_reviewers=["code-reviewer", "architecture-reviewer"])
        self.assertEqual(out["decision"], "ACCEPT")

    def test_identical_duplicate_merges_cleanly(self):
        import assemble
        f = frag("code-reviewer")
        out = assemble.assemble([f, f], required_reviewers=["code-reviewer"])
        self.assertEqual(out["decision"], "ACCEPT")
        self.assertEqual(len(out["claims"]), 2)  # subclaim + CTOP

    def test_identifier_collision_refuses(self):
        import assemble
        f1 = frag("code-reviewer")
        f2 = frag("architecture-reviewer")
        f2["evidence"][0]["id"] = f1["evidence"][0]["id"]
        out = assemble.assemble(
            [f1, f2],
            required_reviewers=["code-reviewer", "architecture-reviewer"])
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertTrue(any("collision" in d["statement"].lower()
                            for d in out["defeaters"]))

    def test_reserved_ids_refuse(self):
        import assemble
        f = frag("code-reviewer")
        f["claims"][0]["id"] = "CTOP"
        out = assemble.assemble([f], required_reviewers=["code-reviewer"])
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertTrue(any("reserved" in d["statement"].lower()
                            for d in out["defeaters"]))

    def test_null_digests_never_conflated(self):
        import assemble
        f1 = frag("code-reviewer")
        f2 = frag("architecture-reviewer")
        f1["evidence"][0]["digest"] = None
        f2["evidence"][0]["digest"] = None
        out = assemble.assemble(
            [f1, f2],
            required_reviewers=["code-reviewer", "architecture-reviewer"])
        digests = [e["digest"] for e in out["evidence"]]
        self.assertEqual(digests.count(None), 2)
        self.assertEqual(out["decision"], "ACCEPT")

    def test_ctop_depends_on_subclaims(self):
        import assemble
        out = assemble.assemble(
            [frag("code-reviewer"), frag("architecture-reviewer")],
            required_reviewers=["code-reviewer", "architecture-reviewer"])
        top = [c for c in out["claims"] if c["id"] == "CTOP"][0]
        subs = sorted(c["id"] for c in out["claims"] if c["id"] != "CTOP")
        self.assertEqual(sorted(top["dependencies"]), subs)

    def test_refusal_carries_no_fragment_items(self):
        import assemble
        other = copy.deepcopy(SCOPE)
        other["candidate_revision"] = "cand@2"
        out = assemble.assemble(
            [frag("code-reviewer"), frag("architecture-reviewer",
                                         scope=other)],
            required_reviewers=["code-reviewer", "architecture-reviewer"])
        self.assertEqual([c["id"] for c in out["claims"]], ["CTOP"])
        self.assertEqual([e["id"] for e in out["evidence"]], ["E-ASM"])
        self.assertEqual(out["reviews"], [])
        self.assertEqual(out["findings"], [])
        self.assertEqual(out["causal_links"], [])
        self.assertEqual(out["incident_cases"], [])
        self.assertEqual(out["safety_constraints"], [])

    def test_shared_digest_conflict_refuses_both_orders(self):
        import assemble
        f1 = frag("code-reviewer", digest="same")
        f2 = frag("architecture-reviewer", digest="same")
        f2["evidence"][0]["integrity"] = "unverified"
        for order in ([f1, f2], [f2, f1]):
            out = assemble.assemble(
                order,
                required_reviewers=["code-reviewer",
                                    "architecture-reviewer"])
            self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")
            self.assertTrue(any("digest" in d["statement"].lower()
                                for d in out["defeaters"]))

    def test_causal_collision_refuses(self):
        import assemble
        f1 = frag("code-reviewer")
        f2 = frag("architecture-reviewer")
        for f, target in ((f1, "queue_depth"), (f2, "retry_rate")):
            f["causal_links"] = [{
                "id": "L-x", "source_variable": "load",
                "target_variable": target, "delay": "none",
                "confidence_basis": "sim", "polarity": "positive",
                "status": "observed",
                "evidence": [f["evidence"][0]["id"]]}]
        out = assemble.assemble(
            [f1, f2],
            required_reviewers=["code-reviewer", "architecture-reviewer"])
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertTrue(any("collision" in d["statement"].lower()
                            for d in out["defeaters"]))

    def test_real_fragments_refuse_cross_context_merge(self):
        import assemble
        import glob as g
        paths = sorted(g.glob(str(REPO / "evals" / "runs" / "*-smoke" /
                                  "envelopes" / "*.json")))
        self.assertGreaterEqual(len(paths), 20)
        frags = [json.loads(Path(p).read_text(encoding="utf-8"))
                 for p in paths[:6]]
        out = assemble.assemble(frags)
        self.assertEqual(out["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertTrue(any("scope" in d["statement"].lower()
                            for d in out["defeaters"]))


if __name__ == "__main__":
    unittest.main()
