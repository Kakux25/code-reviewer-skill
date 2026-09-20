#!/usr/bin/env python3
"""Gate 2: code-reviewer output -> shared ReviewEnvelope (stdlib only,
except the jsonschema-backed assurance validator it checks against).

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
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "evals"))
import evidence as gate1
import grader
from validate_assurance import validate

MODULES = ["code-reviewer", "architecture-reviewer",
           "system-dynamics-reviewer", "safety-stpa-reviewer",
           "incident-memory", "sociotechnical-reviewer",
           "final-engineering-judge"]


def _utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _dir_hash(path):
    """Deterministic content hash of a directory tree."""
    acc = hashlib.sha256()
    for child in sorted(Path(path).rglob("*")):
        if child.is_file() and "__pycache__" not in child.parts:
            acc.update(str(child.relative_to(path)).encode("utf-8"))
            acc.update(b"\0")
            acc.update(child.read_bytes())
            acc.update(b"\0")
    return acc.hexdigest()[:16]


def _ev(id, observation, artifact, method, revision, context_id,
        applicability, limitations, kind, digest):
    return {
        "id": id,
        "observation": observation,
        "artifact": artifact,
        "method": method,
        "collected_at": _utcnow(),
        "revision": revision,
        "context_id": context_id,
        "applicability": applicability,
        "limitations": [limitations],
        "kind": kind,
        "integrity": "verified",
        "digest": digest,
    }


UNVERIFIED_EXPOSURE = ("caller did not assert review conditions; "
                           "blindness and rubric timing not verified for this input")


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
    base_rev = "fixture:%s:base@%s" % (case, _dir_hash(casedir / "base")) \
        if (casedir / "base").is_dir() else "fixture:%s:no-base" % case
    cand_rev = "fixture:%s:candidate@%s" % (case, _dir_hash(casedir / "candidate")) \
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
        suite_ev = _ev("E-%s-suite" % case, "suite: %s (%s)" % (first, ran_note),
                       str(suite_dir), "unittest discover (Gate 1 collector)",
                       cand_rev, context_id, "executed acceptance behavior",
                       "exit code only; full output truncated", "dynamic",
                       suite["content_hash"])
    else:
        suite_ev = _ev("E-%s-suite" % case,
                       "no suite declared (key suite.expected=absent)",
                       str(casedir), "key inspection", cand_rev, context_id,
                       "absence is designed, not missing evidence",
                       "no dynamic observation possible", "static",
                       _sha("absent"))
    git = gate1.collect_git(str(REPO))
    ev_review = _ev("E-%s-review" % case,
                    "review text (%d lines)" % (text.count("\n") + 1),
                    str(review_path), "read", cand_rev, context_id,
                    "mechanical grading input",
                    "lexical proxy (thresholds.json notes)", "static",
                    _sha(text))
    ev_grade = _ev("E-%s-grade" % case,
                   "grade pass=%s (decision ok=%s)" % (
                       passed, graded["checks"]["decision"]["ok"]),
                   "grader.py", "mechanical grading vs frozen answer key",
                   cand_rev, context_id, "key conformance verdict",
                   "lexical proxy, not semantic verification", "static",
                   _sha(grade_detail))
    ev_git = _ev("E-%s-git" % case,
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
    skill_sha = _sha((REPO / "skills" / "code-reviewer" / "SKILL.md").read_bytes())
    producer = producer or {}
    envelope = {
        "id": "R-%s-code" % case,
        "rubric_version": _sha(key_path.read_bytes()),
        "exposure_notes": exposure_notes or UNVERIFIED_EXPOSURE,
        "status_rationale": "mechanical conversion complete",
        "criteria": ["answer-key.json", "thresholds.json"],
        "shared_context": [context_id],
        "evidence": [e["id"] for e in (ev_review, ev_grade, suite_ev, ev_git)],
        "claims": [claim_id],
        "findings": [],
        "missing_evidence": [],
        "schema_version": "0.1.0",
        "module": "code-reviewer",
        "scope": scope,
        "criteria_before_candidate": bool(criteria_first),
        "producer": {"model_family": producer.get("model_family", "unknown"),
                     "model_version": producer.get("model_version", "unknown"),
                     "prompt_digest": producer.get("prompt_digest", skill_sha),
                     "session_id": run_id},
        "status": "complete",
    }
    uncertainty = {
        "id": "U1-%s" % case,
        "missing_fact": "semantic finding content beyond the lexical grade",
        "consequence": "envelope carries grade conformance only",
        "owner": "code-reviewer",
        "next_action": "semantic finding extraction (Phase 2 judge)",
        "blocking": False,
        "status": "open",
    }
    acase = {
        "id": "AC-%s-%s" % (case, run_id),
        "top_claim": claim_id,
        "rationale": "single-reviewer conversion; six specialists missing",
        "required_reviewers": MODULES,
        "conditions": [],
        "evidence": [ev_review, ev_grade, suite_ev, ev_git],
        "claims": [claim],
        "findings": [],
        "defeaters": [],
        "uncertainties": [uncertainty],
        "causal_links": [],
        "incident_cases": [],
        "safety_constraints": [],
        "reviews": [envelope],
        "schema_version": "0.1.0",
        "scope": scope,
        "decision": "INSUFFICIENT_EVIDENCE",
        "authorization": "not_granted",
    }
    validate(acase)
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
