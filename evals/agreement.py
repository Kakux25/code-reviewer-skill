#!/usr/bin/env python3
"""Judge-vs-hand agreement for Phase 2 (deterministic; no LLM calls).

Compares LLM-judge outputs (evals/judge.py records) against
evals/hand_scores.json item by item. Exact match per item; plant
levels (0/1/2) must match exactly. Standard library only.

Usage:
    python3 evals/agreement.py --gold <hand_scores.json> --judge <dir>
                               [--out agreement.json] [--min 0.75]

Exit code 0 iff agreement >= --min (default 0.75, the pre-declared
gate in evals/thresholds.json). Unparseable judge records and schema
problems count as zero matches for every item of that review.
"""

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def gold_items(review):
    """Flatten a gold review's scores to {(kind, id): score}."""
    scores = review["scores"]
    items = {("decision", ""): scores["decision"],
             ("architecture", ""): scores["architecture"],
             ("soul", ""): scores["soul"]}
    for pid, val in scores["plants"].items():
        items[("plant", pid)] = val
    for cid, val in scores["controls"].items():
        items[("control", cid)] = val
    return items


def judge_items(record):
    """Flatten a judge record; None when the record is unusable."""
    if "parse_error" in record or "schema_problems" in record:
        return None
    scores = record["scores"]
    try:
        items = {("decision", ""): scores["decision"],
                 ("architecture", ""): scores["architecture"],
                 ("soul", ""): scores["soul"]}
        for pid, val in scores["plants"].items():
            items[("plant", pid)] = val["score"]
        for cid, val in scores["controls"].items():
            items[("control", cid)] = val["score"]
    except (KeyError, TypeError, AttributeError):
        return None
    return items


def main(argv=None):
    ap = argparse.ArgumentParser(description="Judge agreement scorer")
    ap.add_argument("--gold", required=True)
    ap.add_argument("--judge", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--min", type=float, default=0.75)
    args = ap.parse_args(argv)

    gold = json.loads(Path(args.gold).read_text(encoding="utf-8"))
    judgedir = Path(args.judge)
    report = {"reviews": {}, "by_kind": {}, "matches": 0, "total": 0,
              "agreement": 0.0, "gate": args.min, "gate_met": False}
    for rid, greview in gold["reviews"].items():
        gitems = gold_items(greview)
        jpath = judgedir / ("%s.json" % rid)
        entry = {"matches": 0, "total": len(gitems), "mismatches": []}
        if not jpath.is_file():
            entry["mismatches"] = ["missing judge output"]
        else:
            record = json.loads(jpath.read_text(encoding="utf-8"))
            jitems = judge_items(record)
            if jitems is None:
                entry["mismatches"] = ["unusable judge record"]
            else:
                for key, gval in gitems.items():
                    kind = key[0]
                    slot = report["by_kind"].setdefault(
                        kind, {"matches": 0, "total": 0})
                    slot["total"] += 1
                    report["total"] += 1
                    if key in jitems and jitems[key] == gval:
                        slot["matches"] += 1
                        report["matches"] += 1
                        entry["matches"] += 1
                    else:
                        entry["mismatches"].append(
                            "%s%s gold=%r judge=%r" % (
                                key[0], " " + key[1] if key[1] else "",
                                gval, (jitems.get(key)
                                       if key in jitems else "<absent>")))
                # Items counted above; fix totals for missing/unusable below.
                report["reviews"][rid] = entry
                continue
        # Missing or unusable record: every gold item is a miss.
        for key in gitems:
            slot = report["by_kind"].setdefault(
                key[0], {"matches": 0, "total": 0})
            slot["total"] += 1
            report["total"] += 1
        report["reviews"][rid] = entry

    if report["total"]:
        report["agreement"] = report["matches"] / report["total"]
    report["gate_met"] = report["agreement"] >= args.min
    for rid, entry in report["reviews"].items():
        print("%s: %d/%d" % (rid, entry["matches"], entry["total"]))
        for mm in entry["mismatches"]:
            print("  MISS %s" % mm)
    for kind, slot in sorted(report["by_kind"].items()):
        print("%s: %d/%d" % (kind, slot["matches"], slot["total"]))
    print("agreement: %d/%d = %.3f gate %.2f %s"
          % (report["matches"], report["total"], report["agreement"],
             args.min, "MET" if report["gate_met"] else "NOT MET"))
    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2) + "\n",
                                  encoding="utf-8")
    return 0 if report["gate_met"] else 1


if __name__ == "__main__":
    sys.exit(main())
