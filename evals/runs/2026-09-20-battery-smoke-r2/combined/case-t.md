# Case T — blind review

## Decision
`Changes requested` — candidate breaks the isolation contract: caller mutation corrupts the shared cache.

## Findings
- `P1` candidate/cache.py:5 — `return _CACHE[key]` returns the live cached list instead of an independent copy; `get("a").append(99)` permanently mutates `_CACHE`, next `get("a")` returns `[1, 2, 99]`. Proof: execution, `test_caller_mutation_isolated` FAIL (`[1, 2, 99] != [1, 2]`). Fix: `return list(_CACHE[key])` as in base/cache.py:5.

## Verdicts
- Architecture: `Low` — primary-axis violation of caller-isolation (base anchor `list(...)` copy at base/cache.py:5; candidate returns alias at candidate/cache.py:5), affecting all consumers of `get`.
- Soul: `Unverifiable` — no essence/manifesto/canon provided in scope; ARCHITECTURE.md states mechanism only.

## Checks and limits
- Ran `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<blind/case-t/candidate> python3 -m unittest discover -s <blind/case-t/tests> -v`: 1 pass (`test_values`), 1 fail (`test_caller_mutation_isolated`).
- Ran `trace_callers.py get` on base and candidate: single `def get` in each; no additional callers in scope.
- Scope: request.md, base/ARCHITECTURE.md, base/cache.py, candidate/cache.py, tests/test_cache.py only; rubric derived from base + request (candidate seen during scoped read).
- Static comparison of base vs candidate; no broader repo consumers available.
