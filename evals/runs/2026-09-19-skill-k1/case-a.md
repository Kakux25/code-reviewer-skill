# Review: case-a — percentage discounts

Scope: base (`tests/review-cases/case-a/base`) vs candidate (`tests/review-cases/case-a/candidate`); objective is to apply 0–100% discounts while preserving the public API. Change type: feature addition.

## 1. Decision

**Changes requested** — every nonzero discount corrupts the total (wrong divisor, P1 below).

## 2. Findings

- **P1** `candidate/prices.py:4` — divides `discount_percent` by 10 instead of 100, so `quote(200, 10)` returns `0.0` (expected 180), `quote(200, 50)` returns `-800.0` (expected 100), `quote(200, 100)` returns `-1800.0` (expected 0); any `discount_percent != 0` is wrong. Proof: execution, `test_percent_examples` fails 3/3 nonzero subtests (see Checks). Fix: `return amount * (1 - discount_percent / 100)`.

No other findings. Range validation (`ValueError` on `-1`/`101`) is preserved and passes; `checkout.py` is unchanged and still delegates to `quote`.

## 3. Verdicts

- **Architecture: `High`** — rubric v1, no gaps: (A1, primary) public contract `quote(amount, discount_percent=0)` + out-of-range `ValueError` preserved per `base/prices.py:1-3` and `ARCHITECTURE.md`; (A2, primary) calculation stays in `prices.py` with no new dependencies and `checkout.py` still delegates per `ARCHITECTURE.md` and `base/checkout.py:4-5`. Disclosure: candidate was seen before the rubric was frozen; every criterion was checked against the base.
- **Soul: `Unverifiable`** — no essence/manifesto/canon document in scope; `ARCHITECTURE.md` states structure, not identity.

## 4. Checks and limits

- Ran `PYTHONPATH=.../case-a/candidate PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_prices -v` → FAILED (2 tests, 3 subtest failures: `0.0 != 180`, `-800.0 != 100`, `-1800.0 != 0`; `test_invalid_discount` passed).
- Static review: `base/{ARCHITECTURE.md,checkout.py,prices.py}`, `candidate/{checkout.py,prices.py}`, `tests/test_prices.py`.
- Limits: no callers beyond `checkout.py` traced; no float/rounding edge cases beyond the acceptance examples checked.
