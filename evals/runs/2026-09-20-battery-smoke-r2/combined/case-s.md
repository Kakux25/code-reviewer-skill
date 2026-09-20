# Review: case-s — authorize known users including id 0

## 1. Decision

`Changes requested` — candidate denies the valid pre-provisioned operator (id 0), breaking the core acceptance example.

## 2. Findings

- P1, `candidate/auth.py:5` — cause: `bool(user_id)` is `False` for `0`, so `allowed(0)` returns `False` despite `0` being in `USERS`. Proof (execution): `test_operator_zero` FAILS on candidate (`AssertionError: False is not true`). Fix: `return user_id is not None and user_id in USERS` (match `base/auth.py:4-5`).

No other findings. No open questions.

## 3. Verdicts

- Architecture: `Low` — change type: bug fix (objective: authorize known ids incl. 0, preserve `allowed(user_id)` API); rubric v1, primary axis A1 "known ids incl. falsy 0 authorized; only None/unknown denied" (base `base/auth.py:4-5`, `base/ARCHITECTURE.md:3`) is violated by the `bool()` guard; gap: operator id 0 denied, no justified tradeoff. Secondary axis A2 "single-module `auth.py` public API preserved" holds.
- Soul: `Unverifiable` — no essence/manifesto/canon documented in the reviewed scope.

## 4. Checks and limits

- Ran: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<case-s/candidate> python3 -m unittest discover -s <case-s/tests> -v` → 2 tests, 1 failure (`test_operator_zero` FAIL, `test_regular_and_unknown` ok); confirms the P1.
- Ran: `pytest <case-s/tests/test_auth.py>` → skipped, `No module named pytest` (unittest used instead, not a pass).
- Ran: `trace_callers.py allowed <case-s>` → defs in `base/auth.py:4` and `candidate/auth.py:4`; call sites only in `tests/test_auth.py:7,10,11,12`; no other consumers to trace.
- Static: compared `candidate/auth.py:5` against `base/auth.py:4-5` and `request.md` (0 valid, only None/unknown denied).
- Limits: scope restricted to blind case-s files (`request.md`, `base/`, `candidate/`, `tests/`); no callers beyond the case suite assessed.
