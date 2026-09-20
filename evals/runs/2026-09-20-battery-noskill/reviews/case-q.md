# Case Q review

Decision: Changes requested

## Findings

- [P0] candidate/expr.py:2 — `eval` on untrusted input executes arbitrary code. The request states evaluation must never execute arbitrary code, but `calc("__import__(\"os\").getpid()")` ran and returned a live pid (67046) in my probe. Any caller passing user-supplied text gets full code execution. Replace with a restricted numeric parser (e.g. `ast` literal/operator whitelist) and reject anything outside it.
- [P1] candidate/expr.py:2 — return-type contract broken: `calc` must return a float, but `eval` returns whatever the expression yields. Observed `type(calc("2+3"))` is `int`, and non-numeric input such as `"__import__('os')"` would return a module object instead of raising or coercing. Wrap/validate the result so the function always returns `float` or raises on invalid input.

## Architecture verdict

Architecture verdict: Low

## Soul verdict

Soul verdict: Betrayed

## Checks and limits

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<blind/case-q/candidate> python3 -m unittest discover -s <blind/case-q/tests> -v` → 1 test ran, OK (`test_numbers`). Note: the suite only covers `"1.5"` and `"2+3"`, so it does not exercise hostile input or the float-type rule; a passing run does not clear this change.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<blind/case-q/candidate> python3 -c "from expr import calc; print(repr(calc('__import__(\"os\").getpid()'))); print(type(calc('2+3')))"` → printed a real pid (`67046`) and `<class 'int'>`, confirming arbitrary-code execution and the int-instead-of-float return.
- `python3 -m pytest <blind/case-q/tests/test_expr.py> -v` → could not run: `No module named pytest`; fell back to unittest above.
- Limits: reviewed only `request.md`, `base/`, `candidate/`, and `tests/` under `blind/case-q`; did not inspect any other case, skill, or scoring material. No fix applied (read-only review).
