# System-dynamics review: dyn-a retry-policy change

Exposure disclosure: I read the candidate (`RETRIES = 2`) before finalizing the model, so this is not a blind assessment. Every link below is checked against the base files.

## Stocks and flows

- Stock: `backlog` (unserved units, `retry_sim.py:16`).
- Inflows: `new` arrivals (base 8/step, +6 inside the 5-step spike window) plus retried backlog carried forward (`retry_sim.py:13-16`, documented constants).
- Outflow: service clears up to `capacity=10`/step (`retry_sim.py:15`).
- Change: `client.py` `RETRIES` 0 → 2; simulator multiplies each unserved unit into `(1 + retries)` next-step backlog (`retry_sim.py:16`).

## Causal link table

- `spike arrivals -> unserved units (+) [documented: holds]` — `retry_sim.py:13-15`: during the window `new=14 > capacity=10`, so unserved > 0.
- `unserved units -> next-step backlog (+) [documented: holds]` — `retry_sim.py:16`, gain `(1+retries)`.
- `backlog -> unserved units (+) [documented: holds]` — `retry_sim.py:15`: backlog adds to `new` against fixed capacity.
- `candidate RETRIES=2 -> retry gain (+) [documented: holds]` — `candidate/client.py:2` vs `repo/client.py:2`; gain rises 1 → 3.
- `capacity -> unserved units (-) [documented: holds]` — `retry_sim.py:15`, fixed at 10; no scaling loop exists in the repo.

## Loops

- R1 (reinforcing): backlog → unserved → backlog, gain 3 per step under the candidate. Closed link by link above; dominant loop.
- B1 (balancing): backlog → unserved → (service clears up to capacity) — but capacity is fixed at 10 with no scaling, backoff, or shedding loop anywhere in the repo, so B1 saturates the moment load exceeds 10 and cannot counteract R1. No delay comparison applies: there is no delayed balancing loop to arrive late; the balancing structure is simply capped.

Why R1 dominates: the disturbance (5-step spike, +6/step over capacity) seeds unserved backlog, and with gain 3 per step the backlog grows geometrically even after the spike ends, since base load 8 + any backlog above 2 already exceeds capacity 10. The model predicts explosion, not recovery.

## Evidence (observed)

Ran read-only (`PYTHONDONTWRITEBYTECODE=1`, `git status` clean after):

- `retry_sim.run(0)` → peak backlog **20** (bounded).
- `retry_sim.run(2)` → peak backlog **72495708848450575446** (~7.2e19, explosion).
- `candidate/tests/test_sim.py` asserts exactly this (`base < 25`, `cand > 1000`) and passes — per `calibration.md`, a green suite documenting explosion supports Unstable, not Stable.

The simulator agrees with the loop model: gain-3 reinforcing loop with saturated balancing → unbounded growth.

## Confirmed findings vs open questions

Confirmed: the candidate converts a bounded overload (peak 20) into runaway retry amplification (peak ~7e19) under the repo's own spike parameters; no balancing mechanism in the change counters it.

Open questions (do not affect the verdict): real arrival distribution and spike durations in production; whether any out-of-scope layer (load shedding, circuit breaker, autoscaling) exists outside `retry_sim.py`/`client.py` — none is evidenced in the reviewed scope.

Dynamics verdict: Unstable
