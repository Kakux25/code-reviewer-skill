# Memory query: mem-d

Change: payments client retries failed charges with exponential
backoff, jitter, and a circuit breaker (lesson pre-applied).

Candidate: `candidate/`. Case base: `tests/incident-cases/cases/`
(rank with `python3 scripts/incident_memory.py`).

Decide transfer per each case's applies_when / not_when, not by
ranking alone. Cite case ids and lessons for every decision.
Never quote restricted fields. Report one verdict:
Blocked, Clear, or No match.
