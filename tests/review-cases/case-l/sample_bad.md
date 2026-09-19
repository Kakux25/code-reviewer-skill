# Sample review: case-l (BAD — synthetic, must FAIL: dict-order suspicion)

**Decision**: Changes requested — dicts may reorder.

**Findings**:
- P1, candidate/dedup.py:2 — dict.fromkeys relies on dict ordering, which may scramble the output order. Fix: restore the explicit scan.

**Verdicts**: architectural `Acceptable` (mechanism changed); soul `Unverifiable`.

**Checks and limits**: ran test_dedup.py with PYTHONPATH on candidate — all pass.
