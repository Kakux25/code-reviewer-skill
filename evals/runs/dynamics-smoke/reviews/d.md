# System Dynamics Review: dyn-d (cache TTL 60 → 600)

## Causal model (built first, from repo material)

Stocks: cached entries (implied by TTL constant; no stock/flows code in repo).
Flows: expirations, origin/DB lookups, cache fills (no code or config for any of these in repo).

Link table (required format):

1. `TTL_SECONDS -> expiration rate (-) [assumed: untested]` — higher TTL should mean fewer expirations per unit time, but no expiry logic, load, or hit-rate code exists in `repo/cache.py` (only `TTL_SECONDS = 60`, line 2) to ground this.
2. `expiration rate -> origin/DB request rate (+) [assumed: untested]` — more expirations should mean more misses reaching origin; no arrival-rate, miss-path, or capacity data in repo.
3. `origin/DB request rate -> origin load (+) [assumed: untested]` — no latency, capacity, or queue numbers anywhere in repo.
4. `TTL_SECONDS -> data staleness (+) [assumed: untested]` — longer TTL should mean staler served data; no freshness requirement or invalidation logic in repo.
5. `origin load ->(?) request latency [assumed: untested]` — no latency measurements in repo, so even the sign under saturation cannot be grounded.

Documented constants (not links): `TTL_SECONDS = 60` in `tests/dynamics-cases/dyn-d/repo/cache.py:2`; `TTL_SECONDS = 600` in `tests/dynamics-cases/dyn-d/candidate/cache.py:2`. The candidate changes the constant 10x but adds no measurements, no expiry/jitter/singleflight logic, and no simulator.

Loops: none closable. A candidate balancing story (longer TTL → fewer origin hits → lower load) and a candidate reinforcing risk (longer TTL → synchronized expiry cohort → stampede on mass expiry → overload → more retries/timeouts → more load) are both unclosable link-by-link from repo evidence — every link above is `assumed/untested`. Per the skill, links without provenance are stories; a review with zero `observed` or `documented` links is Uncalibrated, not Stable.

Delays: cannot compare. No TTL-driven refresh delay, no disturbance timescale (spike duration, traffic rate), no origin recovery time exists in the repo, so no delay-vs-disturbance ratio can be computed.

Evidence check: no simulator, no test suite, no logs, no load/latency/hit-rate numbers to run or quote. The change "looks small" (one constant) — calibration rules forbid upgrading that to Stable. Small changes move TTLs; TTLs move stampedes.

Candidate claim ("TTL raised 10x" implying savings/safety): acknowledged as a claim, not analysis. It is untestable against loop structure and numbers because the repository supplies neither.

## Confirmed findings

- The candidate raises TTL 10x (60 → 600) with no accompanying measurements or protective logic.
- No stock-and-flow structure beyond the bare constant is identifiable from repo files.

## Open questions (separate from findings; needed to calibrate)

1. Request arrival rate and peak/average ratio at the cache (measure at edge; owner: service team).
2. Origin/DB capacity and latency-vs-load curve (load test; owner: backend team).
3. Current and projected hit-rate vs TTL curve (measure from cache logs; owner: service team).
4. Staleness tolerance of consumers and invalidation requirements (product/backend contract).
5. Expiry behavior: synchronized vs jittered TTL, stampede protection (singleflight, request coalescing) — provide code or config.

`Dynamics verdict: Uncalibrated`
