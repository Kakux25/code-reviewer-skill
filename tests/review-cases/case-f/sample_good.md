# Sample review: case-f (GOOD — synthetic, must PASS)

**Decision**: Changes requested — carts share state across calls.

**Findings**:
- P1, candidate/cart.py:1 — `cart=[]` is a mutable default argument, so the same list is shared and state leaks across calls: the second `add("b")` returns `["a", "b"]`. Proof: `test_fresh_cart_each_call` fails. Fix: default to `None` and build a fresh list.

**Verdicts**: architectural `High` (single helper, no gaps); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: ran test_cart.py with PYTHONPATH on candidate — FAILED.
