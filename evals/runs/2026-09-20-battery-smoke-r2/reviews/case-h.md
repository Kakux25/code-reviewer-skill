# Case H review (blind)

## Decision

`Changes requested` — the candidate drops the containment contract: absolute names and parent-directory escapes resolve outside the root instead of raising `ValueError`, and the acceptance suite fails.

## Findings

- P1, candidate/files.py:4-5 — cause: `resolve` is a bare `os.path.join(root, name)` with no absolute-name or escape guards (base/files.py:5-9 rejects both). Proof (execution): `test_absolute_name_rejected` FAILS (`ValueError not raised`); probe `resolve("/srv/t1", "/etc/passwd")` returns `'/etc/passwd'` and `resolve("/srv/t1", "../evil.txt")` returns `'/srv/t1/../evil.txt'` (normalizes outside the root). Fix: restore the base guards — reject `os.path.isabs(name)`, then `normpath(join(...))` and reject results outside `root + os.sep`.

## Verdicts

- Architecture: `Low` — primary axis (containment: absolute/escape inputs must raise `ValueError`, results never outside root) is violated on both anchors; the single-module pure shape and `resolve(root, name)` signature are preserved but do not mitigate the structural bypass. Change type: bug fix against base; rubric v1; gaps: (1) absolute-name guard removed, (2) escape/prefix guard removed. Complexity: `Low` — one pure function, no dependency depth; the invariant is explicit in base and request.md.
- Soul: `Unverifiable` — no essence/manifesto/principles documented in the available material (base ARCHITECTURE.md states structure only); no statements to assess.

## Checks and limits

- `PYTHONPATH=<case-h/candidate> python3 -m unittest discover -s <case-h/tests> -v` → 1 pass (`test_plain_name`), 1 FAIL (`test_absolute_name_rejected`, `ValueError not raised`).
- Probe on candidate: absolute name → `'/etc/passwd'`; `../evil.txt` → `'/srv/t1/../evil.txt'`; neither raises.
- `trace_callers.py resolve <case-h>` → defs in base/candidate files.py; callers only in tests/test_files.py:7,11; no other consumers in scope.
- Limits: static comparison base-vs-candidate plus the 2-example suite and 2 probes; no symlink/canonicalization or downstream file-operation callers examined (none in scope); no other context available.
