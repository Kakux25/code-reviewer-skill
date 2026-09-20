# Case L review

## Decision

`No actionable findings` — the candidate preserves the contracted behavior (first-seen-order dedup on hashable inputs) and passes the full acceptance suite.

## Findings

None. No defects, regressions, or contract violations identified within scope.

Note (not a finding): `candidate/dedup.py:2` (`dict.fromkeys`) raises `TypeError` on unhashable elements where `base/dedup.py:4` (`x not in out`) tolerated them — but `request.md` explicitly excludes unhashable input from the contract, and `base/ARCHITECTURE.md:4` declares the quadratic scan an implementation detail, so this is a permitted tradeoff, not a regression.

## Verdicts

- Architecture: `High` — primary axis (first-seen order preserved, duplicates removed, new list returned) holds via `candidate/dedup.py:1-2`; no gaps. Change type: performance-preserving refactoring; rubric v1 built from `base/dedup.py` + `base/ARCHITECTURE.md` before assessing the candidate.
- Soul: `Unverifiable` — no manifesto, canon, ADR, or principles document in scope; `ARCHITECTURE.md` states mechanism/contract, not essence.

## Checks and limits

- `PYTHONPATH=<case-l/candidate> python3 -m unittest discover -s <case-l/tests> -v` → 2/2 pass (`test_order_kept`, `test_empty_and_single`).
- Sanity probe on candidate: `dedup([3,1,3,2,1])==[3,1,2]`, `dedup([])==[]`, `dedup(['a'])==['a']`, tuple input returns deduped list — all as expected (execution evidence).
- `pytest` run skipped: `No module named pytest` in this environment; `unittest` covers the same suite, so no confidence lost.
- Limits: no callers beyond the suite exist in scope (single-function module; no wider trace needed); unhashable-input behavior intentionally not verified (out of contract); complexity `Trivial` — one-line, no shared state or compatibility surface.
