# Memory query: mem-b

Change: raise the DB connection pool from 20 to 200.

Author motivation (a claim, not a criterion): "backend overload
during traffic spikes; cache hit rate dropped."

The change itself touches no retry logic and no cache behavior.

Candidate: `candidate/`. Case base: `tests/incident-cases/cases/`
(rank with `python3 scripts/incident_memory.py`).

Decide transfer per each case's applies_when / not_when, not by
ranking alone. Cite case ids and lessons for every decision.
Never quote restricted fields. Report one verdict:
Blocked, Clear, or No match.
