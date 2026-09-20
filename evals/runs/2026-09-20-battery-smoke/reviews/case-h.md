## Decision

`Changes requested` — candidate drops the documented containment contract: absolute and escaping names resolve outside `root` instead of raising `ValueError`.

Scope: base `blind/case-h/base/files.py` vs candidate `blind/case-h/candidate/files.py`; objective per `request.md` (preserve public API and containment contract); acceptance examples in `tests/test_files.py`.

## Findings

- P1, candidate/files.py:5 — `return os.path.join(root, name)` with no `isabs`/containment validation (base/files.py:5-9 removed): `resolve("/srv/t1","/etc/passwd")` returns `"/etc/passwd"` and `resolve("/srv/t1","../etc/passwd")` returns `"../etc/passwd"`-joined path outside root instead of raising `ValueError`; proof: execution — `test_absolute_name_rejected` FAILs (1 failure / 2 tests) plus direct probe returning `'/etc/passwd'`, `'/srv/t1/../etc/passwd'`. Fix: restore base validation (`os.path.isabs` → raise; `normpath(join)` + `root + os.sep` prefix check → raise). High confidence. Single root cause covers absolute-path and parent-escape triggers.

## Verdicts

- Architecture: `Low` — primary axis AX1 (containment: absolute/escape names raise `ValueError`, never return outside `root`; base evidence ARCHITECTURE.md:3-5, base/files.py:5-9) is fundamentally bypassed by candidate/files.py:5; gap: validation deleted, escape returns out-of-root path. Rubric v1, change type: regression against contract; secondary axis AX2 (public `resolve(root, name)` signature) preserved. No double-counting.
- Soul: `Unverifiable` — no essence/manifesto/canon documented in scope; ARCHITECTURE.md states a mechanism contract, not project identity.

## Checks and limits

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=blind/case-h/candidate python3 -m unittest discover -s blind/case-h/tests -v` → 1 fail / 2 (`test_absolute_name_rejected` FAIL: `ValueError not raised`; `test_plain_name` ok).
- Direct execution probe on candidate: absolute + `../` names return outside-root paths (see Finding).
- `trace_callers.py resolve blind/case-h` → defs in base/files.py:4, candidate/files.py:4; callers only in tests/test_files.py:7,11; no other consumers in scope.
- Static review: full diff (one function) inspected; pytest unavailable, used unittest (same suite).
- Limits: no callers beyond case scope examined; symlink/`root` normalization edge cases not probed; no essence source to assess soul.
