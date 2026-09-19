# Sample review: case-a (GOOD — synthetic, for grader self-test)

**Decision**: Changes requested — the discount divisor is wrong and corrupts every nonzero total.

**Findings**:
- P1, candidate/prices.py:4 — divides by 10 instead of 100: `discount_percent / 10` makes quote(200, 10) return 0 instead of 180. Proof: ran tests/test_prices.py against the candidate, test_percent_examples fails. Fix: divide by 100.
- Architecture assessed separately below; checkout.py delegation is unchanged and correct.

**Verdicts**: architectural `High` (calculation stays in prices.py, no I/O added, public signature kept); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: ran test_prices.py with PYTHONPATH on candidate — 1 failure as cited. Did not modify files.
