# RUN: k2-agreement (second grading addendum)

Date: 2026-09-20. Protocol: `PROTOCOL.md` (pre-registered).
42 independent second grades (LLM agents blind to `grades.json`,
reading review + key only), one per smoke cell (20) and study
cell (22). Second grades in `k2-grades.json`; per-cell agree rule
from PROTOCOL (verdict match + |Δsubstance| ≤ 0.34 + false-claim
match). Frozen runs untouched; corrections live here.

## Result: 38/42 agree (0.90)

- Smoke runs: 20/20 agree. Every `4/4 match expected` headline
  stands under independent re-grading, including all semantic
  resolutions (negations, vocabulary variants), which the second
  graders re-derived blind — raw outputs preserved in `seconds/`,
  per-cell summaries in `k2-grades.json` notes. Caveat (post-hoc
  amendment A1): smoke first grades are binary + notes, so the
  agree rule compares recorded seconds against reconstructed
  firsts (first ≡ T/1.0/F wherever the frozen note documents
  full satisfaction — all 20, verified by re-read).
- Study: 18/22 agree. All 22 verdict_correct and all 22
  false_claim judgments agree; the 4 disagreements are
  substance magnitudes on probe cells (adjudicated below).
- Near-misses within tolerance (no adjudication required):
  study soc-A (first 0.67 docked a non-key escalation concept,
  second 1.0 strict on key; Δ=0.33 vs tolerance 0.34 —
  borderline, see sensitivity) and mem-B (first 2/3, second
  3/4; same missing concept INC-001).

## Adjudications (4, operator third read, must_state-only strict)

| cell | first | second | corrected |
|------|-------|--------|-----------|
| abs-stpa-A | F/0.5/T | F/0.0/T | F/0.0/T (upheld second) |
| abs-socio-A | T/1.0/F | T/0.5/F | T/0.5/F (upheld second) |
| abs-stpa-B | T/1.0/F | T/0.5/F | T/0.0/F (upheld neither; paraphrase credit rejected) |
| abs-socio-B | T/1.0/F | T/0.5/F | T/0.5/F (upheld second) |

Convention (amendment A2): adjudicated substance counts
must_state concepts only, study-rubric-faithful: stpa-d
[control-structure ✗, escalat ✗] → 0.0 both; soc-d
[no-ownership ✓, escalat ✗] → 0.5 both. The first grader
credited abstention behavior and paraphrases; the strict
standard does not. Verdict and false-claim columns never moved.

## Impact on published claims

- All smoke `4/4` headlines: UNCHANGED (20/20 agree).
- Study verdict table (A 7/8, B 8/8, C 6/6) and false-claim
  column (1/8, 0/8, 0/6): UNCHANGED.
- Study mean substance (adjudicated): A 0.90 → 0.77, B 0.96 →
  0.77, C 1.00 (both arms tie at exactly 0.7712). Sensitivity:
  cite-inclusive counting would give A/B 0.83 (tie at 0.8337;
  per-cell: abs-stpa-A/B 0.33, abs-socio-A/B 0.67).
  Either way the B-over-A substance gap was first-grader
  generosity on probes; the verdict gap and the false-claim gap
  (abs-stpa-A Safe fabrication) stand as the measured B-over-A
  effects. The mechanism story in the study RUN is otherwise
  unchanged.
- U2-U6 uncertainties (`second independent grade` next_action):
  second grades now exist for all smoke cells; the frozen
  uncertainty records stay as evidence, superseded by this
  addendum, not rewritten.

## Threats

- Same-model-family first/second operator; blindness by
  instruction only (raw second outputs in `seconds/` contain no
  grades.json content — verifiable, not just claimed).
- Adjudicator is the first grader (operator); disagreements were
  few (4) and the strict-count rule is mechanical, but a fully
  independent tie-breaker would be stronger — disclosed, not
  claimed.
- Denominator heterogeneity: |Δ| compares fractions across
  different rubrics (soc-A 2/3 vs 5/5, mem-B 2/3 vs 3/4).
  Numerically per protocol, conceptually apples-to-oranges.
- Tolerance sensitivity: below 0.33 instead of 0.34, agreement
  would be 37/42 (soc-A Δ=0.33 flips). 0.34 is a rounding of
  1/3; disclosed either way.
