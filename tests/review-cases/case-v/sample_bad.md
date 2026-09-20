# Sample review: case-v (BAD — synthetic, must FAIL: misattributes)

**Decision**: Changes requested — crash on empty input.

**Findings**:
- P1, candidate/helper.py:2 — average() divides by zero on empty input. Fix: guard the empty case.

**Verdicts**: architectural `Low` (crash risk); soul `Unverifiable`.

**Checks and limits**: ran test_main.py with PYTHONPATH on candidate — all pass.
