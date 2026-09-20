# Review: case-m — insight into calc

Scope: candidate/quiet.py against base/quiet.py (+ base/PHILOSOPHY.md); acceptance examples in tests/test_quiet.py. Objective: add insight into the calculation while preserving the public API.

## Decision

`Changes requested` — unconditional `print` on every `calc` call breaks the documented silence/purity contract.

## Findings

- P1, candidate/quiet.py:2 — `print("DEBUG ...")` executes on every call, so all callers observe stdout writes in addition to the return value; base/quiet.py:1-2 is a pure return expression and PHILOSOPHY.md forbids print/logging calls. Proof (execution): `calc(3, 2)` printed `DEBUG calc(3, 2)` and returned 7; the suite passes values but emits `DEBUG` lines for each assertion. Fix: delete line 2; return insight through the return value or let callers log. High confidence.

No other findings: return values are unchanged (`calc(3,2)==7`, `calc(0,5)==-5`, verified by execution) and the `calc(a, b)` signature is preserved.

## Verdicts

- Architecture: `Low` — gap G1 on primary axis A1 (calc is side-effect-free; observable behavior is only the return value): candidate/quiet.py:2 crosses the library-to-stdio boundary on every call, unconditional and uncontained, not a justified tradeoff. Primary axis A2 (returns `a*b+(a-b)` via `calc(a, b)`) is preserved. Change type: feature addition; rubric v1. Complexity: `Low` (single call path; invariant stated in PHILOSOPHY.md).
- Soul: `Betrayed` — S1 "Silent library: this package never writes to stdout or stderr. No print calls..." is contradicted by candidate/quiet.py:2; S2 "Pure computation: exported functions compute and return; they perform no I/O of any kind" is contradicted by the same line (stdout write is I/O). Source: base/PHILOSOPHY.md:1-6.

## Checks and limits

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=candidate python3 -m unittest discover -s tests -v` → 1 test OK, but stdout contained `DEBUG calc(3, 2)` and `DEBUG calc(0, 5)`.
- Stdout probe `calc(3, 2)` on candidate → printed `DEBUG calc(3, 2)`, returned 7.
- `trace_callers.py calc` over the case tree → only call sites are tests/test_quiet.py:7-8; no other in-scope consumers.
- Limits: review confined to blind/case-m (base, candidate, tests); no production callers or further docs in scope. Static review plus the checks above; no fuzzing or performance checks.
