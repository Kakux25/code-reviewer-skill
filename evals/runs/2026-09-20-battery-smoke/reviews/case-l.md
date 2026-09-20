# Case L — Review (brief)

Scope: base vs candidate under `evals/runs/2026-09-20-battery-smoke/blind/case-l`; objective: deduplicate faster while preserving first-seen order. Change type: refactoring (performance optimization; quadratic scan explicitly an implementation detail per `base/ARCHITECTURE.md:3-4`).

## Decision

`Changes requested` — candidate raises `TypeError` on unhashable inputs that base handles, narrowing the input contract.

## Findings

- P2 `candidate/dedup.py:2` — `dict.fromkeys(xs)` requires hashable items, so e.g. `dedup([[1],[2],[1]])` raises `TypeError` where base (`base/dedup.py:1-6`, equality scan) returns `[[1],[2]]`; proof: execution (base returned `[[1],[2]]`, candidate raised `TypeError: unhashable type: 'list'`) (high confidence). Smallest fix: keep the fast path with an equality-scan fallback on `TypeError`, or explicitly document a hashable-only contract if the narrowing is intended.

## Verdicts

- Architecture: `High with concerns` — primary axis (first-seen-order dedup per `base/ARCHITECTURE.md:3-4` and `tests/test_dedup.py:6-11`) preserved for documented/hashable inputs; gap on secondary axis (input generality): unhashable inputs now raise instead of deduping. Complexity: `Low` (single pure function, no cross-component coordination; not trivial — semantic effect exists).
- Soul: `Unverifiable` — no documented essence (no philosophy/manifesto/canon; `ARCHITECTURE.md` states contract/architecture only).

## Checks and limits

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.../blind/case-l/candidate python3 -m unittest discover -s .../blind/case-l/tests -v` → 2 tests ran, OK.
- Base-vs-candidate unhashable repro (`dedup([[1],[2],[1]])`) → base `[[1],[2]]`, candidate `TypeError` (see Finding).
- `trace_callers.py dedup .../blind/case-l` → only `base/dedup.py:1` and `candidate/dedup.py:1` defs plus hashable test calls in `tests/test_dedup.py:7,10,11`; no unhashable caller in scope.
- Limits: no callers beyond the case tests in scope, so real-world unhashable use is unknown; dict insertion-order guarantee assumes Python 3.7+; rubric criteria taken from base only (candidate viewed per task order before write-down; no blind-assessment claim beyond answer-key blindness).
