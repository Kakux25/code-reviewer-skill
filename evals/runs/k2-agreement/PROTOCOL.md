# PROTOCOL: K-2 second grading (pre-registered)

Date: 2026-09-20. Closes the K=1 threat recorded in every smoke
RUN (`*-smoke/RUN.md` threats + U2-U7 uncertainties) and the study
RUN: one independent second grade per cell (20 smoke + 22 study
= 42), then agreement + adjudication.

## Second graders

LLM agents, one per cell, each reading ONLY the frozen review +
its key (`expected.json`, or `answer-key.json` for study/code).
Blind to `grades.json` by instruction (first grades never shown).
Each returns: verdict correctness (bool vs key), substance
fraction (must concepts present, 0..1), false-claim bool,
short notes. Same semantic rubric as the first grading.

## Agreement

Per cell `agree` = second verdict_correct matches first AND
|Δsubstance| <= 0.34 (one concept on a 3-concept rubric) AND
false_claim matches. Overall rate = agree/42. No kappa claimed
(cells are heterogeneous by design); raw agreement + full
disagreement list instead.

## Adjudication

Every disagreement gets an operator third read against review +
key, recorded as `adjudication: {upheld, corrected_reading,
corrected_substance, impact}` with upheld in
{first, second, neither} (see amendment A3). Frozen runs are
NEVER rewritten; the addendum records the corrected reading and
whether any published claim (4/4 matches, arm table, D notes)
changes. A flipped smoke cell changes that run's headline in
THIS report, with the frozen files kept as evidence of the error.

## Post-hoc amendments (disclosed, not pre-registered)

- A1 smoke reconstruction: smoke first grades are binary
  `matches_expected` + notes, not triples, so the agree rule as
  written does not apply to them. Amendment: first ≡ T/1.0/F
  wherever the frozen note documents full must/must-not
  satisfaction with matches_expected true (all 20 cells; verified
  by re-reading every note). Smoke "agreement" therefore compares
  recorded seconds against reconstructed firsts.
- A2 substance convention: adjudicated substance counts
  must_state concepts only (study-rubric-faithful), ignoring
  must_cite. Sensitivity: cite-inclusive counting would give
  A/B 0.83 instead of 0.77; both reported in RUN.md.
- A3 upheld enum: {first, second, neither} (neither = stricter
  than both, or split). The original (first|second) did not
  survive contact with abs-stpa-B.
- A4 timing: PROTOCOL/RUN/k2-grades arrived together untracked;
  "pre-registered" is mtime-anchored at best (same caveat as the
  study). Tolerance 0.34 = rounding of 1/3; sensitivity: at
  below 0.33 (e.g. 0.32), agreement would be 37/42
  (soc-A Δ=0.33 borderline; at exactly 0.33 it still agrees).
