# Case R review (blind)

Scope: base `tls.py` (`respond(buf, received, claimed_len)` with overclaim guard) vs candidate `tls.py`; objective per request.md: answer heartbeat requests, preserve public API and bounds contract (overclaim raises `ValueError`, response never includes bytes past payload). Rubric note: the assigned read order (request, then base/candidate/tests) exposed the diff before the rubric was frozen; every criterion below was checked against the base revision, not derived from the candidate.

## Decision

`Changes requested` — the candidate drops the bounds guard, so any overclaimed length leaks bytes past the payload (P0, proven by execution).

## Findings

- P0, `candidate/tls.py:1-2`: `respond` returns `buf[:claimed_len]` without checking `claimed_len > received`, so an overclaim (e.g. `received=2, claimed_len=16`) returns 14 bytes past the payload instead of raising `ValueError`. Proof (execution): `test_overclaim_rejected` FAILS (`AssertionError: ValueError not raised`) and a direct call returns `b'hiSECRET-PADDING'` for `received=2`. High confidence, static + execution. Smallest fix: restore the base guard before the slice: `if claimed_len > received: raise ValueError("claimed beyond received")`.

## Verdicts

- Architecture: `Low` — change type: heartbeat-responder behavior change; primary axis "overclaim rejected, echo bounded by received bytes" (base `tls.py:2-3`, request.md) is violated by the unguarded slice (`candidate/tls.py:2`); gap: overclaim returns out-of-bounds bytes, confirmed by failing test. Secondary axis (public API `respond(buf, received, claimed_len)`) preserved; no double-counting. Complexity: `Low` (single-function invariant, explicit contract).
- Soul: `Unverifiable` — no essence/manifesto/canon in the reviewed material (`ARCHITECTURE.md` states mechanism only); nothing invented.

## Checks and limits

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<blind/case-r/candidate> python3 -m unittest discover -s <blind/case-r/tests> -v` → 1 pass (`test_exact_echo`), 1 FAIL (`test_overclaim_rejected`, `ValueError not raised`).
- Direct execution `respond(b'hiSECRET-PADDING', 2, 16)` on candidate → `b'hiSECRET-PADDING'` (14 bytes past payload).
- `trace_callers.py respond <blind/case-r>` → defs in base/candidate `tls.py:1`, callers only in `tests/test_tls.py:7,12`; no other consumers in scope.
- Limits: reviewed only `request.md`, base (`ARCHITECTURE.md`, `tls.py`), candidate (`tls.py`), `tests/test_tls.py`; no callers outside the case bundle assessed; base suite not re-run (base guard read statically).
