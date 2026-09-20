# Case F — Review (candidate vs base)

## Decision

`Changes requested` — every omitted-cart call after the first returns polluted results (mutable default argument), failing the acceptance suite.

## Findings

- P1, candidate/cart.py:1 — `def add(item, cart=[])` shares one default list across all omitted-cart calls, so `add("b")` after `add("a")` returns `['a', 'b']` instead of `['b']`. Proof: execution, `test_fresh_cart_each_call` FAILs on candidate (`AssertionError: ['a', 'b'] != ['b']`), passes on base (2/2 OK). Fix: restore the `None` sentinel (`def add(item, cart=None): if cart is None: cart = []`).

Note: rubric was built from base/cart.py and ARCHITECTURE.md after the candidate had already been seen (small isolated case); every criterion below was checked against the base, not derived from the patch.

## Verdicts

- Architecture: `Low` — primary axis violated: base guarantees "no global state" with a fresh cart per omitted call (base/cart.py:1-3, ARCHITECTURE.md:3-4); the candidate's shared mutable default is hidden cross-call state affecting every consumer. Change type: refactoring; rubric v1; gaps: [primary/no-shared-state: candidate/cart.py:1 shares default list; impact: all omitted-cart calls after the first corrupt]. Complexity: `Trivial` (single pure helper, defect localized to one default value).
- Soul: `Unverifiable` — no essence/manifesto document in scope (ARCHITECTURE.md states mechanism, not identity).

## Checks and limits

- Ran `PYTHONPATH=.../blind/case-f/candidate python3 -m unittest discover -s .../blind/case-f/tests -v`: 1 pass, 1 FAIL (`test_fresh_cart_each_call`).
- Ran same suite with `PYTHONPATH=.../blind/case-f/base`: 2/2 OK (confirms regression, not pre-existing).
- Ran `trace_callers.py add` over `blind/case-f`: only defs in base/candidate and the three test call sites; no other consumers in scope.
- Scope: base (ARCHITECTURE.md, cart.py), candidate (cart.py), tests/test_cart.py, request.md. No callers outside the case; no further checks omitted that could change the findings.
