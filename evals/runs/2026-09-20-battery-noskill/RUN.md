# Run: 2026-09-20-battery-noskill (live K=1, WITHOUT skill, cases E–T)

Baseline arm for skill-lift measurement on the Phase 3 battery.

## Design (written before results)

- Conditions: 16 agents, one per case, each sees ONLY its staged blind
  directory (`blind/case-<x>`: request.md + base/candidate/tests, NO
  answer key, NO samples). NO skill files. Blind to keys/EXPECTED/
  hand_scores/rubric/other cases and to all with-skill reviews
  (procedural rule; shared checkout).
- Baseline fairness: agents get the same OUTPUT SHAPE as the skill arm
  (English; Decision line; Findings with P-priorities and file:line;
  Architecture/Soul verdict lines; Checks and limits) including the
  literal vocabularies, but NONE of the skill's method (no rubric from
  base, no verdict rules, no soul-derivation guidance, no report-format
  rules). Format failures are still failures, but the shape instruction
  keeps them from being pure vocabulary artifacts.
- With-skill comparator: combined 16/16 from smoke r1+r2
  (`../2026-09-20-battery-smoke-r2/grading-combined.json`), graded with
  the same frozen keys + grader. Same-model, same-day comparison.

## Pre-registered prediction

- Expect without-skill < with-skill (16/16), gap >= 2 cases.
- Gap concentrates where the method matters most: soul cases m/n
  (Betrayed needs essence derivation), case o (Incomplete rule),
  negatives k/l (false-positive discipline), verdict calibration
  (first-token discipline, Insufficient-evidence restraint).
- K=1: direction and location of the gap are the deliverable, not a
  precise lift percentage.

## Results

Without-skill: **2/16 PASS** (m, o) vs with-skill combined 16/16.
Lift: **+14 cases** at K=1, same model, same day, same frozen keys.

| Case | With | Without | Without fail reason |
| --- | --- | --- | --- |
| e | PASS | FAIL | soul Preserved invented; P0-only (E1 wants P1) |
| f | PASS | FAIL | soul Betrayed invented; "tests pass" (base suite, true) |
| g | PASS | FAIL | soul Betrayed invented |
| h | PASS | FAIL | soul Betrayed invented; P0-only (H1 wants P1) |
| i | PASS | FAIL | soul Betrayed invented; "tests pass" (base suite, true) |
| j | PASS | FAIL | soul Betrayed invented |
| k | PASS | FAIL | soul Preserved invented |
| l | PASS | FAIL | soul Preserved invented |
| m | PASS | PASS | — (quoted "silent library" unprompted) |
| n | PASS | FAIL | Betrayed stated but essence never quoted (N2) |
| o | PASS | PASS | — (request hands over Incomplete + restrained verdicts) |
| p | PASS | FAIL | soul Betrayed invented |
| q | PASS | FAIL | soul Betrayed invented |
| r | PASS | FAIL | soul Betrayed invented |
| s | PASS | FAIL | soul Betrayed invented; P0-only (S1 wants P1) |
| t | PASS | FAIL | soul Betrayed invented; arch Acceptable; P0-only (T1) |

Attribution (8 failing reviews read in full, rest via grading + greps):

1. Soul discipline = the dominant lift (13/14 fails). Without the
   skill's "Unverifiable when no essence is documented; never invent"
   rule, reviewers say Preserved on clean cases (e/k/l) and Betrayed
   on defect cases (f/g/h/i/j/p/q/r/s/t) — conflating "bug found"
   with "essence betrayed". The skill arm is 16/16 on soul.
2. Severity calibration (e/h/s/t): P0-only findings where the key
   wants P1. Keys frozen against skill-arm evidence; NOT widened to
   fit the baseline (that would erase the measurement). The
   priority-calibration half of the skill is real lift.
3. Verdict calibration (t Acceptable; n missing essence quote): the
   D3-rule (betrayal must quote the essence statement) fires only in
   the skill arm.
4. F-C1/I-C1 "tests pass": both flagged statements are TRUE (the BASE
   suite passes — reviewers ran base-vs-candidate comparisons). Known
   document-wide lexical artifact; both cases fail independently on
   soul, so the 2/16 case-level result is unaffected either way.

Prediction check (honest): direction right, magnitude underestimated
(>= 2 predicted, 14 observed). Locations partly wrong: m and o passed
the baseline (m's essence is explicit enough to quote unprompted; o's
request hands over the restraint), and k/l failed only on soul
invention, not the predicted false-positive discipline (no false
positives occurred — the hashable rescope held).

Headline insight: baseline defect DETECTION is strong (13/13 defect
decisions correct, every plant diagnosed lexically except severity/
quote). The skill's lift is not finding bugs — it is verdict, severity,
essence, and factual discipline on top of found bugs.

## Limits

- K=1 per arm: +14 is a direction + location signal, not a precise
  lift percentage; no CIs, no cross-model replication.
- With-skill side is an r1+r2 mix (each fixture's final review);
  without-skill side is a single fresh pass. Same-model comparison
  (muse/Meta); cross-family replication still open.
- Mechanical grading: soul/arch letters dominate the gap by
  construction of the keys; semantic review quality beyond the keys
  is the judge's question (validated on A–D only).
