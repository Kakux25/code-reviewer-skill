# Case F — Review (brief)

## Decision

`Changes requested` — the candidate shares one mutable default list across all default-cart calls, so every fresh-cart call after the first returns polluted results.

## Findings

- `P1` candidate/cart.py:1 — `def add(item, cart=[])` reuses the same default list across calls; second default call returns `['a', 'b']` instead of `['b']` (proof: `test_fresh_cart_each_call` FAIL, plus direct repro `add('a')` then `add('b')`). Fix: restore `cart=None` and create a fresh `[]` inside, as in base/cart.py:1-3. High confidence, execution evidence.

## Verdicts

- Architecture: `Low` — primary axis "no shared state; each call with no cart starts empty" (base ARCHITECTURE.md:3-5, base/cart.py:1-3) is violated by the shared mutable default (candidate/cart.py:1); gap: cross-call state leak. Change type: refactoring; rubric v1 (candidate viewed per task order, not a blind assessment); complexity `Low`.
- Soul: `Unverifiable` — no essence/manifesto/canon source in scope; ARCHITECTURE.md states a mechanism-level contract, not project identity.

## Checks and limits

- Ran `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<blind/case-f/candidate> python3 -m unittest discover -s <blind/case-f/tests> -v`: 1 pass, 1 FAIL (`test_fresh_cart_each_call`, `add("b")` gave `['a', 'b']`).
- Ran direct repro `add('a'); add('b')` on candidate: `['a']`, `['a', 'b']` — confirms shared state.
- Ran `trace_callers.py add <blind/case-f>`: only defs in base/candidate plus 3 call sites in tests/test_cart.py — no other consumers in scope.
- Scope: base (ARCHITECTURE.md, cart.py), candidate cart.py, tests/test_cart.py only; no wider repo or production callers available.
