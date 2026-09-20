Incident memory review: mem-a

Change: payments client retries failed charges in a tight loop with no backoff, jitter, or breaker.

Retrieval (recorded before judging):
`python3 scripts/incident_memory.py --cases tests/incident-cases/cases --tags "retry,payments" --text "payments client now retries failed charges in a tight loop with no backoff, jitter, or breaker"`
Ranking: INC-001 8. No other case ranked (positive scores only).

Transfer judgment by mechanism:

- INC-001 "Retry storm amplified a partial outage" — Applied.
  - Lesson: "Bound every retry loop: exponential backoff with jitter plus a circuit breaker."
  - applies_when matched:
    - "client retries without backoff" — matched by `candidate/client.py:3-7`: `while True:` + `except gateway.TransientError: continue` with no sleep/backoff.
    - "unbounded retry loop on a shared backend" — matched by same lines: `while True` retries `gateway.charge` indefinitely.
  - not_when checked: "retries already bounded with backoff, jitter, and a breaker" — does not hold; candidate has none of the three.
  - Required: bound the loop with exponential backoff + jitter and add a circuit breaker / retry cap. Blocked until fixed.

Open questions: none.

Memory verdict: Blocked
