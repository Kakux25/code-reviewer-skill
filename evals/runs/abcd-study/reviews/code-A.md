Case A review (generic, blind — answer key not opened).

Scope: `candidate/` vs `base/`, acceptance suite `tests/test_prices.py`.

Change:
- `checkout.py`: identical to base (still adapts request → delegates to `quote`).
- `prices.py` line 4: `return amount` → `return amount * (1 - discount_percent / 10)`.

Findings:

1. Correctness — FAIL (blocking). The divisor is 10 instead of 100, so any nonzero discount is 10× too large. Ran `test_prices.py` read-only (`PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH` → candidate): `test_invalid_discount` passes, `test_percent_examples` fails 3 of 4 subtests — discount=10 gives 0.0 (expected 180), discount=50 gives -800.0 (expected 100), discount=100 gives -1800.0 (expected 0). Only discount=0 passes. The formula also yields negative totals for discounts >10, which is an invalid monetary result. Fix: divide by 100.
2. Architecture — PASS. Public signature `quote(amount, discount_percent=0)` preserved, range validation (`ValueError` for out-of-range) preserved, calculation stays in `prices.py` with no I/O dependency added, and `checkout.py` still delegates per `ARCHITECTURE.md`.

Decision: request changes — one-line fix (`/ 10` → `/ 100`), then re-run the suite. No architectural rework needed.

Verdict: REJECT (incorrect discount math; architecture OK)

