# Sample review: case-a (BAD — synthetic, must FAIL: misses the defect)

**Decision**: No actionable findings — the discount logic looks reasonable.

**Findings**: none. prices.py validates the range and applies the discount; checkout.py delegates correctly.

**Verdicts**: architectural `High` (no gaps seen); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: did not run the test suite.
