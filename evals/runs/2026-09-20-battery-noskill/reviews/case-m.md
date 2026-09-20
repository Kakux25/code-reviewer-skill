# Case M review

Decision: Changes requested

## Findings

- [P1] `candidate/quiet.py:2` — `calc` writes `DEBUG calc(...)` to stdout on every call, adding an I/O side effect to a previously pure function. This contradicts `base/PHILOSOPHY.md:3-6` (never writes to stdout/stderr, no print calls, callers decide what to show) and breaks stdout consumers (piping, capture, log noise). Return values are unchanged, but observable behavior is not. Remove the `print`; if introspection is needed, return it or expose it via a separate opt-in path chosen by the caller, not unconditional stdout output.

## Correctness

Return values match base (`calc(3,2)==7`, `calc(0,5)==-5`) and the supplied suite passes, but the suite does not assert silence, so it misses the regression. Verified by capture: `calc(3,2)` returns `7` while emitting `'DEBUG calc(3, 2)\n'` to stdout.

## Architecture verdict: Low

`calc` was pure compute; the candidate couples it to process-wide stdout on every invocation with no flag or caller control, contrary to the repo's stated silent/pure constraints.

## Soul verdict: Betrayed

Both tenets in `PHILOSOPHY.md` (silent library, pure computation) are directly violated by the unconditional `print`.

## Checks and limits

- Ran suite against candidate copy: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.../blind/case-m/candidate python3 -m unittest discover -s .../blind/case-m/tests -v` — result: 1 test run, OK, with `DEBUG calc(3, 2)` and `DEBUG calc(0, 5)` leaked to output.
- Ran stdout-capture probe: `calc(3,2)` under `contextlib.redirect_stdout` — result: returned `7`, captured `'DEBUG calc(3, 2)\n'`, confirming stdout pollution.
- Limits: reviewed only `request.md`, `base/quiet.py`, `base/PHILOSOPHY.md`, `candidate/quiet.py`, `tests/test_quiet.py` inside `blind/case-m`; did not assess performance or callers outside this case.
