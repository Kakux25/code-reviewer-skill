# Sample review: case-b (BAD — synthetic, must FAIL: false positive)

**Decision**: Changes requested — the candidate drops input validation.

**Findings**:
- P1, candidate/registry.py:8 — register_many no longer checks isinstance(pairs, list), so invalid input reaches the loop. Fix: restore the list gate.

**Verdicts**: architectural `Acceptable` (mechanism changed); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: ran test_registry.py with PYTHONPATH on candidate — all pass.
