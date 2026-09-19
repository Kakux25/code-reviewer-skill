# Sample review: case-r (GOOD — synthetic, must PASS)

**Decision**: Changes requested — overclaimed lengths are not rejected.

**Findings**:
- P1, candidate/tls.py:2 — `buf[:claimed_len]` trusts the claimed length with no bounds check, leaking bytes past the payload (Heartbleed pattern). Proof: `test_overclaim_rejected` fails. Fix: raise ValueError when `claimed_len > received`.

**Verdicts**: architectural `High` (single function, no gaps); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: ran test_tls.py with PYTHONPATH on candidate — FAILED.
