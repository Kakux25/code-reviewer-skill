# Case R Review — heartbeat respond()

Decision: Changes requested

## Findings

- P0 — Missing bounds check allows over-read past received bytes (Heartbleed-style disclosure). `respond` must raise `ValueError` when `claimed_len > received`, but the candidate returns `buf[:claimed_len]` unconditionally, echoing bytes past the payload. — tls.py:1
- P1 — Bounds contract violated: response includes bytes past the payload when `claimed_len > received` (demonstrated: `respond(b"hi" + b"SECRET-PADDING", 2, 16)` returns `b'hiSECRET-PADDING'` instead of raising). — tls.py:2

## Architecture verdict: Low

## Soul verdict: Betrayed

## Checks and limits

Commands run (from workspace root, candidate on PYTHONPATH):

1. `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evals/runs/2026-09-20-battery-noskill/blind/case-r/candidate python3 -m unittest discover -s evals/runs/2026-09-20-battery-noskill/blind/case-r/tests -v`
   - Result: 2 tests ran; `test_exact_echo` passed, `test_overclaim_rejected` FAILED (`AssertionError: ValueError not raised`). Exit 1.
2. `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evals/runs/2026-09-20-battery-noskill/blind/case-r/candidate python3 -c "from tls import respond; print(repr(respond(b'hi'+b'SECRET-PADDING', 2, 16)))"`
   - Result: printed `b'hiSECRET-PADDING'`, confirming bytes past `received=2` are disclosed instead of raising `ValueError`.

Limits:
- Reviewed only `request.md`, `base/tls.py`, `base/ARCHITECTURE.md`, `candidate/tls.py`, and `tests/test_tls.py` under `blind/case-r/`.
- No fix applied; no files modified.
- Did not assess performance, concurrency, or behavior outside the heartbeat bounds contract.
