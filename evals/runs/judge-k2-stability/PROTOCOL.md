# PROTOCOL: judge-k2-stability (pre-registered)

Date: 2026-09-20. Closes the judge-k1 threat "K=1, no
judge-temperature or stability data": one independent re-run of
the full 16-review validation set with the identical frozen
instrument, then replication + stability scoring.

## Instrument (identical to K-1, all frozen)

- Manifest: `evals/runs/2026-09-20-judge-k1/manifest.json` (16 jobs)
- Rubric: `evals/rubric.md`, prompt: `evals/judge_prompt.md`
- Runner: `evals/judge.py`, scorer: `evals/agreement.py`
- Judge: `muse exec`, Meta provider, default model, one call per
  review, 4 parallel shards (mirrors K-1). Model version recorded
  in `model-id.txt` at run time.
- Gold: `evals/hand_scores.json` (judge stays blind to it).

## Pre-declared scoring

(a) Replication: K2-vs-gold agreement via `agreement.py --min
0.75` (same pre-declared gate as K-1). Pass = `gate_met`.
(b) Stability: K1-vs-K2 item-level EXACT agreement over the 96
gold items (both runs flattened with `agreement.py`'s
`judge_items`; a missing/unusable record counts every item of
that review as a mismatch). Reported as a rate with the full
mismatch list; no gate — this is a measurement, not a bar.

## Impact rule

- Replication MET + stability reported: the 0.990 finding stands
  with measured sampling noise; judge threats update to
  "K=2, same-family".
- Replication NOT MET: the K-1 finding does not replicate; the
  0.990 headline gains a documented non-replication and the judge
  returns to unvalidated status. Frozen K-1 files are NEVER
  rewritten either way.

## Threats (pre-registered)

- Same model family, same day, identical prompts: stability here
  measures sampling noise only, not prompt/model robustness.
- 16 reviews / 96 items: a single flip moves the rate by ~0.01;
  the mismatch list (not just the rate) is the evidence.
- Reviewer and judge stay same-family; cross-family replication
  remains blocked on operator login, not on method.
