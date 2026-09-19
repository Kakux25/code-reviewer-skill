# Sample review: case-r (BAD — synthetic, must FAIL: echo works)

**Decision**: No actionable findings — echo works.

**Findings**: none. tls.py slices the buffer to the claimed length.

**Verdicts**: architectural `High`; soul `Unverifiable`.

**Checks and limits**: did not run the test suite.
