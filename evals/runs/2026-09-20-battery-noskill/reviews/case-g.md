# Case G Review

Decision: Changes requested

## Findings

- [P0] candidate/loader.py:5 — Missing-file error contract broken: `except OSError: return {}` swallows `FileNotFoundError`, so callers cannot distinguish "missing" from "empty". The request requires a missing file to raise `FileNotFoundError`. Fails `test_missing_file_raises`.
- [P1] candidate/loader.py:6 — Return-shape contract broken: error path returns `{}` instead of `{"records": [...]}`, violating the documented `load(path)` return shape in `ARCHITECTURE.md`. Callers accessing `result["records"]` get `KeyError` on the error path.
- [P2] candidate/loader.py:5 — Overbroad exception handler: catching `OSError` masks `PermissionError`, `IsADirectoryError`, and other I/O failures, making real failures silent and hard to diagnose.

## Architecture verdict

Architecture verdict: Low

## Soul verdict

Soul verdict: Betrayed

## Checks and limits

- Ran candidate suite: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.../blind/case-g/candidate python3 -m unittest discover -s .../blind/case-g/tests -v` → 1 pass, 1 fail (`test_missing_file_raises`: `AssertionError: FileNotFoundError not raised`; `test_reads_records`: ok).
- Ran base suite for comparison: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.../blind/case-g/base python3 -m unittest discover -s .../blind/case-g/tests -v` → 2 pass (`test_missing_file_raises`: ok; `test_reads_records`: ok), confirming the candidate is a regression.
- Attempted `python3 -m pytest .../blind/case-g/tests/test_loader.py -v` on the candidate → failed to run (`No module named pytest`); fell back to unittest.
- Limits: reviewed only `request.md`, `base/ARCHITECTURE.md`, `base/loader.py`, `candidate/loader.py`, and `tests/test_loader.py` inside `blind/case-g`; no other files consulted. Did not test permission errors or directory paths beyond the provided suite.
