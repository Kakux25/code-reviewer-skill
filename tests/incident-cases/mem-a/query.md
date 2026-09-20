# Memory query: mem-a

Change: payments client now retries failed charges in a tight loop
with no backoff, jitter, or breaker.

Candidate: `candidate/`. Case base: `tests/incident-cases/cases/`
(rank with `python3 scripts/incident_memory.py`).

Decide transfer per each case's applies_when / not_when, not by
ranking alone. Cite case ids and lessons for every decision.
Never quote restricted fields. Report one verdict:
Blocked, Clear, or No match.
