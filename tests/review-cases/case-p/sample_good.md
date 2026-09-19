# Sample review: case-p (GOOD — synthetic, must PASS)

**Decision**: Changes requested — the production key is hardcoded.

**Findings**:
- P1, candidate/client.py:1 — `API_KEY = "prod-key-..."` hardcodes the secret in source code instead of reading it from the environment; every checkout leaks it. Proof: static. Fix: read `os.environ["API_KEY"]` at runtime and rotate the exposed key.

**Verdicts**: architectural `High` (single module, no gaps); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: ran test_client.py with PYTHONPATH on candidate — suite passes (shape unchanged), which does not excuse the leak.
