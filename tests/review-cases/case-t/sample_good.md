# Sample review: case-t (GOOD — synthetic, must PASS)

**Decision**: Changes requested — served rows alias the cache.

**Findings**:
- P1, candidate/cache.py:5 — `return _CACHE[key]` serves the cached list by reference with no defensive copy, so caller mutation corrupts the cache. Proof: `test_caller_mutation_isolated` fails. Fix: return `list(_CACHE[key])`.

**Verdicts**: architectural `High` (single function, no gaps); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: ran test_cache.py with PYTHONPATH on candidate — FAILED.
