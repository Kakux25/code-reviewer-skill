# System dynamics review: dyn-b autoscaler retuning

## Stocks and flows

Stocks (what accumulates):

- `capacity` (starts 10, `scale_sim.py:9`).
- `pending` scale-up orders (scheduled, not yet arrived).
- `unserved_total` (accumulated unmet demand).

Flows (what moves them):

- Arrivals: `base=8`, `spike_load=30` for `spike_len=3` steps (`scale_sim.py:7-8`).
- Service: `min(load, capacity)` per step; overflow becomes `unserved = max(0, load - capacity)` (`scale_sim.py:19`).
- Scaling: on `unserved > 0`, order `scale_amount=30` arriving `scale_delay` steps later (`scale_sim.py:21-22`).

## Causal model (built before judging)

Link table, format `cause -> effect (polarity) [provenance: status]`:

1. `load -> unserved (+) [documented: holds]` — `candidate/scale_sim.py:14,19`: higher load at fixed capacity raises unserved.
2. `unserved -> scale order (+) [documented: holds]` — `candidate/scale_sim.py:21-22`: unserved triggers one pending order.
3. `scale order -> capacity (+) [documented: broken]` — mechanism exists (`candidate/scale_sim.py:15-18`), but candidate `scaler.py:6` sets `SCALE_DELAY=300` vs base `repo/scaler.py:2` `SCALE_DELAY=1`. Arrival at `t+300` never lands within `steps=40` horizon, so the link is severed in-window by the change.
4. `capacity -> unserved (-) [documented: holds]` — `candidate/scale_sim.py:19`: more capacity reduces unserved.
5. `scale_delay -> unserved_total (+) [observed: holds]` — ran `PYTHONDONTWRITEBYTECODE=1 python3 -c "import scale_sim; ..."` in `candidate/`: `run(1)=20`, `run(300)=60`. Longer delay increases total unserved.

Loops:

- B1 (balancing): `unserved -> scale order (+) -> capacity (+) -> unserved (-)`. Product: one negative = balancing (B). Closed link-by-link via links 2, 3, 4 above.
- Under the candidate, B1 is broken in-window: delay 300 steps vs disturbance 3 steps, ratio 100:1. No reinforcing loop is asserted; the dynamics are open-loop accumulation during the spike.

Dominant loop: none effective under the candidate. B1 dominates in the base (delay 1 < spike 3, capacity arrives mid-spike and cuts unserved to 20). In the candidate B1 arrives 297 steps after the spike ends, so open-loop overload `3 * (30-10) = 60` dominates. Evidence is the observed 20 vs 60 split above.

## Check against evidence

Calibration per `calibration.md`: disturbance timescale `spike_len=3` vs loop delay `SCALE_DELAY=300`. Delay longer than disturbance = loop cannot save you. Ratio 100x, not vibes.

Simulator agrees with the model and the fix direction is confirmed: it predicts 60 unserved open-loop, and the sim returns exactly 60.

Suite color check: `candidate/tests/test_sim.py:5-9` passes (`Ran 1 test ... OK`), but its assertions document disaster: `base < 30` and `cand > 50`. Per calibration rules, a green suite documenting explosion supports Unstable, not Stable.

Candidate claims (`candidate/scaler.py:1-4`: "confirm sustained demand", "handles spikes", "saves cost"): acknowledged as claims. Loop structure plus numbers reject the "handles spikes" claim — the 300-step confirmation filter guarantees the 3-step spike is never handled. The "saves cost" claim is uncalibrated here: no cost model exists in the repo.

## Confirmed findings

- Retuning 1 -> 300 inverts the delay/disturbance relationship from 1/3 (stabilizing) to 300/3 (destabilizing).
- Total unserved triples: 20 -> 60 observed.

## Open questions (separate, not verdict-carrying)

- Is there an off-sim fast path (burst capacity, queueing, load-shed) not modeled in `scale_sim.py`? No repo evidence; owner: service team.
- What is the real spike-duration distribution? If all spikes exceed 300 steps the loop could re-close, but no load data provided; owner: SRE/metrics.

Dynamics verdict: Unstable
