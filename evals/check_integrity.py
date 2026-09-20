#!/usr/bin/env python3
"""Deterministic integrity gate for the code-reviewer eval harness.

Runs in CI on every push. No LLM calls, no network, no secrets.
Standard library only.

Checks:
  1. Every tests/review-cases/case-*/ has request.md + a schema-valid
     answer-key.json.
  2. Every plant fixture anchor still holds (plants are actually planted,
     controls still describe the fixture) -- guards against fixture rot.
  3. Candidate suites behave as their keys declare (pass/fail/absent).
     A failing suite is the executable proof that the planted defect
     exists.
  4. SKILL.md lint: frontmatter name/description, negative triggers,
     body within the lean budget, referenced files exist.
  5. evals/thresholds.json is valid and declares the suite gate.
  6. Grader self-test: synthetic good reviews pass N/N, each synthetic
     bad review fails its case. An untested instrument proves nothing.
  7. hand_scores.json schema: every gold review covers its key's items
     with valid scales.
  8. Agreement self-test: agreement.py meets/misses its gate on
     synthetic fixtures (3/5 vs 5/5 at 0.75).
  9. Priority-set check: a plant with priorities [P0, P1] passes on a
     P0 review and fails on a P3 review.
  10. Vocabulary case rule: multi-word tokens match case-insensitively
      (distinctive phrases), single-word tokens case-sensitively
      (common words must not false-accept as verdicts).

Usage:  python3 evals/check_integrity.py
Exit code 0 when all checks pass, else 1.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FAILURES = []


def discover_cases():
    """Case ids from case-*/answer-key.json, sorted (battery v2: a..t)."""
    cases_dir = REPO / "tests" / "review-cases"
    return sorted(p.parent.name.removeprefix("case-")
                  for p in cases_dir.glob("case-*/answer-key.json"))


CASES = discover_cases()


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
                "plants", "controls", "suite"}
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
        if key.get("suite", {}).get("expected") not in (
                "pass", "fail", "absent"):
            fail("case-%s: key suite.expected not pass/fail/absent" % case)
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
    """Step 3: suites behave as their keys declare (pass/fail/absent)."""
    for case in CASES:
        cdir = REPO / "tests" / "review-cases" / ("case-%s" % case)
        try:
            key = load_key(case)
        except (OSError, ValueError):
            continue  # reported in step 1
        want = key.get("suite", {}).get("expected")
        has_tests = (cdir / "tests").is_dir()
        if want == "absent":
            if has_tests:
                fail("case-%s: suite expected absent, tests/ exists" % case)
            else:
                ok("case-%s suite absent as designed" % case)
            continue
        if want not in ("pass", "fail"):
            continue  # reported in step 1
        if not has_tests:
            fail("case-%s: suite expected %s, tests/ missing" % (case, want))
            continue
        try:
            passed = run_suite(case)
        except (OSError, subprocess.TimeoutExpired) as exc:
            fail("case-%s suite error (%s)" % (case, exc))
            continue
        if passed == (want == "pass"):
            ok("case-%s suite %s as designed"
               % (case, "passes" if passed else "fails"))
        else:
            fail("case-%s suite passes=%s, designed %s" % (case, passed, want))


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


def sample_path(case, kind):
    """Good/bad sample review for a case.

    Cases a-d keep the Phase 1 location (evals/samples/{good,bad});
    newer cases ship samples next to the fixture (sample_good/bad.md).
    """
    legacy = REPO / "evals" / "samples" / kind / ("case-%s.md" % case)
    if legacy.is_file():
        return legacy
    name = "sample_good.md" if kind == "good" else "sample_bad.md"
    return REPO / "tests" / "review-cases" / ("case-%s" % case) / name


def check_grader_selftest():
    """Step 6: good samples pass N/N, each bad sample fails its case."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        gooddir = Path(tmp) / "good"
        gooddir.mkdir()
        missing = [c for c in CASES
                   if not sample_path(c, "good").is_file()]
        if missing:
            fail("grader self-test: missing good samples %s" % missing)
            return
        for case in CASES:
            (gooddir / ("case-%s.md" % case)).write_text(
                sample_path(case, "good").read_text(encoding="utf-8"),
                encoding="utf-8")
        code, out = run_grader(gooddir)
        if code != 0:
            fail("grader self-test: good samples do not pass\n%s" % out)
            return
        ok("grader self-test: good samples %d/%d"
           % (len(CASES), len(CASES)))
        for case in CASES:
            bad = sample_path(case, "bad")
            if not bad.is_file():
                fail("grader self-test: missing bad sample case-%s" % case)
                continue
            with tempfile.TemporaryDirectory() as tmp2:
                tmpdir = Path(tmp2)
                for other in CASES:
                    src = bad if other == case else sample_path(other, "good")
                    (tmpdir / ("case-%s.md" % other)).write_text(
                        src.read_text(encoding="utf-8"), encoding="utf-8")
                code, _ = run_grader(tmpdir)
            if code == 0:
                fail("grader self-test: bad sample case-%s passes" % case)
            else:
                ok("grader self-test: bad sample case-%s fails" % case)


def check_hand_scores():
    """Step 7: hand_scores.json covers its reviews with valid scales."""
    path = REPO / "evals" / "hand_scores.json"
    try:
        gold = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        fail("hand_scores.json unreadable (%s)" % exc)
        return
    if not gold.get("reviews"):
        fail("hand_scores.json has no reviews")
        return
    bad = 0
    for rid, review in gold["reviews"].items():
        case = review.get("case")
        try:
            key = load_key(case)
        except (OSError, ValueError):
            fail("hand_scores %s: unknown case %r" % (rid, case))
            bad += 1
            continue
        if not (REPO / review.get("path", "")).is_file():
            fail("hand_scores %s: review path missing" % rid)
            bad += 1
        scores = review.get("scores", {})
        for dim in ("decision", "architecture", "soul"):
            if scores.get(dim) not in (0, 1):
                fail("hand_scores %s: %s not 0/1" % (rid, dim))
                bad += 1
        want_plants = {p["id"] for p in key["plants"]}
        got_plants = set(scores.get("plants", {}))
        if want_plants != got_plants:
            fail("hand_scores %s: plants %s, key wants %s"
                 % (rid, sorted(got_plants), sorted(want_plants)))
            bad += 1
        for pid, val in scores.get("plants", {}).items():
            if val not in (0, 1, 2):
                fail("hand_scores %s: plant %s not 0/1/2" % (rid, pid))
                bad += 1
        want_controls = {c["id"] for c in key["controls"]}
        got_controls = set(scores.get("controls", {}))
        if want_controls != got_controls:
            fail("hand_scores %s: controls %s, key wants %s"
                 % (rid, sorted(got_controls), sorted(want_controls)))
            bad += 1
        for cid, val in scores.get("controls", {}).items():
            if val not in (0, 1):
                fail("hand_scores %s: control %s not 0/1" % (rid, cid))
                bad += 1
    if not bad:
        ok("hand_scores.json schema (%d reviews)" % len(gold["reviews"]))


def check_agreement_selftest():
    """Step 8: agreement.py honors its gate on synthetic fixtures."""
    import tempfile
    gold = {"reviews": {"t1": {"scores": {
        "decision": 1, "architecture": 1, "soul": 1,
        "plants": {"X1": 2}, "controls": {"X-C1": 1}}}}}
    judge_hit = {"scores": {
        "decision": 1, "architecture": 1, "soul": 1,
        "plants": {"X1": {"score": 2, "quote": "q"}},
        "controls": {"X-C1": {"score": 1, "quote": "q"}}}}
    judge_miss = {"scores": {
        "decision": 0, "architecture": 1, "soul": 1,
        "plants": {"X1": {"score": 1, "quote": "q"}},
        "controls": {"X-C1": {"score": 1, "quote": "q"}}}}
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        (tmpdir / "gold.json").write_text(json.dumps(gold), encoding="utf-8")
        hitdir, missdir = tmpdir / "hit", tmpdir / "miss"
        hitdir.mkdir()
        missdir.mkdir()
        (hitdir / "t1.json").write_text(json.dumps(judge_hit),
                                        encoding="utf-8")
        (missdir / "t1.json").write_text(json.dumps(judge_miss),
                                         encoding="utf-8")
        for name, jdir, want_code in (("5/5 meets 0.75", hitdir, 0),
                                      ("3/5 misses 0.75", missdir, 1)):
            proc = subprocess.run(
                [sys.executable, str(REPO / "evals" / "agreement.py"),
                 "--gold", str(tmpdir / "gold.json"), "--judge", str(jdir),
                 "--min", "0.75"],
                capture_output=True, text=True, cwd=str(REPO), timeout=120)
            if proc.returncode == want_code:
                ok("agreement self-test: %s" % name)
            else:
                fail("agreement self-test: %s (exit %d)\n%s"
                     % (name, proc.returncode, proc.stdout))


def check_priority_sets():
    """Step 9: plants with priority sets accept any listed severity."""
    sys.path.insert(0, str(REPO / "evals"))
    import grader
    key = {"decision": "Changes requested",
           "architecture": {"allowed": ["High"]},
           "soul": {"allowed": ["Unverifiable"]},
           "plants": [{"id": "Z1", "file": "z.py", "any_of": ["zeek"],
                       "priority": ["P0", "P1"]}],
           "controls": []}
    good = ("**Decision**: Changes requested\n"
            "**Findings**: P0, z.py:1 — zeek defect.\n"
            "**Verdicts**: architectural High; soul Unverifiable.\n")
    nit = good.replace("P0, z.py", "P3, z.py")
    if grader.grade_case("z", good, key)["pass"]:
        ok("priority set: listed P0 passes")
    else:
        fail("priority set: listed P0 does not pass")
    if not grader.grade_case("z", nit, key)["pass"]:
        ok("priority set: unlisted P3 fails")
    else:
        fail("priority set: unlisted P3 passes")


def check_vocab_case():
    """Step 10: closed-vocabulary case rule is pinned, not accidental."""
    sys.path.insert(0, str(REPO / "evals"))
    import grader
    ok_dec, seen_dec = grader.check_first_token(
        ["decision: changes requested"], "Changes requested",
        grader.DECISION_VOCAB)
    if ok_dec and seen_dec[:1] == ["Changes requested"]:
        ok("vocab case: lowercase multi-word decision passes")
    else:
        fail("vocab case: lowercase multi-word decision %s %s"
             % (ok_dec, seen_dec))
    ok_arch, seen_arch = grader.check_vocab(
        ["architectural high"], "architect", ["High"], grader.ARCH_VOCAB)
    if not ok_arch and not seen_arch:
        ok("vocab case: lowercase single-word arch verdict fails")
    else:
        fail("vocab case: lowercase single-word arch verdict %s %s"
             % (ok_arch, seen_arch))
    ok_soul, seen_soul = grader.check_vocab(
        ["soul betrayed"], "soul", ["Betrayed"], grader.SOUL_VOCAB)
    if not ok_soul and not seen_soul:
        ok("vocab case: lowercase single-word soul verdict fails")
    else:
        fail("vocab case: lowercase single-word soul verdict %s %s"
             % (ok_soul, seen_soul))
    _, seen_prose = grader.check_vocab(
        ["architectural: low coupling kept, no layer violations"],
        "architect", ["High"], grader.ARCH_VOCAB)
    if not seen_prose:
        ok("vocab case: 'low coupling' prose matches no verdict")
    else:
        fail("vocab case: prose false-accepts %s" % seen_prose)


def main():
    check_schema()
    check_anchors()
    check_suites()
    check_skill()
    check_thresholds()
    check_grader_selftest()
    check_hand_scores()
    check_agreement_selftest()
    check_priority_sets()
    check_vocab_case()
    print("---")
    if FAILURES:
        print("%d failure(s)" % len(FAILURES))
        return 1
    print("all integrity checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
