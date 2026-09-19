# Run: 2026-09-20-judge-k1 (Phase 2 judge validation, K=1)

First scored run of the LLM judge against the hand-score gold.

## Design (pre-declared in evals/rubric.md + evals/thresholds.json)

- Instrument: `evals/rubric.md` v1 (binary decision/verdicts/controls,
  0/1/2 plant levels), frozen prompt `evals/judge_prompt.md`, runner
  `evals/judge.py`, scorer `evals/agreement.py`.
- Validation set: 12 live Phase 1 reviews (smoke k1 + A/B with/without)
  + 4 synthetic bad reviews = 16 reviews, 96 items. Manifest frozen in
  `manifest.json`; judge blind to hand scores and mechanical grades.
- Gate: item-level exact agreement >= 0.75 (plant levels must match
  exactly). Declared before the first judge call.

## Conditions

- Judge: `muse exec` 1.3.0, Meta provider, default model, one call per
  review (K=1). 4 parallel shards, 0 parse/schema failures, all first
  attempt except retries unused (attempts=1 everywhere).
- Gold: `evals/hand_scores.json`, single scorer (maintainer), scored
  after the rubric freeze and before any judge output was seen.

## Results

- Agreement: **95/96 = 0.990, gate 0.75 MET**. Details in agreement.json.
- By kind: decision 16/16, architecture 16/16, soul 16/16,
  controls 20/20, plants 27/28.
- Review-level full match: 15/16 (info only; gate is item-level).

## The single miss (with-b, plant B2)

Gold=1, judge=2. The with-b review accepts general iterables but never
names the removed list-only gate; the rubric's B2 level-2 bar requires
explicit treatment, hence gold 1. The judge read the implicit
acceptance ("No defects found ... objective: iterable batch input")
as sufficient for 2. Sibling review without-b, near-identical on this
point, got judge=1 (match). So the miss is judge noise on the 1-vs-2
boundary, not a systematic blindness: the plant scale's middle level
is where two honest scorers can differ.

No adjudication applied: the freeze rule forbids gold changes after
seeing judge outputs, and the gate is met with margin either way
(94/96 = 0.979 even if the gold side is taken as truth, which it is).

## Limits (do not over-claim)

- Same-family judge: reviews and judge both come from `muse` (Meta).
  Self-grading bias cannot be ruled out; a cross-family replication
  (e.g. claude, which was not logged in here) is future work.
- Single-scorer gold, no inter-rater check; K=1, no judge-temperature
  or stability data.
- Validated on cases A–D only; the 20-case battery (Phase 3) reuses
  the same rubric shape but the judge is unvalidated there.
- 0.990 measures judge-vs-human agreement on this set, not review
  quality and not general accuracy.
