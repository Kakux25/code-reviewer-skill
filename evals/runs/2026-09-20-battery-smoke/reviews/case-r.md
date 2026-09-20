# Case R review (blind, brief)

## Decision

`Changes requested` — the candidate drops the bounds guard, so any overclaimed heartbeat length leaks bytes past the received payload instead of raising `ValueError`.

## Findings

- P0, candidate/tls.py:2 — `return buf[:claimed_len]` with no `claimed_len > received` check; overclaim `(buf=b"hi"+b"SECRET-PADDING", received=2, claimed_len=16)` returns `b'hiSECRET-PADDING'` instead of raising (execution: `test_overclaim_rejected` FAILs, `ValueError not raised`; leak probe confirms 14 undisclosed bytes echoed). Fix: restore the base guard `if claimed_len > received: raise ValueError("claimed beyond received")` before slicing.

## Verdicts

- Architecture: `Low` — change type: regression against a bug-fix contract; primary axis "overclaim rejected, response never exceeds received bytes" (base/tls.py:2-3, ARCHITECTURE.md:3-5) is violated at candidate/tls.py:1-2; gap: missing `ValueError` guard enables out-of-bounds echo to every caller. No secondary/minor gaps; complexity `Low` (single invariant, one call surface).
- Soul: `Unverifiable` — no philosophy/manifesto/canon essence documented in the reviewed material; ARCHITECTURE.md states a mechanism contract, not identity.

## Checks and limits

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.../blind/case-r/candidate python3 -m unittest discover -s .../blind/case-r/tests -v` → 1 pass (`test_exact_echo`), 1 fail (`test_overclaim_rejected`: `ValueError not raised`).
- Leak probe `respond(b"hi"+b"SECRET-PADDING", 2, 16)` on candidate → `b'hiSECRET-PADDING'` (confirms disclosure).
- `trace_callers.py respond .../blind/case-r` → defs in base/tls.py:1 and candidate/tls.py:1; call sites only in tests/test_tls.py:7,12; no other consumers in scope.
- `pytest` unavailable (`No module named pytest`); unittest used instead.
- Limits: reviewed only base (ARCHITECTURE.md, tls.py), candidate tls.py, and tests/test_tls.py; no production callers beyond the suite; base behavior verified statically (guard present), not executed.
