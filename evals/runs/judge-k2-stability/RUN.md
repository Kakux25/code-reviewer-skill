# RUN: judge-k2-stability (independent re-run, K=2)

Date: 2026-09-20. Protocol: `PROTOCOL.md` (commit-anchored:
c52a045, committed BEFORE any judge call). Full 16-review
re-run of the K-1 validation set with the identical frozen
instrument (manifest, rubric, prompt, runner, gold). Outputs in
`outputs/`, replication scoring in `agreement-k2.json`,
K1-vs-K2 stability in `stability-k1-k2.json`. Frozen K-1 files
untouched.

## Results

- Replication (K2 vs gold): **96/96 = 1.000, gate 0.75 MET**
  (`agreement-k2.json`). By kind: decision 16/16, architecture
  16/16, soul 16/16, controls 20/20, plants 28/28.
- Stability (K1 vs K2 exact): **95/96 = 0.990**. Single diff:
  with-b plant B2 (k1=2, k2=1, gold=1).

## Interpretation

The K-1 RUN predicted its single miss (with-b B2, gold=1 vs
judge=2) was sampling noise on the 1-vs-2 boundary, not
systematic blindness. K-2 confirms it: the independent re-run
lands on the gold side (k2=1) of the same item, and every other
item — including the near-identical sibling without-b — is
unchanged. Both directions of the boundary wobble are now
observed (k1 over, k2 exact), which is what honest-scorer noise
looks like. Measured sampling noise: ±1 item (~0.01) per run.

## Impact on published claims

- The 0.990 judge-vs-hand finding REPLICATES (1.000 this run,
  same gate, same instrument). Judge threats update to "K=2,
  same-family, noise ±0.01 measured".
- Review-level full match 16/16 this run (was 15/16; info only,
  gate stays item-level).
- Open as before: cross-family replication, judge validation on
  cases E–T, prompt/model robustness (this run varies sampling
  only).

## Conditions

- Judge: `muse exec` 1.3.0 (1.3.0-R3401.1), Meta provider,
  default model, one call per review, sequential. 16/16 parsed
  first attempt, 0 retries, 0 schema failures.
- Blindness unchanged from K-1: prompts contain review + key +
  rubric only, no hand scores, no K-1 outputs.

## Threats

- Same model family, same day, identical prompts: stability
  measures sampling noise only.
- 96 items: ±1 item is ±0.01; the mismatch list above (one line)
  is the whole evidence — no histogram to hide behind.
- Same-family judge and reviews throughout; cross-family stays
  blocked on operator login.
