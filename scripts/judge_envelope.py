#!/usr/bin/env python3
"""Judge envelope: final-engineering-judge verdict -> fragment.

Converts one independent judge verdict on an assembled assurance
case into a schema-valid fragment: claim C7 (assembly decision is
sound, per independent judge verdict) mirrors the verdict
(concur->supported, dissent->defeated, abstain->unresolved). The
verdict record (written reasons per docs/assurance/judge-protocol.md)
is the measurement instrument. The fragment carries the assembly's
own scope so a concur fragment merges back for a full-loop decision.
A single reviewer can never ACCEPT alone.

Usage:
    python3 scripts/judge_envelope.py --assembly <asm.json>
        --verdict-file <reasons.md> --verdict '{"verdict": "concur"}'
        --tag <name> --run-id <id> --out <case.json>
"""
import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "evals"))
import envelope as shared
import evidence as gate1

STATUS = {"concur": "supported", "dissent": "defeated",
          "abstain": "unresolved"}


def build_case(assembly_path, verdict_path, verdict, tag, run_id,
               out_path=None, producer=None, exposure_notes=None,
               criteria_first=False):
    """verdict is a caller-asserted judge verdict dict {"verdict": ...};
    the adapter observes files, never judging process."""
    assembly_path = Path(assembly_path)
    assembly = json.loads(assembly_path.read_text(encoding="utf-8"))
    verdict_path = Path(verdict_path)
    text = verdict_path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("empty verdict: reasons are mandatory (R5)")
    v = verdict["verdict"]
    if v not in STATUS:
        raise ValueError("unknown judge verdict: %r" % v)
    status = STATUS[v]
    scope = assembly["scope"]
    context_id = scope["context_id"]
    asm_rev = "assembly:%s@%s" % (assembly_path.name,
                                  shared.sha(assembly_path.read_bytes())[:16])

    verdict_detail = json.dumps({"verdict": verdict,
                                 "assembly_decision": assembly["decision"],
                                 "assembly_id": assembly["id"]}, sort_keys=True)
    ev_assembly = shared.ev(
        "E7-%s-assembly" % tag,
        "assembly decision=%s (%d defeaters)" % (
            assembly["decision"], len(assembly["defeaters"])),
        str(assembly_path), "read", asm_rev, context_id,
        "verdict input", "frozen bytes; judge read this file",
        "static", shared.sha(assembly_path.read_bytes()))
    ev_verdict = shared.ev(
        "E7-%s-verdict" % tag,
        "judge verdict=%s (%d lines of reasons)" % (
            v, len(text.splitlines())),
        str(verdict_path), "read", asm_rev, context_id,
        "verdict record", "free text; reasons are the instrument",
        "static", shared.sha(verdict_detail + "\n" + text))
    git = gate1.collect_git(str(REPO))
    ev_git = shared.ev(
        "E7-%s-git" % tag, "repo HEAD observed (%s)" % git["status"],
        str(REPO), "git rev-parse/status (Gate 1 collector)",
        asm_rev, context_id, "revision context",
        "dirty state recorded, not resolved", "static",
        git["content_hash"])
    claim_id = "C7-%s" % tag
    verdict_id = ev_verdict["id"]
    claim = {
        "id": claim_id,
        "statement": "Assembly decision for %s is sound (per independent judge verdict)" % context_id,
        "warrant": "independent verdict with written reasons per judge-protocol.md; claim mirrors verdict",
        "independence_notes": "judge read the frozen assembly; single judge (K=1)",
        "assumptions": ["judge applies judge-protocol.md norms faithfully"],
        "supporting_evidence": [verdict_id] if status == "supported" else [],
        "counterevidence": [verdict_id] if status == "defeated" else [],
        "defeaters": [],
        "dependencies": [],
        "residual_doubts": [],
        "scope": scope,
        "status": status,
    }
    proto_sha = shared.sha((REPO / "docs" / "assurance" /
                            "judge-protocol.md").read_bytes())
    uncertainty = {
        "id": "U7-%s" % tag,
        "missing_fact": "second-judge agreement on this verdict",
        "consequence": "claim rests on one judge (K=1)",
        "owner": "final-engineering-judge",
        "next_action": "second independent verdict",
        "blocking": False,
        "status": "open",
    }
    acase = shared.assemble(
        module="final-engineering-judge", short="judge", case_tag=tag,
        claim=claim, evidence=[ev_assembly, ev_verdict, ev_git],
        uncertainties=[uncertainty], scope=scope,
        rubric_version=proto_sha,
        exposure_notes=exposure_notes,
        status_rationale="mechanical conversion complete",
        criteria=["judge-protocol.md"], run_id=run_id, producer=producer,
        prompt_digest=proto_sha, criteria_before_candidate=criteria_first)
    if out_path is not None:
        Path(out_path).write_text(json.dumps(acase, indent=2) + "\n",
                                  encoding="utf-8")
    return acase


def main(argv=None):
    ap = argparse.ArgumentParser(description="judge envelope adapter")
    ap.add_argument("--assembly", required=True)
    ap.add_argument("--verdict-file", required=True)
    ap.add_argument("--verdict", required=True,
                    help='judge verdict JSON, e.g. {"verdict": "concur"}')
    ap.add_argument("--tag", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model-family", default="unknown")
    ap.add_argument("--model-version", default="unknown")
    ap.add_argument("--exposure-notes", default=None)
    ap.add_argument("--criteria-first", action="store_true",
                    help="caller asserts protocol read before assembly judged")
    args = ap.parse_args(argv)
    build_case(args.assembly, args.verdict_file, json.loads(args.verdict),
               args.tag, args.run_id, out_path=args.out,
               producer={"model_family": args.model_family,
                         "model_version": args.model_version},
               exposure_notes=args.exposure_notes,
               criteria_first=args.criteria_first)
    print("envelope written: %s" % args.out)


if __name__ == "__main__":
    main()
