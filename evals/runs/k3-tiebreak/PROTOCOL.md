# PROTOCOL: K-3 tie-break (pre-registered)

Date: 2026-09-20. Closes the K-2 threat "adjudicator is the first
grader (operator)": the 4 K-2 disagreements (all study abstention
probes, all substance magnitudes) were adjudicated by the same
operator who produced the first grades. K-3 adds one independent
third grade per disputed cell, then compares third vs first vs
second vs adjudicated. No new adjudication: the third is
tie-break evidence, recorded only.

## Cells (4)

| cell | review (frozen) | key (frozen) |
|------|-----------------|--------------|
| abcd-study/abs-stpa-A | evals/runs/abcd-study/reviews/abs-stpa-A.md | tests/stpa-cases/stpa-d/expected.json |
| abcd-study/abs-socio-A | evals/runs/abcd-study/reviews/abs-socio-A.md | tests/socio-cases/soc-d/expected.json |
| abcd-study/abs-stpa-B | evals/runs/abcd-study/reviews/abs-stpa-B.md | tests/stpa-cases/stpa-d/expected.json |
| abcd-study/abs-socio-B | evals/runs/abcd-study/reviews/abs-socio-B.md | tests/socio-cases/soc-d/expected.json |

## Third graders

`muse exec` headless, one call per cell, self-contained prompt
(review + key + rules pasted inline, frozen in `prompts/`).
The prompt instructs the grader to use ONLY the pasted material
and to read no repository files. Blindness to first / second /
adjudicated grades by construction (they appear nowhere in the
prompt); raw outputs preserved in `thirds/` with a tripwire test
(no `grades.json` / `k2-grades` / `adjudicat` content).

Each third returns: `verdict_correct` (bool vs key verdict),
`substance` (strict must_state fraction, 0..1), `false_claim`
(bool vs key must_not_claim), per-concept notes.

## Strict substance rule (pre-registered, K-2/A2 adopted ex ante)

Substance counts must_state concepts ONLY (must_cite ignored). A
concept counts iff the review states it explicitly or with an
unambiguous synonym IN THE ABSTENTION FRAME:

- stpa-d "no control structure": requires STPA control-structure
  language (losses/hazards/control structure absent). Notes about
  code structure (files, functions, call flow) do NOT count.
- stpa-d / soc-d "escalat": requires escalation language (escalate,
  needs safety/domain-owner review, cannot proceed without X).
  Merely flagging a need or describing a gap does NOT count.
- soc-d "no ownership": requires stating that no owner / ownership
  record exists (or equivalent). Naming a team or owner counts
  AGAINST (see false_claim).

Both keys have 2 must_state concepts, so substance ∈ {0.0, 0.5,
1.0} and all comparisons are EXACT (no tolerance).

## Comparison (no adjudication)

Per cell, report the third triple alongside first / second /
adjudicated triples and name exact matches (all three fields
equal). If the third matches none, or matches a non-adjudicated
reading, that is recorded as an OPEN disagreement with arm-mean
sensitivity recomputed under the third reading (both numbers
reported). Frozen runs and the K-2 addendum are NEVER rewritten.

## Impact rule

- If all 4 thirds match the adjudicated triples: the K-2
  adjudications stand confirmed; arm means 0.77/0.77/1.00 unchanged.
- Otherwise: the affected arm mean(s) gain a documented
  alternative; the published claim becomes the range, not a point.

## Threats (pre-registered)

- Same-model-family third graders (claude CLI not logged in here;
  no provider API keys in env — cross-family replication stays
  future work, blocked on operator login, not on method).
- Headless `muse exec` could in principle read repo files despite
  instructions; the tripwire test verifies it did not (raw outputs
  contain no grades content — verifiable, not just claimed).
- The strict rule's synonym line (escalation vs need-flagging) is
  the known judgment call; per-concept notes make each call auditable.
