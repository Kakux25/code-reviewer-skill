# Case T — Review of `candidate/cache.py` against `base`

## Decision

`Changes requested` — the candidate breaks the documented isolation contract: callers can corrupt the cache by mutating a served value (acceptance test fails).

## Findings

- P1, `candidate/cache.py:5` — `get` returns the live cached list (`return _CACHE[key]`) instead of an independent copy, so any caller-side mutation (e.g. `.append`) permanently corrupts `_CACHE` for all later callers. Proof (execution): `test_caller_mutation_isolated` fails on the candidate (`[1, 2, 99] != [1, 2]`) while the base passes 2/2. Trigger is broad — nothing tells callers the value is shared — so P1, not P2. Smallest fix: `return list(_CACHE[key])` (restore base behavior).

No other findings. Public API shape (`get(key)`, `KeyError` on missing key) is unchanged, and `test_values` passes.

## Verdicts

- Architecture: `Low` — primary-axis violation: A1 (caller isolation, base `ARCHITECTURE.md:3-4` + `base/cache.py:5`) is directly broken by returning the shared mutable; gap G1. Change type: refactoring (simplification of `get`); rubric v1; complexity `Low` (single function, one invariant, fully exercised by tests). Note: the candidate was seen before the rubric was written (instructed read order), so this is not a blind assessment; every criterion was checked against the base.
- Soul: `Unverifiable` — no philosophy, manifesto, canon, ADR, or README essence statement in scope; `ARCHITECTURE.md` states an architectural contract, not project essence.

## Checks and limits

- `PYTHONPATH=candidate python3 -m unittest discover -s tests`: 1 pass, 1 fail (`test_caller_mutation_isolated` FAIL, `[1, 2, 99] != [1, 2]`).
- `PYTHONPATH=base python3 -m unittest discover -s tests`: OK (2/2) — confirms the failure is a regression introduced by the candidate.
- `scripts/trace_callers.py get blind/case-t`: only definitions (`base/cache.py:4`, `candidate/cache.py:4`) and test call sites; no other in-scope consumers.
- Static diff: base `return list(_CACHE[key])` vs candidate `return _CACHE[key]` — the only change.
- Limits: scope restricted to `blind/case-t` materials (base, candidate, tests); no out-of-scope callers or production consumers assessed; no essence documents available.
