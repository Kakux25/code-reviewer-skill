# System dynamics review: dyn-a retry-policy change

Scope: `client.py` (`RETRIES` 0 → 2) with shared `retry_sim.py`; base `repo/`, candidate `candidate/`. I read the base first and built the model below before judging the candidate.

## Stocks and flows

- Stock: `backlog` (unserved units carried step to step).
- Inflows: `new` arrivals (base 8 + spike extra 6 inside the window) plus retry-spawned load.
- Outflow: service, capped at `capacity` = 10 per step.

## Causal model (link table)

Format: `cause -> effect (polarity) [provenance: status]`

1. `arrivals -> backlog (+) [documented: holds]` — `repo/retry_sim.py:14-15`: unserved arrivals add to backlog.
2. `backlog -> unserved next step (+) [documented: holds]` — `repo/retry_sim.py:15`: backlog re-enters the unserved computation.
3. `unserved -> retry load (+) [documented: holds]` — `repo/retry_sim.py:16`: `backlog = unserved * (1 + retries)`; each unserved unit spawns `retries` extra units.
4. `retry load -> backlog (+) [documented: holds]` — same line: retry load lands in next step's backlog.
5. `service capacity -> backlog (-) [documented: holds]` — `repo/retry_sim.py:15`: capacity clears up to 10 units/step; saturated whenever load exceeds 10.

## Loops

- **R1 (reinforcing): backlog → unserved → retry load → backlog** (links 2–4; zero negatives → R). Gain per step is ×(1 + retries): ×1 under base, ×3 under the candidate. Closed link by link from `retry_sim.py:15-16`.
- **B1 (balancing, capped): backlog → served → backlog** (link 5; one negative → B). It can clear at most 10/step, so it saturates during the spike (load 14/step) and cannot counteract R1's ×3 compounding.

**Dominant loop: R1.** The candidate triples R1's gain while adding no balancing structure (no backoff, jitter, cap, or circuit breaker). B1 is saturated during the disturbance, so R1 dominates by construction.

## Delays and timescales

- Disturbance: spike of +6/step for 5 steps (`spike_at=10, spike_len=5`), total excess 20 units over a capacity-10 server at base load 8 (`repo/retry_sim.py:8-9`).
- Retry delay: one step (immediate next-step retry, `repo/retry_sim.py:16`) — the reinforcing loop acts *within* the disturbance, compounding 5 times before the spike even ends.
- No balancing loop with a delay to compare: B1 is instantaneous but capacity-saturated, so delay analysis only confirms R1 runs unopposed.

## Evidence: simulator calibration

Ran read-only: `PYTHONDONTWRITEBYTECODE=1 python3 -c "import retry_sim; ..."` in `repo/`:

- `retry_sim.run(0)` → peak backlog **20** (bounded, matches base test `assertLess(..., 25)`).
- `retry_sim.run(2)` → peak backlog **72495708848450575446** (~7.2e19).

The model predicted amplification (×3/step compounding during a saturated spike); the simulator confirms explosive divergence, not mild growth. Per `calibration.md`, agreement strengthens the verdict.

The candidate suite (`candidate/tests/test_sim.py:9`, `assertGreater(cand, 1000)`) passes *by documenting* this explosion — a green suite on disaster, which supports Unstable, not Stable.

## Confirmed findings vs open questions

Confirmed:

- The change converts a bounded overload (peak 20) into runaway backlog growth (peak ~7.2e19) under the repository's own spike scenario.
- No new balancing mechanism accompanies the retry gain increase.

Open questions (do not affect the verdict, would size a fix):

- What retry budget, backoff, or cap would keep peak bounded? (Needs a follow-up sim run, not run here.)
- Is the 5-step spike representative of production disturbances? (Repo gives one scenario; owner: service authors.)

No dynamics claims in candidate comments to rebut; the change is a bare constant flip.

Dynamics verdict: Unstable
