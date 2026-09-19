# Sample review: case-h (GOOD — synthetic, must PASS)

**Decision**: Changes requested — absolute names escape the root.

**Findings**:
- P1, candidate/files.py:5 — bare `os.path.join(root, name)` discards the root for absolute names, so `resolve("/srv/t1", "/etc/passwd")` escapes containment instead of raising ValueError. Proof: `test_absolute_name_rejected` fails. Fix: restore the absolute-name and escape checks.

**Verdicts**: architectural `High` (single helper, no gaps); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: ran test_files.py with PYTHONPATH on candidate — FAILED.
