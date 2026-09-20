## Arm C study (mem-a, incident-memory)

**Skill read:** `skills/incident-memory/SKILL.md` + `references/applicability.md` + `references/redaction.md`. `expected.json` never opened (blind).

**Retrieval (recorded before judging):**
Query from the change itself: tags `retry,backoff,payments,charge`, text "payments client now retries failed charges in a tight loop with no backoff, jitter, or breaker".
Ranking: `INC-001 9` only. Non-empty, so proceeding to transfer judgment.

**Candidate** (`tests/incident-cases/mem-a/candidate/client.py`):
`while True:` (line 3) → `gateway.charge` (line 5) → `except gateway.TransientError: continue` (lines 6–7). No backoff, no jitter, no breaker, no attempt bound.

**Transfer decisions (mechanism, not rank):**

- **INC-001 "Retry storm amplified a partial outage" — Applied.** `applies_when` "client retries without backoff" matches lines 3–7 (`while True` + bare `continue` on transient error); "unbounded retry loop on a shared backend" matches (infinite loop against `gateway`). `not_when` "retries already bounded with backoff, jitter, and a breaker" does not match — none are present. Lesson: bound every retry loop with exponential backoff with jitter plus a circuit breaker. Candidate is blocked until it does.
- **INC-002 (cache stampede), INC-003 (disk exhaustion) — not ranked (score 0), no transfer.** Mechanism mismatch confirmed: candidate has no cache TTL/expiry path and no local-write/logging path, so neither `applies_when` list matches.

No restricted fields quoted or hinted (cases read via `render_public`). No open questions — the mechanism evidence is conclusive.

`Memory verdict: Blocked`
