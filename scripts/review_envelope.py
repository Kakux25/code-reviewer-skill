#!/usr/bin/env python3
"""Gate 2: code-reviewer output -> shared ReviewEnvelope.

Converts one graded battery review into a schema-valid assurance case
fragment: claim C1 (review meets its frozen answer key) mirrors the
mechanical grade; evidence carries review text, grade detail, executed
suite, and git state via Gate 1 collectors. A single reviewer can never
ACCEPT alone: decision is always INSUFFICIENT_EVIDENCE with all seven
reviewers required.

Usage:
    python3 scripts/review_envelope.py --case a --review <file>
        --run-id <id> --out <case.json>
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
import grader

MODULES = shared.MODULES
UNVERIFIED_EXPOSURE = shared.UNVERIFIED_EXPOSURE


def build_case(case, review_path, run_id, out_path=None, producer=None,
               exposure_notes=None, criteria_first=False):
    """producer/exposure/criteria timing are caller assertions: the adapter
    observes files and grades, never review process. Defaults plead
    ignorance; pass explicit values only when you can defend them."""
    casedir = REPO / "tests" / "review-cases" / ("case-%s" % case)
    key_path = casedir / "answer-key.json"
    key = json.loads(key_path.read_text(encoding="utf-8"))
    review_path = Path(review_path)
    text = review_path.read_text(encoding="utf-8")
    graded = grader.grade_case(case, text, key)
    passed = graded["pass"]
    context_id = "battery-case-%s" % case
    base_rev = "fixture:%s:base@%s" % (case, shared.dir_hash(casedir / "base")) \
        if (casedir / "base").is_dir() else "fixture:%s:no-base" % case
    cand_rev = "fixture:%s:candidate@%s" % (case, shared.dir_hash(casedir / "candidate")) \
        if (casedir / "candidate").is_dir() else "fixture:%s:no-candidate" % case
    scope = {"base_revision": base_rev, "candidate_revision": cand_rev,
             "context_id": context_id, "operation": "integration",
             "risk_class": "low"}

    grade_detail = json.dumps(graded["checks"], sort_keys=True)
    suite_dir = casedir / "tests"
    if suite_dir.is_dir():
        suite = gate1.collect_unittest(suite_dir, extra_env={
            "PYTHONPATH": str(casedir / "candidate"),
            "PYTHONDONTWRITEBYTECODE": "1"})
        ran = [ln for ln in suite["content"].splitlines()
               if ln.startswith("Ran ")]
        ran_note = ran[0] if ran else "NO Ran LINE (collection suspect)"
        first = suite["content"].splitlines()[0] if suite["content"] else "no output"
        suite_ev = shared.ev("E-%s-suite" % case, "suite: %s (%s)" % (first, ran_note),
                       str(suite_dir), "unittest discover (Gate 1 collector)",
                       cand_rev, context_id, "executed acceptance behavior",
                       "exit code only; full output truncated", "dynamic",
                       suite["content_hash"])
    else:
        suite_ev = shared.ev("E-%s-suite" % case,
                       "no suite declared (key suite.expected=absent)",
                       str(casedir), "key inspection", cand_rev, context_id,
                       "absence is designed, not missing evidence",
                       "no dynamic observation possible", "static",
                       shared.sha("absent"))
    git = gate1.collect_git(str(REPO))
    ev_review = shared.ev("E-%s-review" % case,
                    "review text (%d lines)" % (len(text.splitlines())),
                    str(review_path), "read", cand_rev, context_id,
                    "mechanical grading input",
                    "lexical proxy (thresholds.json notes)", "static",
                    shared.sha(text))
    ev_grade = shared.ev("E-%s-grade" % case,
                   "grade pass=%s (decision ok=%s)" % (
                       passed, graded["checks"]["decision"]["ok"]),
                   "grader.py", "mechanical grading vs frozen answer key",
                   cand_rev, context_id, "key conformance verdict",
                   "lexical proxy, not semantic verification", "static",
                   shared.sha(grade_detail))
    ev_git = shared.ev("E-%s-git" % case,
                 "repo HEAD observed (%s)" % git["status"],
                 str(REPO), "git rev-parse/status (Gate 1 collector)",
                 cand_rev, context_id, "revision context",
                 "dirty state recorded, not resolved", "static",
                 git["content_hash"])
    claim_id = "C1-%s" % case
    grade_id = ev_grade["id"]
    claim = {
        "id": claim_id,
        "statement": "Code review of battery case %s meets its frozen answer key" % case,
        "warrant": "mechanical grading (grader.py) against frozen answer-key.json; claim mirrors grade pass",
        "independence_notes": "single instrument; lexical proxy, not semantic verification",
        "assumptions": ["mechanical grading is a lexical proxy (thresholds.json notes)"],
        "supporting_evidence": [grade_id] if passed else [],
        "counterevidence": [] if passed else [grade_id],
        "defeaters": [],
        "dependencies": [],
        "residual_doubts": [],
        "scope": scope,
        "status": "supported" if passed else "defeated",
    }
    skill_sha = shared.sha((REPO / "skills" / "code-reviewer" / "SKILL.md").read_bytes())
    uncertainty = {
        "id": "U1-%s" % case,
        "missing_fact": "semantic finding content beyond the lexical grade",
        "consequence": "envelope carries grade conformance only",
        "owner": "code-reviewer",
        "next_action": "semantic finding extraction (Phase 2 judge)",
        "blocking": False,
        "status": "open",
    }
    acase = shared.assemble(
        module="code-reviewer", short="code", case_tag=case,
        claim=claim, evidence=[ev_review, ev_grade, suite_ev, ev_git],
        uncertainties=[uncertainty], scope=scope,
        rubric_version=shared.sha(key_path.read_bytes()),
        exposure_notes=exposure_notes,
        status_rationale="mechanical conversion complete",
        criteria=["answer-key.json", "thresholds.json"], run_id=run_id,
        producer=producer, prompt_digest=skill_sha,
        criteria_before_candidate=criteria_first)
    if out_path is not None:
        Path(out_path).write_text(json.dumps(acase, indent=2) + "\n",
                                  encoding="utf-8")
    return acase


def main(argv=None):
    ap = argparse.ArgumentParser(description="code-reviewer envelope adapter")
    ap.add_argument("--case", required=True)
    ap.add_argument("--review", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model-family", default="unknown")
    ap.add_argument("--model-version", default="unknown")
    ap.add_argument("--exposure-notes", default=None)
    ap.add_argument("--criteria-first", action="store_true",
                    help="caller asserts keys frozen before scored runs")
    args = ap.parse_args(argv)
    build_case(args.case, args.review, args.run_id, out_path=args.out,
               producer={"model_family": args.model_family,
                         "model_version": args.model_version},
               exposure_notes=args.exposure_notes,
               criteria_first=args.criteria_first)
    print("envelope written: %s" % args.out)


if __name__ == "__main__":
    main()
