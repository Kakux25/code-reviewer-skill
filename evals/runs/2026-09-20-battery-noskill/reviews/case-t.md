# Code Review — Case T

Decision: Changes requested

## Findings

- [P0] `candidate/cache.py:5` — `get()` returns the live cached list (`return _CACHE[key]`) instead of an independent copy. Any caller mutation (e.g. `.append()`) permanently corrupts `_CACHE`, violating the stated isolation contract. Base (`base/cache.py:5`) returned `list(_CACHE[key])`; the candidate drops that copy. Fix: restore the defensive copy (`return list(_CACHE[key])`).

## Architecture verdict

Architecture verdict: Acceptable

## Soul verdict

Soul verdict: Betrayed

## Checks and limits

- Ran candidate suite: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="evals/runs/2026-09-20-battery-noskill/blind/case-t/candidate" python3 -m unittest discover -s "evals/runs/2026-09-20-battery-noskill/blind/case-t/tests" -v` → 1 pass, 1 FAIL (`test_caller_mutation_isolated`: got `[1, 2, 99]`, expected `[1, 2]`).
- Ran base suite with same tests for comparison: `PYTHONPATH=".../blind/case-t/base" python3 -m unittest discover -s ".../blind/case-t/tests"` → 2/2 OK, confirming this is a candidate-introduced regression.
- Aliasing probe: `cache.get('a') is cache._CACHE['a']` on candidate → `True`, confirming the returned value aliases the cache entry.
- Limits: reviewed only `request.md`, `base/`, `candidate/`, `tests/` under `blind/case-t` per blindness rules; no other sources consulted. Nested-element (deep-copy) isolation was not exercised by the suite and was not probed beyond the top-level list contract.
