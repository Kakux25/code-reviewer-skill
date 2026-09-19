# Sample review: case-c (BAD — synthetic, must FAIL: finding without contract)

**Decision**: Changes requested — the snippet crashes on None.

**Findings**:
- P2, snippet.py:2 — normalize_name calls value.strip() without a None guard, raising AttributeError on None input. Fix: add `if value is None` handling.

**Verdicts**: architectural `High` (simple and clean); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: static read only.
