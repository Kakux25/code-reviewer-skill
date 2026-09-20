Incident memory review — mem-d

Retrieval (recorded before judging):
- Ran `scripts/incident_memory.py` with tags/text from the change (payments retry backoff jitter circuit breaker).
- Ranking: `INC-001` (score 9). No other cases ranked.

Candidate examined: `candidate/client.py`.

Case decision:

- INC-001 "Retry storm amplified a partial outage" — Satisfied.
  - Mechanism: retry/amplification/backoff/overload; failure narrative is clients retrying failed requests and amplifying a partial backend slowdown. Lesson: bound every retry loop with exponential backoff, jitter, plus a circuit breaker.
  - The candidate is a retry loop against a shared payments backend, so the mechanism is in scope. However `not_when` holds: "retries already bounded with backoff, jitter, and a breaker". Evidence in candidate:
    - Bounded loop: line 6 `for _ in range(5):`
    - Circuit breaker: lines 7–8 `if breaker.is_open(): raise breaker.OpenError`
    - Backoff with jitter: lines 12–13 `time.sleep(delay * (0.5 + random.random()))` and `delay *= 2`
  - Per lesson-already-present, this is Satisfied, not Applied: the candidate already upholds the lesson. It is clear on this case.

Restricted fields: not quoted.

Open questions: none.

Memory verdict: Clear
