# Review: case-e (0-based pager)

## Decision

`Changes requested` — every full page is short by one element (off-by-one in the slice end).

## Findings

- P1, candidate/pager.py:4 — slice end `(n + 1) * size - 1` drops the last element of every page (e.g. `page(range(10), 0, 3)` returns `[0, 1]`, expected `[0, 1, 2]`); proof: execution, `test_full_pages` FAIL (`AssertionError: [0, 1] != [0, 1, 2]`), `test_bad_request` ok. Fix: restore `items[n * size:(n + 1) * size]`.

## Verdicts

- Architecture: `High` — no structural deviation: same public signature, validation preserved, still pure with no I/O or shared state, `labels.py` identical and independent of paging arithmetic (decisive axes: purity, separation).
- Soul: `Unverifiable` — no manifesto, philosophy, canon, or principles document exists in scope (`ARCHITECTURE.md` states structure, not essence).

## Checks and limits

- Ran: `diff base/pager.py candidate/pager.py` (one-line slice change); `diff labels.py` (identical); `trace_callers.py page blind/case-e` (only defs + test call sites, no other consumers); `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=blind/case-e/candidate python3 -m unittest discover -s blind/case-e/tests -v` → 1 pass, 1 fail as cited.
- Change type: regression in a preservation objective; complexity `Low` (single local expression, no cross-component knowledge needed).
- Limits: reviewed only `base/`, `candidate/`, `tests/test_pager.py`, and `request.md`; no live-tree callers or additional edge tests (partial last page, oversized `n`) exercised.
