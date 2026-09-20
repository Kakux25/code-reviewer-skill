# Case G review (blind)

## Decision

`Changes requested` — the candidate breaks the required missing-file error contract (`FileNotFoundError` swallowed; acceptance test fails).

## Findings

- P1, candidate/loader.py:5-6: `except OSError: return {}` swallows `FileNotFoundError` on any missing file (trigger: every nonexistent path; also masks permission/IO errors) and returns `{}` without the documented `"records"` key, so callers cannot distinguish "missing" from "empty" and downstream `result["records"]` raises `KeyError`. Proof: execution — `test_missing_file_raises` FAILS on candidate (`FileNotFoundError not raised`), passes on base. Fix: remove the try/except and let `open()` propagate (base loader.py:1-3).

## Verdicts

- Architecture: `Low` — primary axis A1 (missing file raises `FileNotFoundError`; success returns `{"records": [...]}`) violated by the `except OSError → {}` handler; gap is the swallowed error plus the shapeless `{}` return. Secondary axis A2 (single-module `load(path)` API) preserved. Change type: error-handling change; base: blind/case-g/base; rubric v1.
- Soul: `Unverifiable` — no documented essence in scope (`ARCHITECTURE.md` states mechanism only); no statements to assess.

## Checks and limits

- `PYTHONPATH=blind/case-g/candidate python3 -m unittest discover -s blind/case-g/tests`: 1 fail (`test_missing_file_raises`), 1 pass (`test_reads_records`).
- `PYTHONPATH=blind/case-g/base python3 -m unittest discover -s blind/case-g/tests`: 2 pass (confirms regression is introduced by candidate).
- `trace_callers.py load blind/case-g`: defs in base/candidate loader.py; call sites only in tests/test_loader.py:13,20 — no other in-scope callers.
- Limits: no callers beyond the case suite visible; pytest unavailable (used unittest); static + execution evidence only.
