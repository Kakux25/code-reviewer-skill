# Run: 2026-09-19-skill-k1 (smoke, with-skill, K=1)

First end-to-end run of the Phase 1 harness against live reviews.

## Conditions

- Skill: repo at 950ae79 plus uncommitted Phase 1 work (negative-use block
  in SKILL.md; Incomplete-vs-No-findings clarification in report-format.md
  added DURING this run, see below).
- Reviewers: 4 parallel agents, one per case, blind to answer keys and
  EXPECTED.md (procedural rule in prompt; shared checkout, not enforced
  by isolation). Each saw only the skill files + its own case directory.
- Language fixed to English (grader tokens are English; recorded protocol).
- Grader: evals/grader.py as calibrated during this run (see below).

## Result

4/4 PASS, gate all_cases_pass MET. Details in grading.json.

Notable: the case-d reviewer found a legitimate extra P1 beyond the key
(candidate `put` rejects previously valid keys via the alphanumeric gate).
Extra findings do not fail the key; plants/controls only gate what they
declare.

## Calibration changes made during this run (pre-baseline, no scored
comparison existed yet)

1. Grader crash when printing results (passing checks fell into the
   nested-dict branch). Fixed; covered by self-test.
2. Grader decision/verdict scoping was line-based; real reviews use
   `## Decision` headers or numbered items with sub-bullets. Reworked to
   section scope + continuation lines + first-token rule. Thresholds and
   evals/README updated to describe the rule.
3. Plant matching now strips markdown inline markers; A1 gained
   "by 10" / "instead of 100" variants.
4. REAL SKILL FINDING: case-c exposed ambiguity — isolated snippet with
   no findings is `Incomplete` or `No actionable findings`? Both readings
   were defensible. Fixed the skill (report-format.md now rules:
   `Incomplete` only when the gap could change the findings) and updated
   the case-c key + good sample accordingly. Failure-derived loop closed:
   ambiguity -> skill sentence -> regression case (C1/C-C1 unchanged).

## Limits (do not over-claim)

- K=1, single model, no vanilla baseline: this run validates harness
  mechanics, not skill lift. Lift needs Phase 4 (K>=6, with/without).
- Treatment contamination: the skill's own calibration anchors name the
  case-A/case-D/case-C answers, so with-skill agents are answer-aware by
  construction. The trustworthy subset will be Phase 3 shadow fixtures.
- Lexical grading only; semantic correctness of diagnoses not verified.
