# Review: case-a (percentage discounts)

1. **Decision**: `Changes requested` — the discount divisor corrupts every nonzero total.
2. **Findings**:
   - P1, candidate/prices.py:4 — divides `discount_percent` by 10 instead of 100, so any nonzero discount over-discounts (large discounts go negative); proof by execution: `quote(200, 10)=0.0` (expected 180), `quote(200, 50)=-800.0` (expected 100), `quote(200, 100)=-1800.0` (expected 0); fix: `return amount * (1 - discount_percent / 100)`.
3. **Verdicts**:
   - Architecture: `High` — no gaps; rubric v1 primary axes hold (public signature `quote(amount, discount_percent=0)` and range validation preserved per base/prices.py:1-3; calculation stays in prices.py with no I/O dependency and checkout.py still delegates per base/checkout.py:4-5 and base/ARCHITECTURE.md).
   - Soul: `Unverifiable` — no documented essence (manifesto/principles) in scope to assess against.
4. **Checks and limits**:
   - Ran `PYTHONPATH=candidate PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`: `test_invalid_discount` passed; `test_percent_examples` failed on discounts 10/50/100 (0/200 passed).
   - Static review of base and candidate `prices.py`/`checkout.py`, `base/ARCHITECTURE.md`, and `tests/test_prices.py`.
   - Limits: no consumers beyond `checkout.py` traced; no other scope reviewed.
