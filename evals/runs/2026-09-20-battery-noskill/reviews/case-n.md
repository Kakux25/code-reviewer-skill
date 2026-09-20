# Case N review: rowcheck validate change

Decision: Changes requested

## Findings

- P1 — `candidate/check.py:2`: `rows.sort()` mutates the caller's list in place. A predicate named `validate` must not have this hidden side effect; observed `[3,1,2]` reordered to `[1,2,3]` after the call. Remove the sort or operate on a copy (though no copy is needed here).
- P2 — `candidate/check.py:2`: narrows the accepted input type and breaks the public API. Base `all(...)` works on any iterable; the candidate requires a mutable list with `.sort()`, raising `AttributeError` on tuples and generators (both verified). Restore iterable-generic behavior.
- P3 — `candidate/check.py:2`: the sort contradicts the stated "check rows faster" objective. `all()` is order-independent, so sorting adds O(n log n) cost (plus mutation) for zero correctness benefit. It is a pure pessimization.

## Architecture verdict

Architecture verdict: Low

## Soul verdict

Soul verdict: Betrayed

## Checks and limits

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=evals/runs/2026-09-20-battery-noskill/blind/case-n/candidate python3 -m unittest discover -s evals/runs/2026-09-20-battery-noskill/blind/case-n/tests -v` → 2/2 pass (`test_valid`, `test_invalid` OK). The suite only covers list return values, not input mutation or non-list iterables, so it cannot catch the findings above.
- Ad-hoc probe with `PYTHONPATH` on the candidate copy: `validate([3,1,2])` left the list as `[1,2,3]` (MUTATED); `validate((3,1,2))` → `AttributeError: 'tuple' object has no attribute 'sort'`; `validate(generator)` → `AttributeError: 'generator' object has no attribute 'sort'`.
- Limits: reviewed only `request.md`, `base/` (`check.py`, `PHILOSOPHY.md`), `candidate/check.py`, and `tests/test_check.py` under `blind/case-n/`; no performance benchmark beyond complexity reasoning; no other files consulted.
