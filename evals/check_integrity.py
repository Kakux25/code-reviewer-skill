#!/usr/bin/env python3
"""Deterministic integrity gate for the code-reviewer eval harness.

Runs in CI on every push. No LLM calls, no network, no secrets.
Standard library only.

Checks:
  1. Every tests/review-cases/case-*/ has request.md + a schema-valid
     answer-key.json.
  2. Every plant fixture anchor still holds (plants are actually planted,
     controls still describe the fixture) -- guards against fixture rot.
  3. Candidate suites behave as designed: case-a FAILS (defect present),
     case-b and case-d PASS. A failing suite in case-a is the executable
     proof that the planted defect exists.
  4. SKILL.md lint: frontmatter name/description, negative triggers,
     body within the lean budget, referenced files exist.
  5. evals/thresholds.json is valid and declares the suite gate.
  6. Grader self-test: synthetic good reviews pass 4/4, each synthetic
     bad review fails its case. An untested instrument proves nothing.

Usage:  python3 evals/check_integrity.py
Exit code 0 when all checks pass, else 1.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CASES = ("a", "b", "c", "d")
FAILURES = []


def fail(msg):
    FAILURES.append(msg)
    print("FAIL %s" % msg)


def ok(msg):
    print("ok %s" % msg)


def load_key(case):
    path = REPO / "tests" / "review-cases" / ("case-%s" % case) \
        / "answer-key.json"
    return json.loads(path.read_text(encoding="utf-8"))


def check_schema():
    """Step 1: keys exist and validate."""
    required = {"case", "decision", "architecture", "soul",
                "plants", "controls"}
    for case in CASES:
        cdir = REPO / "tests" / "review-cases" / ("case-%s" % case)
        if not (cdir / "request.md").is_file():
            fail("case-%s: missing request.md" % case)
            continue
        try:
            key = load_key(case)
        except (OSError, ValueError) as exc:
            fail("case-%s: unreadable answer-key.json (%s)" % (case, exc))
            continue
        missing = required - set(key)
        if missing:
            fail("case-%s: key missing fields %s" % (case, sorted(missing)))
            continue
        if key["case"] != case:
            fail("case-%s: key case tag %r" % (case, key["case"]))
        for plant in key["plants"]:
            if not plant.get("id") or not plant.get("any_of"):
                fail("case-%s: plant without id/any_of" % case)
            fc = plant.get("fixture_check")
            if fc and "path" not in fc:
                fail("case-%s: plant %s fixture_check without path"
                     % (case, plant.get("id")))
        for control in key["controls"]:
            if control.get("kind") not in ("not_flagged", "forbid_phrase"):
                fail("case-%s: control %s bad kind"
                     % (case, control.get("id")))
        ok("case-%s schema" % case)


def check_anchors():
    """Step 2: fixture anchors hold (plants really planted)."""
    for case in CASES:
        cdir = REPO / "tests" / "review-cases" / ("case-%s" % case)
        try:
            key = load_key(case)
        except (OSError, ValueError):
            continue  # reported in step 1
        for plant in key["plants"]:
            fc = plant.get("fixture_check")
            if not fc:
                continue
            target = cdir / fc["path"]
            pid = plant["id"]
            if not target.is_file():
                fail("case-%s %s: anchor file missing %s"
                     % (case, pid, fc["path"]))
                continue
            text = target.read_text(encoding="utf-8")
            if "contains" in fc and "line" in fc:
                lines = text.splitlines()
                n = fc["line"]
                if n < 1 or n > len(lines) or fc["contains"] not in lines[n - 1]:
                    fail("case-%s %s: line %d of %s lacks %r"
                         % (case, pid, n, fc["path"], fc["contains"]))
                    continue
            elif "contains" in fc:
                if fc["contains"] not in text:
                    fail("case-%s %s: %s lacks %r"
                         % (case, pid, fc["path"], fc["contains"]))
                    continue
            elif "absent" in fc:
                if fc["absent"] in text:
                    fail("case-%s %s: %s unexpectedly contains %r"
                         % (case, pid, fc["path"], fc["absent"]))
                    continue
            else:
                fail("case-%s %s: bad fixture_check" % (case, pid))
                continue
            ok("case-%s %s anchor" % (case, pid))


def run_suite(case):
    """Run a candidate unittest suite; return True iff it passes."""
    cdir = REPO / "tests" / "review-cases" / ("case-%s" % case)
    cmd = [sys.executable, "-m", "unittest", "discover",
           "-s", str(cdir / "tests")]
    env = {"PYTHONDONTWRITEBYTECODE": "1",
           "PYTHONPATH": str(cdir / "candidate"),
           "PATH": "/usr/bin:/bin"}
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          cwd=str(REPO), env=env, timeout=120)
    return proc.returncode == 0


def check_suites():
    """Step 3: suites behave as designed (A fails, B and D pass)."""
    expected = {"a": False, "b": True, "d": True}
    for case, want_pass in expected.items():
        try:
            passed = run_suite(case)
        except (OSError, subprocess.TimeoutExpired) as exc:
            fail("case-%s suite error (%s)" % (case, exc))
            continue
        if passed == want_pass:
            ok("case-%s suite %s as designed"
               % (case, "passes" if passed else "fails"))
        else:
            fail("case-%s suite passes=%s, designed passes=%s"
                 % (case, passed, want_pass))


def check_skill():
    """Step 4: SKILL.md lint (lean, triggers, references resolve)."""
    skill = REPO / "skills" / "code-reviewer" / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    lines = text.splitlines()
    front = "\n".join(lines[:12])
    if "name: code-reviewer" not in front:
        fail("SKILL.md frontmatter name")
    else:
        ok("SKILL.md frontmatter name")
    m = re.search(r"^description:\s*(.+)$", front, re.M)
    if not m:
        fail("SKILL.md frontmatter description missing")
    elif "not to" not in m.group(1):
        fail("SKILL.md description lacks negative trigger")
    else:
        ok("SKILL.md description negative trigger")
    if "Do not use this skill" not in text:
        fail("SKILL.md lacks 'Do not use this skill' block")
    else:
        ok("SKILL.md negative-use block")
    body = [ln for ln in lines if ln.strip()]
    if len(body) > 500:
        fail("SKILL.md body %d lines exceeds 500" % len(body))
    else:
        ok("SKILL.md lean body (%d lines)" % len(body))
    refs = re.findall(r"\((references/[^)]+)\)", text)
    refs += re.findall(r"`(scripts/[^`]+)`", text)
    missing = [r for r in dict.fromkeys(refs)
               if not (skill.parent / r).is_file()]
    if missing:
        fail("SKILL.md dangling refs %s" % missing)
    else:
        ok("SKILL.md refs resolve (%d)" % len(set(refs)))


def check_thresholds():
    """Step 5: thresholds declare the gate."""
    path = REPO / "evals" / "thresholds.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        fail("thresholds.json unreadable (%s)" % exc)
        return
    gate = data.get("suite_gate", {})
    if gate.get("rule") != "all_cases_pass":
        fail("thresholds.json suite_gate rule")
    elif gate.get("total_cases") != len(CASES):
        fail("thresholds.json total_cases")
    elif not data.get("case_pass") or not data.get("frozen"):
        fail("thresholds.json missing case_pass/frozen")
    else:
        ok("thresholds.json gate")


def run_grader(reviews_dir):
    cmd = [sys.executable, str(REPO / "evals" / "grader.py"),
           "--reviews", str(reviews_dir)]
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          cwd=str(REPO), timeout=120)
    return proc.returncode, proc.stdout


def check_grader_selftest():
    """Step 6: good samples pass 4/4, each bad sample fails its case."""
    good = REPO / "evals" / "samples" / "good"
    code, out = run_grader(good)
    if code != 0:
        fail("grader self-test: good samples do not pass\n%s" % out)
    else:
        ok("grader self-test: good samples 4/4")
    bad = REPO / "evals" / "samples" / "bad"
    for case in CASES:
        single = bad / ("case-%s.md" % case)
        if not single.is_file():
            fail("grader self-test: missing bad sample case-%s" % case)
            continue
        # Grade the one bad review alongside good reviews for other cases.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            for other in CASES:
                src = (bad if other == case else good) \
                    / ("case-%s.md" % other)
                (tmpdir / ("case-%s.md" % other)).write_text(
                    src.read_text(encoding="utf-8"), encoding="utf-8")
            code, _ = run_grader(tmpdir)
        if code == 0:
            fail("grader self-test: bad sample case-%s passes" % case)
        else:
            ok("grader self-test: bad sample case-%s fails" % case)


def main():
    check_schema()
    check_anchors()
    check_suites()
    check_skill()
    check_thresholds()
    check_grader_selftest()
    print("---")
    if FAILURES:
        print("%d failure(s)" % len(FAILURES))
        return 1
    print("all integrity checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
