Review — mem-a: payments client retry loop

Candidate: `tests/incident-cases/mem-a/candidate/client.py`
- `charge()` wraps `gateway.charge` in `while True`, catching `TransientError` and retrying immediately with no sleep, no attempt cap, no jitter, no breaker.

Findings:
1. Unbounded retry loop (INC-001 applies): matches "client retries without backoff" and "unbounded retry loop on a shared backend". Lesson: bound every retry loop with exponential backoff + jitter + circuit breaker. A partial gateway slowdown would be amplified into a full outage, plus risk of duplicate charges. Not excluded by its not_when (no backoff/jitter/breaker present). → transfer INC-001.
2. INC-002 (cache stampede) does not transfer: no cache, TTL, or hot-key refill in this code; applies_when not met.
3. INC-003 (disk-full from logs) does not transfer: no local writes or logging verbosity change; applies_when not met.

Decision: 1 transfer (INC-001), blocking severity — unbounded immediate retry on a shared payments backend.

Verdict: Blocked
