#!/usr/bin/env python3
"""Gate 4: safety-stpa-reviewer output -> shared ReviewEnvelope.

Converts one human-graded STPA review into a schema-valid assurance
fragment: claim C3 (candidate is free of unhandled unsafe control
actions, per human-graded review) mirrors the graded verdict. The
human grade is the measurement instrument (no mechanical key exists
for safety judgment; expected.json is the frozen answer key). STPA
fixtures are analysis-only: no suites by design. A single reviewer
can never ACCEPT alone.

Usage:
    python3 scripts/stpa_envelope.py --case a --review <file>
        --grade '{"verdict": "unsafe"}' --run-id <id> --out <case.json>
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

STATUS = {"safe": "supported", "unsafe": "defeated",
          "unanalyzable": "unresolved"}


def build_case(case, review_path, grade, run_id, out_path=None,
               producer=None, exposure_notes=None, criteria_first=False):
    """grade is a caller-asserted human grade dict {"verdict": ...};
    the adapter observes files, never review process."""
    casedir = REPO / "tests" / "stpa-cases" / ("stpa-%s" % case)
    key_path = casedir / "expected.json"
    expected = json.loads(key_path.read_text(encoding="utf-8"))
    review_path = Path(review_path)
    text = review_path.read_text(encoding="utf-8")
    verdict = grade["verdict"]
    if verdict not in STATUS:
        raise ValueError("unknown stpa verdict: %r" % verdict)
    status = STATUS[verdict]
    context_id = "stpa-case-%s" % case
    base_rev = "fixture:stpa-%s:repo@%s" % (case, shared.dir_hash(
        casedir / "repo")) if (casedir / "repo").is_dir() \
        else "fixture:stpa-%s:no-repo" % case
    cand_rev = "fixture:stpa-%s:candidate@%s" % (case, shared.dir_hash(
        casedir / "candidate")) if (casedir / "candidate").is_dir() \
        else "fixture:stpa-%s:no-candidate" % case
    scope = {"base_revision": base_rev, "candidate_revision": cand_rev,
             "context_id": context_id, "operation": "integration",
             "risk_class": "low"}

    grade_detail = json.dumps({"grade": grade, "expected": expected},
                              sort_keys=True)
    suite_dir = casedir / "candidate" / "tests"
    if suite_dir.is_dir():
        suite = gate1.collect_unittest(suite_dir, extra_env={
            "PYTHONPATH": str(casedir / "candidate"),
            "PYTHONDONTWRITEBYTECODE": "1"})
        ran = [ln for ln in suite["content"].splitlines()
               if ln.startswith("Ran ")]
        ran_note = ran[0] if ran else "NO Ran LINE (collection suspect)"
        first = suite["content"].splitlines()[0] if suite["content"] else "no output"
        suite_ev = shared.ev(
            "E3-%s-suite" % case, "suite: %s (%s)" % (first, ran_note),
            str(suite_dir), "unittest discover (Gate 1 collector)",
            cand_rev, context_id, "executed acceptance behavior",
            "exit code only; full output truncated", "dynamic",
            suite["content_hash"])
    else:
        suite_ev = shared.ev(
            "E3-%s-suite" % case, "no suite declared (analysis-only fixture)",
            str(casedir), "key inspection", cand_rev, context_id,
            "absence is designed, not missing evidence",
            "no dynamic observation possible", "static",
            shared.sha("absent"))
    ev_review = shared.ev(
        "E3-%s-review" % case,
        "review text (%d lines)" % (len(text.splitlines())),
        str(review_path), "read", cand_rev, context_id,
        "human grading input", "free text; grade is the instrument",
        "static", shared.sha(text))
    ev_grade = shared.ev(
        "E3-%s-grade" % case,
        "human grade verdict=%s (expected %s)" % (
            verdict, expected["verdict"]),
        "expected.json", "human grading vs frozen expected.json",
        cand_rev, context_id, "expected-verdict conformance",
        "single human grader; inter-rater agreement unmeasured",
        "static", shared.sha(grade_detail))
    git = gate1.collect_git(str(REPO))
    ev_git = shared.ev(
        "E3-%s-git" % case, "repo HEAD observed (%s)" % git["status"],
        str(REPO), "git rev-parse/status (Gate 1 collector)",
        cand_rev, context_id, "revision context",
        "dirty state recorded, not resolved", "static",
        git["content_hash"])
    claim_id = "C3-%s" % case
    grade_id = ev_grade["id"]
    claim = {
        "id": claim_id,
        "statement": "Candidate stpa-%s is free of unhandled unsafe control actions (per human-graded review)" % case,
        "warrant": "human grading against frozen expected.json; claim mirrors graded verdict",
        "independence_notes": "single human grader; no mechanical key",
        "assumptions": ["human grader applies expected.json must/must-not faithfully"],
        "supporting_evidence": [grade_id] if status == "supported" else [],
        "counterevidence": [grade_id] if status == "defeated" else [],
        "defeaters": [],
        "dependencies": [],
        "residual_doubts": [],
        "scope": scope,
        "status": status,
    }
    skill_sha = shared.sha((REPO / "skills" / "safety-stpa-reviewer" /
                            "SKILL.md").read_bytes())
    uncertainty = {
        "id": "U3-%s" % case,
        "missing_fact": "second-grader agreement on this review",
        "consequence": "claim rests on one human grade (K=1)",
        "owner": "safety-stpa-reviewer",
        "next_action": "second independent grade",
        "blocking": False,
        "status": "open",
    }
    acase = shared.assemble(
        module="safety-stpa-reviewer", short="stpa", case_tag=case,
        claim=claim, evidence=[ev_review, ev_grade, suite_ev, ev_git],
        uncertainties=[uncertainty], scope=scope,
        rubric_version=shared.sha(key_path.read_bytes()),
        exposure_notes=exposure_notes,
        status_rationale="mechanical conversion complete",
        criteria=["expected.json"], run_id=run_id, producer=producer,
        prompt_digest=skill_sha, criteria_before_candidate=criteria_first)
    if out_path is not None:
        Path(out_path).write_text(json.dumps(acase, indent=2) + "\n",
                                  encoding="utf-8")
    return acase


def main(argv=None):
    ap = argparse.ArgumentParser(description="stpa envelope adapter")
    ap.add_argument("--case", required=True)
    ap.add_argument("--review", required=True)
    ap.add_argument("--grade", required=True,
                    help='human grade JSON, e.g. {"verdict": "unsafe"}')
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model-family", default="unknown")
    ap.add_argument("--model-version", default="unknown")
    ap.add_argument("--exposure-notes", default=None)
    ap.add_argument("--criteria-first", action="store_true",
                    help="caller asserts safety model recorded before candidate examined")
    args = ap.parse_args(argv)
    build_case(args.case, args.review, json.loads(args.grade),
               args.run_id, out_path=args.out,
               producer={"model_family": args.model_family,
                         "model_version": args.model_version},
               exposure_notes=args.exposure_notes,
               criteria_first=args.criteria_first)
    print("envelope written: %s" % args.out)


if __name__ == "__main__":
    main()
