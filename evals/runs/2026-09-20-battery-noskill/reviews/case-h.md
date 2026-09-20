# Case H Review

Decision: Changes requested

## Summary

Base `resolve(root, name)` enforces the containment contract: it rejects
absolute names and normalizes the joined path, raising `ValueError` when the
result escapes `root`. The candidate reduces the function to a bare
`os.path.join(root, name)`, deleting both guards. Absolute names and
parent-directory escapes now resolve instead of raising, which directly
contradicts the stated contract and fails the acceptance suite.

## Findings

1. [P0] Absolute tenant names are no longer rejected. `resolve("/srv/t1",
   "/etc/passwd")` returns `"/etc/passwd"` (`os.path.join` discards the root)
   instead of raising `ValueError`. The acceptance test
   `test_absolute_name_rejected` fails. (candidate/files.py:5)
2. [P0] Parent-directory escapes are no longer rejected. Names such as
   `"../evil.txt"` and `"sub/../../evil.txt"` resolve to paths outside the
   root instead of raising `ValueError`; the `normpath` plus prefix check in
   base is gone, so tenant paths can escape the root directory.
   (candidate/files.py:5)

## Architecture verdict

Architecture verdict: High

## Soul verdict

Soul verdict: Betrayed

## Checks and limits

Commands run (all with `PYTHONDONTWRITEBYTECODE=1`):

1. Candidate suite:
   `PYTHONPATH=<...>/blind/case-h/candidate python3 -m unittest discover -s <...>/blind/case-h/tests -v`
   Result: 2 tests, 1 failure — `test_absolute_name_rejected` fails with
   `AssertionError: ValueError not raised`; `test_plain_name` passes.
2. Base suite (same command with `PYTHONPATH=<...>/blind/case-h/base`):
   Result: 2 tests, both pass.
3. Candidate probe:
   `resolve('/srv/t1','../evil.txt')` -> `'/srv/t1/../evil.txt'`;
   `resolve('/srv/t1','/etc/passwd')` -> `'/etc/passwd'`;
   `resolve('/srv/t1','sub/../../evil.txt')` -> `'/srv/t1/sub/../../evil.txt'`
   (no exception in any case).
4. Base probe (same inputs): all three raise `ValueError`
   (`escape from root` / `absolute name` / `escape from root`).

Limits: reviewed only `request.md`, `base/` (`ARCHITECTURE.md`, `files.py`),
`candidate/files.py`, and `tests/test_files.py` inside `blind/case-h`. No
symlink/realpath edge cases were exercised beyond the containment probes above;
the candidate has no normalization at all, so any `..`-based escape succeeds
regardless.
