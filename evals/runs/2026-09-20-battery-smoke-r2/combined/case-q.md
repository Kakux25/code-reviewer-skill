# Review: case-q — safe numeric evaluation of untrusted input

## Decision

`Changes requested` — candidate executes arbitrary code on untrusted input (P0).

## Findings

- P0, candidate/expr.py:2 — `return eval(text)` executes caller-controlled input as Python code, violating the request.md requirement that evaluation "must never execute arbitrary code". Proof (execution): `calc('__import__("os").getcwd()')` returned `'/Users/jesussevillano/Projects/code-reviewer-skill/evals/runs/2026-09-20-battery-smoke-r2/blind/case-q'`, i.e. the import ran. Same line also breaks the `calc` returns-float contract: `calc('2+3')` returns `int 5`, and non-numeric input returns arbitrary objects (e.g. `str` above). Fix: replace `eval` with a safe numeric parser (restricted expression evaluator, no `eval`/`exec`/`compile`), and return `float(...)` of the result. High confidence.

No other findings. The P0 groups both symptoms (code execution, non-float return) since they share the single root cause (`eval`).

## Verdicts

- Architecture: `Low` — primary-axis violation: A1 (untrusted input is never executed as code; base evidence `float(text)` in base/expr.py:1-2 parses without executing) is breached by `eval(text)` at candidate/expr.py:2; gap G1 with executed PoC above. A2 (returns `float`, base ARCHITECTURE.md + base/expr.py:2) also breached (gap G2: `int`/`str` returns, same cause). A3 secondary (single module, no imports) preserved. Change type: feature addition; rubric v1. Complexity: `Low` (single-function change, no cross-component coordination, security-critical invariant).
- Soul: `Unverifiable` — no essence/manifesto/ADR in scope; base/ARCHITECTURE.md states contract and structure only, not project identity.

## Checks and limits

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<case-q>/candidate python3 -m unittest discover -s tests -v` → 1 test (`tests/test_expr.py:6-8`), OK; covers only `"1.5"`/`"2+3"` numerics, not safety or return type, so the pass does not support acceptance.
- Read-only PoC `calc('__import__("os").getcwd()')` and `calc('2+3')` → arbitrary import executed (returned cwd string); `2+3` returned `int 5`. No files modified.
- `trace_callers.py calc <case-q>` → defs in base/expr.py:1 and candidate/expr.py:1; call sites only in tests/test_expr.py:7-8; no other consumers in scope.
- Limits: reviewed only request.md, base (ARCHITECTURE.md, expr.py), candidate expr.py, and tests/test_expr.py; base behavior assessed statically; no assessment of callers outside the case directory.
