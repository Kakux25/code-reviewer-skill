# Sample review: case-g (GOOD — synthetic, must PASS)

**Decision**: Changes requested — missing files are silently hidden.

**Findings**:
- P1, candidate/loader.py:5-6 — `except OSError: return {}` swallows the error and hides missing files behind an empty dict, breaking the FileNotFoundError contract. Proof: `test_missing_file_raises` fails. Fix: let the error propagate (or re-raise after logging).

**Verdicts**: architectural `High` (single module, no gaps); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: ran test_loader.py with PYTHONPATH on candidate — FAILED.
