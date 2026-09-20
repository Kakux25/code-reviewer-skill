Incident-memory review — mem-b

Change: raise DB connection pool from 20 to 200 (`POOL_SIZE = 200`). Author motivation mentions "backend overload during traffic spikes; cache hit rate dropped" — treated as claim, included in retrieval query but not as transfer criterion.

Retrieval (recorded before judging):
`python3 scripts/incident_memory.py --cases tests/incident-cases/cases/ --text "raise DB connection pool from 20 to 200 backend overload during traffic spikes cache hit rate dropped" --tags "pool,overload,cache"`
Ranking:
- INC-002: 5
- INC-001: 4
- INC-003: no score (did not rank)

Transfer judgment by mechanism (applies_when AND NOT not_when):

1. INC-002 — "Thundering herd on synchronized cache expiry" — Rejected
   - Mechanism: stampede, synchronized, expiry, cache. Lesson: "Jitter TTLs and single-flight cache refills for hot keys."
   - applies_when requires "synchronized TTL expiry under load" or "hot key refill without single-flight".
   - Candidate evidence: `candidate/pool.py:2` — `POOL_SIZE = 200` — only a pool limit; no TTL, no cache refill, no read path. Fixture states: "The change itself touches no retry logic and no cache behavior."
   - Fails transfer test condition 1: no applies_when condition matches. Rank came from motivation keyword "cache" only — domain/motivation lure. Rejected; clears nothing else.

2. INC-001 — "Retry storm amplified a partial outage" — Rejected
   - Mechanism: retry, amplification, backoff, overload. Lesson: "Bound every retry loop: exponential backoff with jitter plus a circuit breaker."
   - applies_when requires "client retries without backoff" or "unbounded retry loop on a shared backend".
   - Candidate evidence: `candidate/pool.py:2` — `POOL_SIZE = 200` — no retry loop, no client retry, no backoff logic. Fixture states: "The change itself touches no retry logic and no cache behavior."
   - Fails transfer test condition 1: no applies_when condition matches. Rank came from motivation keyword "overload" only — motivation lure. Rejected; clears nothing else.

Open questions: none. Whether pool size 200 is itself safe (DB capacity, connection churn) is outside the ranked cases' mechanisms and not blocked on suspicion.

Memory verdict: Clear
