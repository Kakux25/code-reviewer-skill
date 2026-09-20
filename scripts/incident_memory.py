#!/usr/bin/env python3
"""Gate 5: deterministic incident-case retrieval (stdlib only).

Retrieval proposes, judgment disposes: weighted lexical scoring over
the structured case fields ranks candidates, but the incident-memory
skill makes the final transfer call (a top-ranked case whose
mechanism does not transfer must be rejected, not followed).

Scoring: 3 per mechanism word hit, 1 per context word hit, 1 per
tag hit against mechanism+context. Only positive scores rank.
render_public strips restricted fields structurally.
"""
import json
import re
from pathlib import Path

WORD = re.compile(r"[a-z0-9]+")


def _words(text):
    return set(WORD.findall(text.lower()))


def load_cases(cases_dir):
    out = []
    for f in sorted(Path(cases_dir).glob("*.json")):
        out.append(json.loads(f.read_text(encoding="utf-8")))
    return out


def score(case, query):
    words = _words(query.get("text", "")) | {
        t.lower() for t in query.get("tags", [])}
    mech = {w for e in case["mechanism"] for w in _words(e)}
    ctx = {w for e in case["context"] for w in _words(e)}
    tags = {t.lower() for t in query.get("tags", [])}
    return (3 * len(mech & words) + 1 * len(ctx & words)
            + 1 * len(tags & (mech | ctx)))


def ranked(cases_dir, query):
    scored = [(c["id"], score(c, query)) for c in load_cases(cases_dir)]
    return sorted([(i, s) for i, s in scored if s > 0],
                  key=lambda p: (-p[1], p[0]))


def render_public(case):
    import copy
    return {k: copy.deepcopy(v) for k, v in case.items()
            if k != "restricted"}


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="rank incident cases")
    ap.add_argument("--cases", required=True)
    ap.add_argument("--tags", default="")
    ap.add_argument("--text", default="")
    args = ap.parse_args(argv)
    query = {"tags": [t for t in args.tags.split(",") if t],
             "text": args.text}
    for cid, s in ranked(args.cases, query):
        print("%s %d" % (cid, s))


if __name__ == "__main__":
    main()
