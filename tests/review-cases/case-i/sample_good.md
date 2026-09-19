# Sample review: case-i (GOOD — synthetic, must PASS)

**Decision**: Changes requested — the public signature is broken.

**Findings**:
- P1, candidate/greeter.py:1 — `greet(first, last, ...)` requires two names, breaking the documented single-name signature; every existing caller raises TypeError. Proof: `test_single_name` errors. Fix: keep `greet(name, punct="!")` and split the name inside if needed.

**Verdicts**: architectural `Low` (stable-signature contract violated); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: ran test_greeter.py with PYTHONPATH on candidate — FAILED (TypeError).
