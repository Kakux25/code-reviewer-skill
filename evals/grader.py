#!/usr/bin/env python3
"""Mechanical grader for code-reviewer eval cases (Phase 1: deterministic).

Scores review outputs against tests/review-cases/case-*/answer-key.json using
only literal matching on the skill's own closed vocabulary (decision tokens,
verdict tokens, priority tokens) plus file citations and evidence tokens.

This is a coarse lexical proxy, not a semantic judgment: a citation next to a
token does not prove the diagnosis is correct, and negation ("no partial
publication") can fool token matching. Documented limits live in
evals/README.md; semantic verification is the Phase 2 calibrated judge.

Usage:
    python3 evals/grader.py --reviews <dir> [--keys tests/review-cases]
                            [--out grading.json]

<dir> must contain case-a.md, case-b.md, case-c.md, case-d.md.
Exit code 0 when the suite gate in evals/thresholds.json is met, else 1.
Standard library only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CASES = ("a", "b", "c", "d")

ARCH_VOCAB = ["High with concerns", "High", "Acceptable", "Low",
              "Insufficient evidence"]
SOUL_VOCAB = ["Preserved", "Tense", "Betrayed", "Unverifiable"]
DECISION_VOCAB = ["Changes requested", "No actionable findings", "Incomplete"]


def token_re(token):
    """Case-sensitive literal with word boundaries, optional backticks."""
    return re.compile(r"`?" + re.escape(token) + r"`?\b", re.IGNORECASE
                      if " " in token else 0)


def scoped_lines(text, scope_word):
    """Section-aware scope for scope_word ('decision' / 'verdict').

    A markdown ATX section whose header contains the word contributes its
    header plus body lines. Falls back to lines containing the word
    (inline style, e.g. '**Decision**: ...'), then to the whole document.
    """
    sections = []
    cur_header, cur_lines = "", []
    for ln in text.splitlines():
        m = re.match(r"#{1,6}\s+(.*)", ln)
        if m:
            sections.append((cur_header, cur_lines))
            cur_header, cur_lines = m.group(1), []
        else:
            cur_lines.append(ln)
    sections.append((cur_header, cur_lines))
    hits = [ln for h, ls in sections for ln in ([h] + ls)
            if scope_word.lower() in h.lower()]
    if hits:
        return hits
    # Inline style: the triggering line plus its continuation lines
    # (e.g. '3. **Verdicts**:' followed by sub-bullets), stopping at a
    # blank line, a new numbered item, or a header.
    out = []
    grab = False
    for ln in text.splitlines():
        if scope_word.lower() in ln.lower():
            grab = True
            out.append(ln)
        elif grab:
            if (not ln.strip() or re.match(r"#{1,6}\s+", ln)
                    or re.match(r"\d+\.\s+", ln)):
                grab = False
            else:
                out.append(ln)
    return out if out else text.splitlines()


def ordered_tokens(lines, vocab):
    """Vocabulary tokens in order of first appearance (longest wins ties)."""
    joined = "\n".join(lines)
    found = []
    for tok in vocab:
        m = token_re(tok).search(joined)
        if m:
            found.append((m.start(), -len(tok), tok))
    return [tok for _, _, tok in sorted(found)]


def check_first_token(lines, expected, vocab):
    """Pass iff the first vocabulary token in scope is the expected one.

    Later mentions (rationale discussing rejected alternatives) are ignored:
    the skill's format states the verdict first, then the rationale.
    """
    seen = ordered_tokens(lines, vocab)
    return (bool(seen) and seen[0] == expected), seen


def check_vocab(lines, dim_word, allowed, vocab):
    """Pass iff the first verdict token on dimension lines is allowed.

    Dimension lines mention e.g. 'architect' or 'soul'; all scope lines
    are used when no line does (single-line verdict styles).
    """
    dim = [ln for ln in lines if dim_word.lower() in ln.lower()] or lines
    seen = ordered_tokens(dim, vocab)
    return (bool(seen) and seen[0] in allowed), seen


def check_plant(lines, plant):
    text = "\n".join(lines)
    # Ignore inline markdown so `discount_percent` matches discount_percent.
    low = text.replace("`", "").replace("*", "").lower()
    detail = {}
    if plant.get("file"):
        cited = plant["file"].lower() in low
        detail["file_cited"] = cited
    else:
        cited = True
    token_hit = any(t.lower() in low for t in plant["any_of"])
    detail["token_hit"] = token_hit
    if plant.get("priority"):
        prio = re.search(r"\b" + re.escape(plant["priority"]) + r"\b", text)
        detail["priority_hit"] = bool(prio)
        prio_ok = bool(prio)
    else:
        prio_ok = True
    detail["hit_tokens"] = [t for t in plant["any_of"] if t.lower() in low]
    return cited and token_hit and prio_ok, detail


def check_control(lines, control):
    kind = control["kind"]
    if kind == "not_flagged":
        fname = control["file"].lower()
        sev = [re.compile(r"\b" + re.escape(s) + r"\b")
               for s in control["severities"]]
        bad = [ln.strip() for ln in lines
               if fname in ln.lower() and any(r.search(ln) for r in sev)]
        return not bad, {"violating_lines": bad}
    if kind == "forbid_phrase":
        low = "\n".join(lines).lower()
        bad = [p for p in control["any_of"] if p.lower() in low]
        return not bad, {"violating_phrases": bad}
    raise ValueError("unknown control kind: %r" % kind)


def grade_case(case, review_text, key):
    lines = review_text.splitlines()
    result = {"case": case, "checks": {}, "pass": True}

    dec_lines = scoped_lines(review_text, "decision")
    dec_ok, dec_seen = check_first_token(
        dec_lines, key["decision"], DECISION_VOCAB)
    result["checks"]["decision"] = {"expected": key["decision"],
                                    "seen": dec_seen, "ok": dec_ok}

    verdict_lines = scoped_lines(review_text, "verdict")
    arch_ok, arch_seen = check_vocab(
        verdict_lines, "architect",
        key["architecture"]["allowed"], ARCH_VOCAB)
    result["checks"]["architecture"] = {
        "allowed": key["architecture"]["allowed"],
        "seen": arch_seen, "ok": arch_ok}
    soul_ok, soul_seen = check_vocab(
        verdict_lines, "soul", key["soul"]["allowed"], SOUL_VOCAB)
    result["checks"]["soul"] = {
        "allowed": key["soul"]["allowed"],
        "seen": soul_seen, "ok": soul_ok}

    plants = {}
    for plant in key["plants"]:
        ok, detail = check_plant(lines, plant)
        plants[plant["id"]] = {"ok": ok, "detail": detail}
    result["checks"]["plants"] = plants

    controls = {}
    for control in key["controls"]:
        ok, detail = check_control(lines, control)
        controls[control["id"]] = {"ok": ok, "detail": detail}
    result["checks"]["controls"] = controls

    all_ok = ([dec_ok, arch_ok, soul_ok]
              + [v["ok"] for v in plants.values()]
              + [v["ok"] for v in controls.values()])
    result["pass"] = all(all_ok)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Mechanical review grader")
    ap.add_argument("--reviews", required=True, help="dir with case-*.md")
    ap.add_argument("--keys", default=str(REPO / "tests" / "review-cases"))
    ap.add_argument("--out", default=None, help="write grading.json here")
    args = ap.parse_args(argv)

    reviews = Path(args.reviews)
    keys_dir = Path(args.keys)
    report = {"cases": {}, "summary": {}}
    missing = []
    for case in CASES:
        review_path = reviews / ("case-%s.md" % case)
        key_path = keys_dir / ("case-%s" % case) / "answer-key.json"
        if not review_path.is_file():
            missing.append(str(review_path))
            continue
        key = json.loads(key_path.read_text(encoding="utf-8"))
        text = review_path.read_text(encoding="utf-8")
        report["cases"][case] = grade_case(case, text, key)
    if missing:
        print("missing reviews: %s" % ", ".join(missing), file=sys.stderr)
        return 2
    passed = sum(1 for c in report["cases"].values() if c["pass"])
    total = len(report["cases"])
    gate = passed == total == len(CASES)
    report["summary"] = {"passed": passed, "total": total,
                         "gate": "all_cases_pass", "gate_met": gate}
    for case in CASES:
        c = report["cases"][case]
        print("case-%s: %s" % (case, "PASS" if c["pass"] else "FAIL"))
        if not c["pass"]:
            for name, chk in c["checks"].items():
                if not isinstance(chk, dict):
                    continue
                if "ok" in chk:
                    if not chk["ok"]:
                        print("  FAIL %s: %s" % (name, json.dumps(chk)))
                else:
                    for sub, v in chk.items():
                        if isinstance(v, dict) and not v.get("ok", True):
                            print("  FAIL %s.%s: %s"
                                  % (name, sub, json.dumps(v)))
    print("gate all_cases_pass: %d/%d %s"
          % (passed, total, "MET" if gate else "NOT MET"))
    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2) + "\n",
                                  encoding="utf-8")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
