# Case I review

Decision: Changes requested

## Findings

- [P0] candidate/greeter.py:1 — `greet(first, last, punct="!")` breaks the stable public signature `greet(name, punct="!")` (base/greeter.py:1, base/ARCHITECTURE.md:3). All existing single-name callers now raise `TypeError: missing 1 required positional argument: 'last'`, and the second positional argument silently changed meaning from punctuation to last name (`greet("Ada", "?")` returns `'Hello, Ada ?!'` instead of `'Hello, Ada?'`).
- [P1] candidate/app.py:5 — `welcome(user)` still calls `greet(user)` with one argument, so it is broken by the signature change and raises TypeError at runtime. The candidate updates the callee but not its in-repo caller.
- [P2] candidate/greeter.py:1 — No backward-compatible extension path: if a last name is needed, it should be an optional parameter (e.g. `greet(name, last=None, punct="!")`) preserving existing call shapes, not a new required positional.

## Architecture verdict

Architecture: Low

The change violates the documented stable API contract (one positional name plus optional punctuation) and breaks both the acceptance suite and the existing caller, rather than extending the greeter within the architecture.

## Soul verdict

Soul: Betrayed

The stated objective was to extend the greeter while preserving the public API; the candidate replaces the API with an incompatible one, defeating the request's core constraint.

## Checks and limits

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/candidate" python3 -m unittest discover -s tests -v` → FAILED (2 tests: 1 error on test_single_name with TypeError missing 'last', 1 failure on test_custom_punct: `'Hello, Ada ?!' != 'Hello, Ada?'`).
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/candidate" python3 -c "from greeter import greet; print(repr(greet('Ada')))"` → TypeError: missing required positional argument 'last'.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/candidate" python3 -c "import app; print(repr(app.welcome('Ada')))"` → TypeError raised from candidate/app.py:5.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/base" python3 -m unittest discover -s tests -v` → OK (2 tests pass), confirming the regression is introduced by the candidate.
- pytest not installed, so unittest discovery was used. Static read of base vs candidate only; no other callers searched beyond the provided app.py.
