# Sample review: case-j (GOOD — synthetic, must PASS)

**Decision**: Changes requested — batch fetch became N+1 queries.

**Findings**:
- P2, candidate/repo.py:2 — the list comprehension calls `db.fetch_one` per item (3 calls for 3 ids) instead of one `fetch_many` round-trip. Proof: `test_single_round_trip` fails with 3 calls. Fix: restore `db.fetch_many(list(ids))`.

**Verdicts**: architectural `High` (single function, no gaps); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: ran test_repo.py with PYTHONPATH on candidate — FAILED.
