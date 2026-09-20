Study arm B (code-reviewer skill ONLY) — blind review of `tests/incident-cases/mem-a/candidate/client.py`. Did not open `expected.json`.

Scope: 7-line isolated snippet; change objective per query: payments client now retries failed charges in a tight loop with no backoff, jitter, or breaker. No base revision of the payments client, no gateway contract, no in-repo callers (trace shows only the def at `client.py:2` and self-call at `client.py:5`).

Exposure disclosure: candidate was seen before rubric freeze, so no blind assessment is claimed. Rubric was still checked against available base context (none for this client).

## Review (brief format)

**Decision**: `Changes requested` — unbounded tight retry loop hangs the caller and hammers the shared backend (P1, execution-confirmed).

**Findings**:
- P1, `client.py:3-7` — `while True` retries `gateway.charge` on `TransientError` with no attempt bound, sleep, backoff, jitter, or breaker. Trigger: persistent transient failure (backend slowdown). Consequence: caller never returns; loop spins at ~6.4M attempts/s (measured), amplifying a partial outage into overload. Proof: execution repro — 5,000 forced failures cleared in 0.001 s with zero delay; always-failing gateway still looping after 13,155,582 attempts in 2 s (SIGALRM interrupt). No guard in snippet; unknown caller timeout would not fix backend hammering. Change introduces it per query statement. Fix: bound attempts, exponential backoff with jitter, re-raise last error after exhaustion; add breaker per client convention.

**Open questions** (not findings): `gateway` is undefined/unimported in the snippet — excerpt or real `NameError` risk? Caller timeout/cancellation behavior unknown.

**Architecture**: change type: behavior change (retry policy). No base revision → no defensible primary axis from repository evidence → verdict `Insufficient evidence`, no gaps claimed (a lack of evidence is not `High`). Complexity: `Low` — single function, invariant visible locally.

**Soul**: no essence/manifesto/canon for the payments client in repo (skill README describes the reviewer, not the client) → `Unverifiable`, continue without it.

**Checks and limits**: `trace_callers.py charge` (1 def, 1 call site); AST parse; `/tmp/repro_retry.py` execution as above. Not run: repo test suite (no tests cover this snippet). Limits: partial coverage — no base, no gateway contract, no callers; architectural verdict unanswerable but does not change the P1 functional finding.

## Skill verdict lines
- Decision: `Changes requested` (P1 unbounded retry)
- Architectural verdict: `Insufficient evidence` (isolated snippet, no base revision for a primary axis)
- Soul verdict: `Unverifiable` (no documented essence)
