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
  11. Failure classification: an ImportError, or exit != 0 without
      executed tests, is a loader failure, never bug proof; assertion
      failures and candidate-raised errors after "Ran N tests" are.

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
    """Case ids from case-*/answer-key.json, sorted (battery v2.1: a..v)."""
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
    """Run a candidate unittest suite; return (passed, output).

    passed is True iff the suite exits 0. output is the combined
    stdout/stderr, kept so a failure can be classified as an
    executed-test failure (bug proof) rather than a loader or
    setup failure (not proof of anything).
    """
    cdir = REPO / "tests" / "review-cases" / ("case-%s" % case)
    cmd = [sys.executable, "-m", "unittest", "discover",
           "-s", str(cdir / "tests")]
    env = {"PYTHONDONTWRITEBYTECODE": "1",
           "PYTHONPATH": str(cdir / "candidate"),
           "PATH": "/usr/bin:/bin"}
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          cwd=str(REPO), env=env, timeout=120)
    return proc.returncode == 0, proc.stdout + proc.stderr


def _text_block_phase(header_test, block):
    """Phase of one ERROR:/FAIL: traceback block (F2 followup).

    import: loader failure (_FailedTest) or ImportError.
    setup: setUp (or its helpers) raised before the test body ran.
    teardown: tearDown raised after the body ran.
    call: the test body executed and misbehaved (bug proof).
    """
    if "_FailedTest" in header_test or "_FailedTest" in block:
        return "import"
    if "ImportError" in block or "ModuleNotFoundError" in block:
        return "import"
    frames = re.findall(r'File "[^"]+", line \d+, in (\S+)', block)
    method = header_test.split("(")[0].split(".")[-1]
    if "setUp" in frames and method not in frames:
        return "setup"
    if "tearDown" in frames:
        return "teardown"
    return "call"


def suite_failure_is_bug_proof(output):
    """True iff a nonzero-exit suite actually executed tests that
    failed, rather than dying in import/discovery/setup/teardown.

    A loader or setup failure (ImportError, undiscovered tests, a
    setUp RuntimeError) must never count as the executable proof
    that a planted defect exists. Runtime errors raised *by* the
    candidate under test (e.g. a TypeError from a wrong signature)
    are still bug proof: the tests ran and the candidate
    misbehaved. Traceback blocks are classified by phase; terse
    summaries without tracebacks keep the legacy Ran/FAILED rule.
    """
    headers = list(re.finditer(r"^(ERROR|FAIL): (\S+)", output, re.M))
    if headers:
        spans = [h.start() for h in headers] + [len(output)]
        for header, end in zip(headers, spans[1:]):
            if _text_block_phase(header.group(2),
                                 output[header.start():end]) == "call":
                return True
        return False
    if re.search(r"Ran [1-9]\d* tests?", output) is None:
        return False
    if "ImportError" in output or "ModuleNotFoundError" in output:
        return False
    return "FAILED" in output


def run_structured_probe(case):
    """Per-test identity/phase/outcome for a case suite (F2 followup).

    Same sandbox as run_suite (interpreter, PYTHONPATH, PATH, cwd).
    Returns the parsed probe dict, or None if the probe itself
    failed (infra failure: never bug proof, always gate failure).
    """
    cdir = REPO / "tests" / "review-cases" / ("case-%s" % case)
    cmd = [sys.executable, str(REPO / "evals" / "structured_unittest.py"),
           str(cdir / "tests")]
    env = {"PYTHONDONTWRITEBYTECODE": "1",
           "PYTHONPATH": str(cdir / "candidate"),
           "PATH": "/usr/bin:/bin"}
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              cwd=str(REPO), env=env, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except ValueError:
        return None


def check_suites():
    """Step 3: suites behave as their keys declare (pass/fail/absent).

    A designed-fail suite must fail by executed tests, not by an
    import/setup failure: exit != 0 alone is not bug proof.
    """
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
            passed, output = run_suite(case)
        except (OSError, subprocess.TimeoutExpired) as exc:
            fail("case-%s suite error (%s)" % (case, exc))
            continue
        if want == "pass":
            if passed:
                ok("case-%s suite passes as designed" % case)
            else:
                fail("case-%s suite fails, designed pass" % case)
            continue
        if passed:
            fail("case-%s suite passes, designed fail" % case)
            continue
        # Two independent oracles must agree it is an executed-test
        # failure: the structured probe (identity/phase per test) and
        # the traceback-text classifier. Ambiguity never certifies.
        probe = run_structured_probe(case)
        structured = (probe is not None and probe.get("runner_error")
                      is None and any(e["phase"] == "call"
                                      for e in probe.get("events", [])))
        textual = suite_failure_is_bug_proof(output)
        if probe is None or probe.get("runner_error") is not None:
            fail("case-%s structured probe failed (infra)" % case)
        elif structured and textual:
            ok("case-%s suite fails as designed" % case)
        elif structured != textual:
            fail("case-%s oracles disagree (structured=%s text=%s)"
                 % (case, structured, textual))
        else:
            fail("case-%s suite exit != 0 is a loader/setup failure, "
                 "not proof of the planted defect" % case)


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


def check_grader_negation():
    """Step 6b: negation, open-questions scope, base exemption."""
    sys.path.insert(0, str(REPO / "evals"))
    import grader
    cases = [
        ("there is no partial publication here", "partial publication",
         False, "denied token does not satisfy"),
        ("diagnoses the divisor bug as P1", "P1", True,
         "affirmed priority satisfies"),
        ("no longer silent. Findings: P2", "P2", True,
         "negation across a boundary does not deny"),
        ("not P0, but P1 for this leak", "P1", True,
         "'but' resets the negation window"),
        ("severity P1 but not P0", "P0", False,
         "denied alternative does not satisfy"),
        ("no doubt this deserves P1", "P1", True,
         "distant negator does not deny"),
    ]
    for text, token, want, name in cases:
        got = grader._affirmed(
            text, token,
            word_bound=len(token) <= 2, case_sensitive=len(token) <= 2)
        if got == want:
            ok("grader negation: %s" % name)
        else:
            fail("grader negation: %s (want %s)" % (name, want))
    scoped = grader.finding_lines(
        ["## Findings", "- P1 leaking socket", "## Open questions",
         "- is the divisor right?", "## Verdicts"])
    if (any("leaking" in ln for ln in scoped)
            and not any("divisor" in ln for ln in scoped)):
        ok("grader scope: open questions excluded from plants")
    else:
        fail("grader scope: open-questions exclusion broken")
    ctrl = {"kind": "forbid_phrase", "any_of": ["tests pass"]}
    ok_base, _ = grader.check_control(
        ["the base suite passes; candidate fails"], ctrl)
    ok_naked, _ = grader.check_control(["all tests pass"], ctrl)
    if ok_base and not ok_naked:
        ok("grader control: base-attributed pass exempt, naked fails")
    else:
        fail("grader control: base exemption broken")


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


def check_failure_classification():
    """Step 11: loader failures are never bug proof."""
    proof = ("Ran 2 tests in 0.001s\n\nFAILED (failures=1, errors=1)\n"
             "TypeError: greet() missing 1 required positional argument")
    loader_import = ("Traceback (most recent call last):\n"
                     'ImportError: AUDIT: unrelated dependency failure\n'
                     "Ran 2 tests in 0.001s\n\nFAILED (errors=1)\n")
    loader_empty = "Ran 0 tests in 0.000s\n\nOK\n"
    setup_err = ("ERROR: test_v (test_mod.T)\n"
                 '  File "/x/test_mod.py", line 5, in setUp\n'
                 '    raise RuntimeError("AUDIT_SETUP_FAILED")\n'
                 "RuntimeError: AUDIT_SETUP_FAILED\n"
                 "Ran 2 tests in 0.001s\n\nFAILED (errors=2)\n")
    teardown_err = ("ERROR: test_v (test_mod.T)\n"
                    '  File "/x/test_mod.py", line 12, in tearDown\n'
                    '    raise RuntimeError("AUDIT_TEARDOWN_FAILED")\n'
                    "RuntimeError: AUDIT_TEARDOWN_FAILED\n"
                    "Ran 1 test in 0.001s\n\nFAILED (errors=1)\n")
    mixed = (setup_err +
             "FAIL: test_w (test_mod.T)\n"
             '  File "/x/test_mod.py", line 9, in test_w\n'
             "    self.assertEqual(1, 2)\n"
             "AssertionError: 1 != 2\n")
    cases = [(proof, True, "assertion failure + candidate TypeError"),
             ("Ran 2 tests\n\nFAILED (failures=2)\n", True,
              "plain assertion failures"),
             (loader_import, False, "ImportError despite exit != 0"),
             (loader_empty, False, "no tests executed"),
             ("Ran 1 test\n\nOK\n", False, "pass output is not a failure"),
             (setup_err, False, "setUp RuntimeError is not bug proof"),
             (teardown_err, False, "tearDown error is not bug proof"),
             (mixed, True, "setup noise plus a real test failure")]
    for output, want, name in cases:
        if suite_failure_is_bug_proof(output) == want:
            ok("failure classification: %s" % name)
        else:
            fail("failure classification: %s" % name)


def main():
    check_schema()
    check_anchors()
    check_suites()
    check_skill()
    check_thresholds()
    check_grader_selftest()
    check_grader_negation()
    check_hand_scores()
    check_agreement_selftest()
    check_priority_sets()
    check_vocab_case()
    check_failure_classification()
    print("---")
    if FAILURES:
        print("%d failure(s)" % len(FAILURES))
        return 1
    print("all integrity checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
