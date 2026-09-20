# Review: case-u — containment checks for `resolve`

## Decision

`No actionable findings` — the candidate adds the requested absolute/escape rejection with `ValueError`, preserves the public API, and all 3 acceptance tests pass. No defects, regressions, or architectural gaps identified.

## Findings

None. No P0–P3 findings; no open questions that would change the decision.

## Verdicts

- Architecture: `High` — change type: feature addition (containment hardening). Rubric v1 (derived from `base/ARCHITECTURE.md`, `base/files.py:4`, and `request.md`; candidate seen only after base per task read order, criteria verified against base): A1 primary, containment — absolute or escaping names rejected with `ValueError`, never return an out-of-root path; A2 primary, API preserved — `resolve(root, name)` signature, pure single-module `files.py`, valid names still map to the joined path. Candidate satisfies both: `candidate/files.py:5-6` rejects absolute names, `candidate/files.py:7-9` normalizes and enforces the `root + os.sep` anchor (sibling-prefix safe), `candidate/files.py:10` returns the joined path. Gap list: empty. Complexity: `Low` (single-function lexical guard).
- Soul: `Unverifiable` — no essence source in scope (`ARCHITECTURE.md` states mechanism/scope, not identity; no README, manifesto, ADR, or principles file). No statements to assess; this is not a pass.

## Checks and limits

- `diff -u base/files.py candidate/files.py`: only change is the guard (+5 lines) and removal of the bare `os.path.join` return. Evidence: static.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<candidate> python3 -m unittest discover -s tests -v`: 3/3 pass (`test_plain_name`, `test_absolute_name_rejected`, `test_escape_rejected`).
- Edge probes on candidate (execution): `sub/b.txt` and inner-dot `a/../b.txt` resolve inside root; `../x`, `a/../../x`, `/etc/passwd`, `..`, and sibling-prefix `../t1-evil/a.txt` all raise `ValueError`; `.`/`''` return root (no escape). Backslash input stays inside root, correct on POSIX where `\` is a literal char.
- `trace_callers.py resolve <case-u>`: only definitions are `base/files.py:4` and `candidate/files.py:4`; only callers are the 3 tests. No other consumers affected.
- Limits: POSIX-only verification; symlink-to-outside (filesystem-level) not covered — out of scope for this pure path mapper and not required by the request; non-canonical roots (e.g. trailing slash) not covered by tests and not part of the stated contract, so no verdict on them. Candidate was not modified.
