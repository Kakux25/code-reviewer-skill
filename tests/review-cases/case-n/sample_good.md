# Sample review: case-n (GOOD — synthetic, must PASS)

**Decision**: Changes requested — validation mutates its input.

**Findings**:
- P1, candidate/check.py:2 — `rows.sort()` mutates the caller's list in place, a hidden side effect behind an honest `validate` name. Proof: static (sort is in-place). Fix: sort a copy or drop the sort.

**Verdicts**: architectural `High` (single function, no gaps); soul `Betrayed` — "Honest API: names say what they do ... never mutates its input" (base/PHILOSOPHY.md) is contradicted by the in-place sort.

**Checks and limits**: ran test_check.py with PYTHONPATH on candidate — suite passes (answers unchanged), which does not excuse the betrayal.
