# Case G — Review (brief)

## Decision

`Changes requested` — the candidate breaks the documented error contract: a missing file returns `{}` instead of raising `FileNotFoundError`, and the acceptance test `test_missing_file_raises` fails.

## Findings

- **P1** — `candidate/loader.py:5-6`: `except OSError: return {}` swallows `FileNotFoundError` (and every other `OSError`, e.g. permission errors) and returns a dict without the `"records"` key, so callers can no longer distinguish "missing" from "empty" and will hit `KeyError` on `result["records"]`. Proof: execution — `test_missing_file_raises` FAILS on candidate (`FileNotFoundError not raised`), passes on base. Fix: remove the `try/except` and let `open()` propagate (restore base behavior).

## Verdicts

- Architecture: `Low` — primary axis A1 (error contract: missing file raises `FileNotFoundError`, per `base/ARCHITECTURE.md:3-4` and `base/loader.py:1-3`) is violated on every missing-file call with no contained tradeoff; gap: `candidate/loader.py:5-6` returns `{}` instead of raising. Secondary axis A2 (success-path shape `{"records": [...]}`) is preserved (`test_reads_records` passes). Change type: bug fix; rubric v1. No double-count: the wrong-shaped `{}` is evidence within the single A1 gap.
- Soul: `Unverifiable` — no documented essence (principles/manifesto/canon) exists in scope; `ARCHITECTURE.md` states a mechanism/contract, not identity.

## Checks and limits

- Ran `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=candidate python3 -m unittest discover -s tests -v` → 1 pass, 1 FAIL (`test_missing_file_raises`); same suite with `PYTHONPATH=base` → 2 pass.
- Ran `trace_callers.py load` over `blind/case-g` → only defs in `base/loader.py:1`, `candidate/loader.py:1` and calls in `tests/test_loader.py:13,20`; no other in-scope consumers.
- Limits: reviewed only `base/`, `candidate/`, `tests/` in `blind/case-g`; external callers beyond the suite (if any) not assessed; no static-analysis gaps beyond the reported finding.
