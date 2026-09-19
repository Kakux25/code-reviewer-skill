# Review: case-a (percentage discounts)

Scope: candidate vs base; objective is to apply 0–100% discounts while preserving the public API. Change type: feature addition. Note: the diff was seen before the rubric was frozen, so this is not a blind assessment; every criterion below was checked against the base.

## Decision

**Changes requested** — the discount divisor corrupts every nonzero-discount total (verified by execution).

## Findings

- P1, candidate/prices.py:4 — divides `discount_percent` by 10 instead of 100, so `quote(200, 10)` returns 0.0, `quote(200, 50)` returns -800.0, and `quote(200, 100)` returns -1800.0; proof: `test_percent_examples` fails on all three nonzero subcases (execution). Fix: `return amount * (1 - discount_percent / 100)`.

No other findings. Range validation (`ValueError` for -1/101) is preserved and passes; `checkout.py` is unchanged.

## Verdicts

- Architecture: **High** — primary axis "calculation stays in prices.py with the public signature `quote(amount, discount_percent=0)` and no I/O dependency" (base: ARCHITECTURE.md, base/prices.py:1, base/checkout.py:1-5) is preserved by candidate/prices.py:1-4; no gaps.
- Soul: **Unverifiable** — the repository documents architecture only (ARCHITECTURE.md); no essence/manifesto source exists to assess against.

## Checks and limits

- Ran `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=candidate python3 -m unittest discover -s tests -v`: 1 pass (`test_invalid_discount`), 1 test with 3 subcase failures (`test_percent_examples` for discounts 10/50/100).
- Ran same suite with `PYTHONPATH=base` for comparison: identical 3 subcase failures (base ignores discounts entirely), confirming the candidate introduces a new corruption mode (negative/zero totals) rather than fixing the base.
- Static review: full diff of prices.py and checkout.py; traced consumer `checkout()` which delegates directly, so all discounted checkouts are affected.
- Limits: no additional scope requested; no essence documents available.
