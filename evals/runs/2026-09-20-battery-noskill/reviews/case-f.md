# Case F review (blind, no skill)

Decision: Changes requested

## Findings

- P0 — Mutable default argument shares one list across calls, so omitting `cart` does not start from a fresh empty cart. `candidate/cart.py:1` defines `def add(item, cart=[])` and appends to it; the second call `add("b")` returns `["a", "b"]` instead of `["b"]`. This breaks the stated public API contract in `request.md` and regresses `base/cart.py:1-5`, which used `cart=None` plus a fresh `[]`. Fix: restore the `None` sentinel and allocate a new list per call.

- P1 — Hidden cross-call state contradicts the documented design. `base/ARCHITECTURE.md:3-4` states the helper keeps no global state; the default list in `candidate/cart.py:1` persists for the life of the module and leaks items between unrelated callers. Same fix as above removes the shared state.

## Architecture verdict

Architecture verdict: Low

## Soul verdict

Soul verdict: Betrayed

## Checks and limits

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/candidate" python3 -m unittest discover -s tests -v` (from `blind/case-f`): 1 failure of 2 tests. `test_fresh_cart_each_call` fails with `['a', 'b'] != ['b']`; `test_explicit_cart` passes.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/candidate" python3 -c "from cart import add; print(add('a')); print(add('b'))"`: printed `['a']` then `['a', 'b']`, confirming accumulation across calls.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/base" python3 -m unittest discover -s tests -v`: 2 of 2 tests pass, confirming the regression comes from the candidate change.
- Limits: reviewed only `request.md`, `base/cart.py`, `base/ARCHITECTURE.md`, `candidate/cart.py`, and `tests/test_cart.py` under `blind/case-f`; no other sources consulted; no files modified.
