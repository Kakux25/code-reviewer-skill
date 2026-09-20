Review of `tests/review-cases/case-a` candidate vs base (brief format). Note on method: I saw the one-line diff while assembling the rubric below, so this is not a blind assessment; every criterion was checked against the base revision (`base/prices.py`, `base/checkout.py`, `base/ARCHITECTURE.md`) and the acceptance suite. I did not open `answer-key.json`.

**Decision: `Changes requested`** — execution-proven P1: every nonzero discount corrupts totals.

**Findings**

- P1, `candidate/prices.py:4` — wrong percentage divisor (`/10` instead of `/100`). Trigger: any `discount_percent != 0`. Consequence: totals wrong and negative for discounts >10 (quote(200,10)=0.0, quote(200,50)=-800.0, quote(200,100)=-1800.0), propagating through `checkout.py:5` to all consumers. Proof: execution — `test_percent_examples` fails 3/4 subtests (see Checks). Fix: `return amount * (1 - discount_percent / 100)`. High confidence. This is a regression introduced by the candidate (base returned `amount` unscaled); range validation (`ValueError` outside 0..100) is preserved and `test_invalid_discount` passes.

**Architecture** — change type: feature addition (apply 0–100% discounts); rubric v1, frozen against base:
- A1 (primary, placement/boundaries): amount math lives in `prices.py` with no I/O dependency; `checkout.py` adapts requests and delegates via `quote(amount, discount_percent=0)` — preserved: math stays in `prices.py:4`, no imports added, signature and delegation unchanged.
- A2 (secondary, API stability): public signature `quote(amount, discount_percent=0)` unchanged — preserved.
- Gaps: none. The divisor error is a functional defect inside the correct module, not a structural violation, so it does not appear as an architectural gap. Complexity: `Low` (single expression, one caller, but semantically effective).

**Soul** — no manifesto, canon, ADR, or README principles in scope (`ARCHITECTURE.md` states structure, not essence); no statements derived.

**Checks and limits**
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=candidate python3 -m unittest discover -s tests -v` → FAILED (failures=3): `test_invalid_discount` ok; `test_percent_examples` fails for discounts 10/50/100 (`0.0 != 180`, `-800.0 != 100`, `-1800.0 != 0`).
- Direct probe `quote(200,d)` for d in (0,10,50,100) → `[200.0, 0.0, -800.0, -1800.0]`; base suite not re-run (base behavior read statically).
- Scope: full diff (`prices.py` one line; `checkout.py` identical); no files outside scope; no essence to verify against.

Architectural verdict: `High` — no primary-axis violations; boundaries, placement, and API preserved.
Soul verdict: `Unverifiable` — no documented essence to assess against.
