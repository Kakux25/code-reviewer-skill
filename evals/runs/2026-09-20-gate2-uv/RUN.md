# Run: 2026-09-20-gate2-uv (live K=1, with-skill, cases U–V)

Live validation of the two gate-2 control fixtures.

## Design

- Same conditions as the battery smokes: skill HEAD, one blind agent
  per case, skill files + staged `blind/case-<x>` only (request.md +
  base/candidate/tests, no keys, no samples), English, brief format.
- Expectation (same bar as smoke r1): live reviews should pass their
  frozen keys first try; any fail would trigger the same triage policy
  (fixture bug / review miss / grader artifact). Recorded here rather
  than pre-registered: both fixtures passed mechanically (integrity
  self-test incl. good/bad samples) before any live review ran.

## Results

2/2 PASS (`grading.json`). No triage needed:

- case-u (guard-present): NAF, High/Unverifiable, guard affirmed.
- case-v (pre-existing): NAF with helper.py attributed to base.

Envelopes for both live reviews built via `scripts/review_envelope.py`
(`envelopes/case-{u,v}.json`, self-validated on write): claims
supported, decision INSUFFICIENT_EVIDENCE (single reviewer).

## Limits

- K=1, same model/day as prior runs; negatives only (both NAF by
  design); no without-skill arm for u/v.
