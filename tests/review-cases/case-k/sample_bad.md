# Sample review: case-k (BAD — synthetic, must FAIL: false positive)

**Decision**: Changes requested — the loop was removed.

**Findings**:
- P2, candidate/stats.py:1 — total no longer accumulates in a loop, so the summation logic is gone. Fix: restore the loop.

**Verdicts**: architectural `Acceptable` (mechanism changed); soul `Unverifiable`.

**Checks and limits**: ran test_stats.py with PYTHONPATH on candidate — all pass.
