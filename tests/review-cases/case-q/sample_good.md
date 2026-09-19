# Sample review: case-q (GOOD — synthetic, must PASS)

**Decision**: Changes requested — user input is executed as code.

**Findings**:
- P1, candidate/expr.py:2 — `eval(text)` on untrusted input allows arbitrary code execution; `calc("__import__('os')...")` would run. Proof: static. Fix: parse numbers only (e.g. `ast.literal_eval` or `float`).

**Verdicts**: architectural `High` (single function, no gaps); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: ran test_expr.py with PYTHONPATH on candidate — suite passes (benign inputs), which does not excuse the execution hole.
