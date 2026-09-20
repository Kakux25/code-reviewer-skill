# Case J — Review (candidate vs base)

Scope: objective is to fetch a batch of names with a single database round-trip; base `base/repo.py` uses `db.fetch_many(list(ids))`; candidate `candidate/repo.py` replaces it with a per-id list comprehension. Acceptance: `tests/test_repo.py`.

## Decision

`Changes requested` — the candidate issues one round-trip per id instead of a single batch round-trip, failing the stated objective and `test_single_round_trip`.

## Findings

- P1, candidate/repo.py:2 — N+1 round-trips: `[db.fetch_one(i) for i in ids]` calls the database once per id (3 calls for 3 ids) instead of one `fetch_many` batch call; breaks the single-round-trip contract in `base/ARCHITECTURE.md` ("One batch call means one round-trip"). Proof: execution — `test_single_round_trip` FAILs (`AssertionError: 3 != 1`); `test_batch_values` passes, so values are right but the batching contract is violated. Smallest fix: `return db.fetch_many(list(ids))`.

No other findings. Returned values are correct for the exercised inputs (static: comprehension preserves order; execution: `test_batch_values` ok).

## Verdicts

- Architecture: `Low` — primary axis "single round-trip batch fetch" (base evidence: `base/repo.py:1-2` uses `fetch_many`; `base/ARCHITECTURE.md:3-5` defines one batch call = one round-trip) is violated: candidate makes N `fetch_one` calls and never calls `fetch_many` (trace confirms: `fetch_one` call at candidate/repo.py:2, zero `fetch_many` hits). Gap G1 on that axis captures this deviation.
- Soul: `Unverifiable` — no essence/manifesto/principles document in scope; nothing to assess against.

## Checks and limits

- Ran: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<case-j>/candidate python3 -m unittest discover -s tests -v` → 1 pass (`test_batch_values`), 1 FAIL (`test_single_round_trip`, 3 != 1).
- Ran: `trace_callers.py fetch_many candidate` (no hits) and `trace_callers.py fetch_one candidate` (1 call hit at repo.py:2); lexical leads only.
- Rubric note: base and candidate were both visible before the rubric was frozen (per blind-case workflow); every criterion above was checked against base evidence (`base/repo.py`, `base/ARCHITECTURE.md`), not derived from the patch.
- Limits: no callers/consumers of `names()` in scope to trace beyond the case files; empty-id and non-list-iterable inputs not exercised by the suite; no performance measurement beyond the FakeDB call count.
