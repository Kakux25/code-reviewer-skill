## Review: case-a (blind; answer key not opened)

**Scope:** base → candidate in `tests/review-cases/case-a`; objective from `request.md`: apply percentage discounts 0–100 while preserving the public API. No files modified.

**Rubric v1** (frozen from base + request + tests, before opening candidate):
- A1 (primary, architectural): calculation placement and dependency direction — amount logic lives in `prices.py` with no I/O-infra dependency; `checkout.py` adapts and delegates. Preserve: logic in `prices.py`, no I/O imports, delegation intact. Violate: logic moved out of `prices.py` or I/O imports added to it.
- A2 (primary, architectural): public signature `quote(amount, discount_percent=0)` importable from `prices` stays stable. Preserve: same signature/defaults. Violate: rename, reparam, or removed default breaking `checkout.py`/consumers.
- Functional contract (assessed separately, not an architectural axis): `quote(200, d)` == 200/180/100/0 for d in 0/10/50/100; `ValueError` outside 0–100 (per `tests/test_prices.py`).

**Diff:** `checkout.py` identical to base. Only change is `candidate/prices.py:4`: `return amount * (1 - discount_percent / 10)`.

### Brief report

1. **Decision: `Changes requested`** — one P1 functional defect corrupts every nonzero-discount total (decisive reason).
2. **Findings:**
   - P1, `candidate/prices.py:4` — divisor `/10` instead of `/100`: any `discount_percent != 0` corrupts the total (e.g. `quote(200,10)=0.0`, `quote(200,50)=-800.0`, `quote(200,100)=-1800.0` vs expected 180/100/0; proof: execution below). No guard or caller compensates (`checkout.py` passes through unchanged). Smallest fix: `/ 100`. High confidence.
3. **Verdicts:**
   - Architectural verdict: `High` — A1 preserved (arithmetic in `prices.py`, no new imports; `checkout.py` delegation unchanged) and A2 preserved (signature identical); gap list empty. The divisor bug is functional, not structural.
   - Soul verdict: `Unverifiable` — no essence/manifesto/ADR/principles document in scope (`ARCHITECTURE.md` states mechanisms, not identity); nothing to assess against.
4. **Checks and limits:**
   - `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests/review-cases/case-a/candidate python3 -m unittest discover -s tests/review-cases/case-a/tests -v` → Ran 2 tests, FAILED (3 subtest failures: discounts 10/50/100; `test_invalid_discount` passed).
   - Direct probe `quote(200,d)` for d in 0/10/50/100 → `[200.0, 0.0, -800.0, -1800.0]`, expected `[200, 180, 100, 0]`.
   - `pytest` attempt skipped: module not installed; reran via `unittest` (above).
   - Static: full candidate-vs-base diff inspected (2 files); `trace_callers.py` not needed — single caller `checkout()` verified by read.
   - Complexity: `Low` (one pure function, one delegation edge, no shared state; semantic effect on money totals rules out `Trivial`).

**Verdict lines:** Decision `Changes requested`; Architectural verdict `High`; Soul verdict `Unverifiable`.
