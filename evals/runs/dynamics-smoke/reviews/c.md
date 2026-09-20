# System dynamics review: dyn-c (bounded-retry change)

Scope: `bounded_sim.py` and `client.py`, `repo/` (base) vs `candidate/`. Disclosure: I read the candidate files as the scope requires, so this is not a blind assessment of the change; every link below is checked against the base/simulator text. I did not consult any expected verdict.

Candidate claim: `client.py` changes `POLICY` from `"unbounded"` to `"bounded-backoff-breaker"`, i.e. "bounded retries with backoff + breaker". Acknowledged as a claim; tested below against loop structure and simulator numbers.

## Causal model (built before judging)

Stocks: `backlog` (unserved units awaiting retry); breaker state (`breaker_open_until` timer). Flows: arrivals (`base` 8/step + `spike_extra` 6/step for `spike_len` 5 steps), service (`capacity` 10/step), retry re-send (`backlog` added to `sent`), backoff drain (2/step), breaker shed (`sent` = 0 for 5 steps + backlog reset). All numbers documented in `candidate/bounded_sim.py` (identical in `repo/bounded_sim.py`), lines 7–20.

Link table (line refs to `bounded_sim.py`):

- `load -> sent (+) [documented: holds]` — L14, `sent = load + backlog`
- `backlog -> sent (+) [documented: holds]` — L14; severed while breaker open (`sent = 0`)
- `sent -> unserved (+) [documented: holds]` — L15
- `capacity -> unserved (-) [documented: holds]` — L15
- `unserved -> backlog (+) [documented: holds]` — L20
- `backoff drain -> backlog (-) [documented: holds]` — L20, fixed −2/step
- `unserved -> breaker-open (+) [documented: holds]` — L16–17, trips when `unserved > 15`
- `breaker-open -> sent (-) [documented: holds]` — L14, sheds all load while open
- `breaker-open -> backlog (-) [documented: holds]` — L18, reset to 0 on trip
- `production spike -> sim load profile (+) [assumed: untested]` — ASSUMED: the step-load profile represents real traffic. Marked LOUDLY; carries no part of the verdict.

Loops (character = product of signs):

- R1 (reinforcing): `backlog -> sent (+) -> unserved (+) -> backlog (+)` — zero negatives, closes link by link.
- B1 (balancing, breaker): `sent -> unserved (+) -> breaker-open (+) -> sent (-)` — one negative; plus the `breaker-open -> backlog (-)` reset.
- B2 (balancing, backoff drain): `backlog -> backlog (-)` via the −2/step drain — one negative.

Dominant loop: **B1 (breaker)**. During the specified spike, per-step `unserved` runs 4 → 6 → 10 → 18; at 18 > 15 the breaker trips 3 steps into the 5-step spike, sheds all load for 5 steps (covering the spike remainder) and resets backlog to 0. R1 gets at most 3 steps of compounding before B1 severs it. B2 alone cannot contain R1 (drain is a fixed 2/step while R1's growth compounds as `2 + backlog` per step during the spike), so the breaker — not the backoff — is the binding stabilizer. Evidence: the bigger spike trips earlier and peaks *lower* (observed peak 8 at `spike_extra=12` vs 14 default), which only a threshold-shed loop explains.

Delay check with numbers: disturbance duration 5 steps; B1 detection delay 3 steps (accumulation to the trip threshold of 15), action in the same step (L16–18 shed + reset), shed duration 5 steps ≥ remaining disturbance 2 steps. Trip at 60% of the disturbance, shed covering 100% of the remainder — the balancing loop arrives in time, so it stabilizes rather than oscillates.

## Check against evidence

Ran read-only (`PYTHONDONTWRITEBYTECODE=1 python3`, `sys.path` pointed at `candidate/`; no `__pycache__`/`.pyc` left behind):

- `bounded_sim.run()` → peak **14** (model predicted trip-and-reset with peak under 15 — agreement).
- `run(spike_len=10)` → peak 20; `run(spike_extra=12)` → 8; `run(spike_len=10, spike_extra=12)` → 8.
- Suite (`PYTHONPATH=. python3 tests/test_sim.py`): 1 test, OK. The assertion `assertLess(run(), 15)` passes and genuinely documents boundedness (observed 14), so here green means bounded — read, not assumed.

The sim agrees with the model (trip → shed → reset → peak 14), which strengthens the verdict per the calibration rule.

## Confirmed findings

- Within the specified disturbance (5-step spike), balancing structure (B1, backed by B2) dominates the retry amplification loop R1; backlog peaks at 14 and resets.
- The candidate's "bounded" claim holds for the tested profile: the breaker threshold + 5-step shed + reset is what bounds it, not the drain rate.

## Open questions (not findings)

- Margin is one unit (14 vs asserted 15), and a 10-step spike peaks at 20 — above the suite's bound. Whoever owns the spike profile (capacity/SRE owner) should confirm the 5-step disturbance is the right design envelope and extend the suite beyond default params; the suite currently asserts only one profile.
- Post-shed re-close into a still-hot spike rebuilds backlog (the `spike_len=10` run); repeated trip-cycle behavior is observed but unasserted.
- Mapping of the sim's step-load profile to production traffic is assumed and untested (link above).

`Dynamics verdict: Stable`
