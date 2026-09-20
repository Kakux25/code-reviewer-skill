# Case Q — Review (candidate vs base)

Scope: `blind/case-q` — base (`base/expr.py`, `base/ARCHITECTURE.md`) vs candidate (`candidate/expr.py`); acceptance examples in `tests/test_expr.py`. Full root: `evals/runs/2026-09-20-battery-smoke/blind/case-q/`.

## Decision

`Changes requested` — candidate evaluates untrusted input with `eval`, executing arbitrary code and violating the documented safety contract.

## Findings

- P0, `candidate/expr.py:2` — `return eval(text)` on untrusted input executes arbitrary code (violates `base/ARCHITECTURE.md:4` "must never execute arbitrary code"); proof (execution): `calc('(__import__("os").name)')` → `'posix'`, `calc('[i*i for i in range(3)]')` → `[0, 1, 4]`. Fix: replace `eval` with a restricted numeric/arithmetic parser (e.g. validated AST evaluator) that never executes code or imports.
- P2, `candidate/expr.py:2` — breaks the `calc(text) -> float` contract (`base/ARCHITECTURE.md:3`, `base/expr.py:1-2` always returns `float`): proof (execution): `calc("2+3")` → `5` of type `int`, and non-numeric inputs return arbitrary objects (list/str) instead of a float or an error. Fix: coerce valid results with `float(...)` and reject non-numeric input (raise `ValueError`).

## Verdicts

- Architecture: `Low` — primary-axis violation (untrusted-input safety: "evaluation must never execute arbitrary code"); change type: feature addition (arithmetic evaluation); rubric axes: (P1) no-code-execution violated, (S1) float-return contract violated. Complexity: Low (invariant is explicit in `ARCHITECTURE.md`, single call path).
- Soul: `Unverifiable` — no essence/manifesto/canon documented (`ARCHITECTURE.md` states architecture, not identity); nothing to assess against.

## Checks and limits

- Correctness (functional, separate from architecture): acceptance examples PASS — `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.../blind/case-q/candidate python3 -m unittest discover -s .../blind/case-q/tests -v` → `Ran 1 test ... OK`; passing examples do not cover untrusted-input safety or return-type strictness.
- Security/contract probes (execution, same env): `calc('2+3')` → `(5, int)`; `calc('1.5')` → `(1.5, float)`; `calc('(__import__("os").name)')` → `'posix'`; `calc('[i*i for i in range(3)]')` → `[0, 1, 4]`.
- Static: `trace_callers.py calc .../blind/case-q` → defs in `base/expr.py:1` and `candidate/expr.py:1`; call sites only in `tests/test_expr.py:7-8`; no other consumers in scope.
- Skipped: `pytest .../tests/test_expr.py` not run — `No module named pytest` (used `unittest` instead).
- Limits: rubric built from base + `ARCHITECTURE.md`; candidate seen per task order (request → base → candidate → tests), so no independent-blind claim; no callers beyond the case suite inspected.
