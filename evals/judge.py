#!/usr/bin/env python3
"""LLM-judge runner for Phase 2 validation (NOT part of the merge gate).

Builds one self-contained prompt per review (rubric + answer key +
review), calls an LLM command, extracts the fenced JSON verdict, and
writes one output file per review. Standard library only.

Usage:
    python3 evals/judge.py --manifest <jobs.json> --out <dir> [--cmd ...]

Manifest: [{"id": "k1-a", "case": "a", "review": "path/to/case-a.md"}]
Default LLM command: muse exec --prompt-file <file> (Meta provider).
Override with --cmd, e.g. --cmd "claude -p --prompt-file" (prompt file
path is appended as the last argument).

Up to one automatic retry per review when the output has no parseable
fenced JSON block; a still-unparseable review is recorded with
"parse_error" and counts as zero matches in evals/agreement.py.

Judge blindness: the prompt contains no hand scores and no mechanical
grades. Model identity is recorded from --model-id (free text, e.g.
the CLI version string) into every output file.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FENCE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


def build_prompt(case, key_text, rubric_text, template, review_text):
    return (template.replace("{RUBRIC}", rubric_text)
            .replace("{ANSWER_KEY}", key_text)
            .replace("{CASE}", case)
            .replace("{REVIEW}", review_text))


def run_llm(cmd, prompt):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                     encoding="utf-8") as fh:
        fh.write(prompt)
        prompt_path = fh.name
    try:
        proc = subprocess.run(cmd + [prompt_path], capture_output=True,
                              text=True, cwd=str(REPO), timeout=600)
    finally:
        Path(prompt_path).unlink(missing_ok=True)
    return proc.returncode, proc.stdout, proc.stderr


def extract_json(stdout):
    m = FENCE.search(stdout)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except ValueError:
        return None


def validate_scores(case, key, verdict):
    """Check the verdict covers exactly the key's items with valid scales.

    Exact allowlist: extra ids are errors, scores must be true ints
    (bool is not an int here: True == 1 would smuggle non-scores
    through `in (0, 1)`). Never raises on malformed model output:
    every problem is returned as an error string so batch grading
    records a schema failure instead of crashing.
    """
    errors = []
    if not isinstance(verdict, dict):
        return ["verdict is not an object"]
    for dim in ("decision", "architecture", "soul"):
        got = verdict.get(dim)
        if type(got) is not int or got not in (0, 1):
            errors.append("%s not 0/1" % dim)
    for group, scale in (("plants", (0, 1, 2)), ("controls", (0, 1))):
        want_ids = {item["id"] for item in key[group]}
        got_group = verdict.get(group, {})
        if not isinstance(got_group, dict):
            errors.append("%s is not an object" % group)
            continue
        for extra in sorted(set(got_group) - want_ids):
            errors.append("extra %s %s" % (group[:-1], extra))
        for item in key[group]:
            entry = got_group.get(item["id"], {})
            got = entry.get("score") if isinstance(entry, dict) else None
            if type(got) is not int or got not in scale:
                errors.append("%s %s not %s" % (
                    group[:-1], item["id"],
                    "0/1/2" if group == "plants" else "0/1"))
    return errors


def main(argv=None):
    ap = argparse.ArgumentParser(description="LLM-judge runner")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cmd", nargs="+",
                    default=["muse", "exec", "--prompt-file"])
    ap.add_argument("--model-id", default="muse exec (Meta provider)")
    args = ap.parse_args(argv)

    rubric = (REPO / "evals" / "rubric.md").read_text(encoding="utf-8")
    template = (REPO / "evals" / "judge_prompt.md").read_text(
        encoding="utf-8")
    jobs = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    failures = 0
    for job in jobs:
        key_path = (REPO / "tests" / "review-cases"
                    / ("case-%s" % job["case"]) / "answer-key.json")
        key = json.loads(key_path.read_text(encoding="utf-8"))
        review = (REPO / job["review"]).read_text(encoding="utf-8")
        prompt = build_prompt(job["case"], key_path.read_text(
            encoding="utf-8"), rubric, template, review)
        verdict, attempts, err = None, 0, ""
        for attempt in (prompt, prompt + "\n\nOutput the JSON block only."):
            attempts += 1
            code, stdout, stderr = run_llm(args.cmd, attempt)
            if code != 0:
                # A nonzero provider exit is an execution failure even
                # when stdout happens to contain parseable JSON: the
                # provider reported failure, so the verdict is unusable.
                err = ("provider exit %d: %s"
                       % (code, (stderr.strip() or stdout.strip())[-500:]))
                continue
            verdict = extract_json(stdout)
            if verdict is not None:
                break
            err = (stderr.strip() or stdout.strip())[-500:]
        record = {"id": job["id"], "case": job["case"],
                  "review": job["review"], "model": args.model_id,
                  "attempts": attempts}
        if verdict is None:
            record["parse_error"] = err or ("exit %d" % code)
            failures += 1
        else:
            record["scores"] = verdict
            problems = validate_scores(job["case"], key, verdict)
            if problems:
                record["schema_problems"] = problems
                failures += 1
        (outdir / ("%s.json" % job["id"])).write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print("%s: %s" % (job["id"],
                          "PARSE/SCHEMA FAIL" if failures and
                          ("parse_error" in record
                           or "schema_problems" in record) else "ok"))
    print("failures: %d/%d" % (failures, len(jobs)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
