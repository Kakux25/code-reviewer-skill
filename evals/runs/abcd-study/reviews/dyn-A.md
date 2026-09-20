# Arm A review: retry-policy change (dyn-a)

Scope: `client.py` (`RETRIES` 0 → 2), `retry_sim.py` unchanged. Base = `tests/dynamics-cases/dyn-a/repo/`, candidate = `tests/dynamics-cases/dyn-a/candidate/`.

## Causal model (built before simulation)

| # | Link | Polarity | Provenance | Status |
|---|------|----------|------------|--------|
| 1 | backlog(t) → offered load(t) | + | `retry_sim.py:15` (`new + backlog`) | confirmed in code |
| 2 | offered load → unserved | + | `retry_sim.py:15` (`max(0, ... - capacity)`) | confirmed, threshold at capacity |
| 3 | unserved → backlog(t+1) | + with gain (1+RETRIES) | `retry_sim.py:16` | confirmed; gain 1 → 3 under candidate |
| 4 | backlog(t+1) → backlog(t+2...) | reinforcing loop via 1–3 | composition of above | inferred structure, checked by sim |

Loop gain: each unserved unit returns as (1+RETRIES) next step. Base gain = 1 (persists but bounded when spike ends, since base_load 8 < capacity 10 drains it). Candidate gain = 3 (each overload step triples the backlog contribution — classic retry-storm reinforcing loop, no backoff/jitter/cap/circuit-breaker visible in `client.py`).

## Simulator check (read-only)

`PYTHONDONTWRITEBYTECODE=1`, `retry_sim.run()` from candidate dir (simulator identical in both revisions):

- retries=0 (base): peak backlog = 20 (bounded, drains after spike)
- retries=1: peak ≈ 8.4e12 (already diverges)
- retries=2 (candidate): peak ≈ 7.2e19 (explosive divergence)

Candidate's own test (`candidate/tests/test_sim.py`) asserts this: base < 25, candidate > 1000 — i.e. it documents the amplification rather than guarding against it.

## Findings

1. **Retry storm:** with RETRIES=2 and immediate retry (no delay/backoff), any transient overload (spike 14 vs capacity 10) is amplified 3× per step and never drains — even after the spike window ends the backlog keeps growing.
2. **No mitigation in scope:** `client.py` is a single constant; no backoff, jitter, retry budget, idempotency note, or breaker. `retry_sim.py` models immediate retry faithfully, so the sim result transfers directly.
3. **Base was stable:** gain-1 loop with headroom (base 8 < cap 10) recovers; peak 20 is consistent with a 5-step spike of +6/step draining afterward.

Decision: reject the change as-is; if retries are wanted, add bounded retries with backoff/jitter plus a retry budget or breaker, and re-run the sim with those mechanics modeled.

Verdict: Unstable
