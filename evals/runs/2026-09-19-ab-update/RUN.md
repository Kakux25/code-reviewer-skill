# Run: 2026-09-19-ab-update (A/B: skill HEAD vs skill + update, K=1)

## Design (written before results)

- Conditions: `without` = skill at HEAD (950ae79) for SKILL.md +
  report-format.md; `with` = worktree (negatives block + Incomplete
  clarification). All other skill files identical (worktree) in both.
  Snapshots frozen in skill-without/ and skill-with/.
- Reviewers: 8 agents (4 cases x 2 conditions), each sees ONLY its
  condition snapshot + its own case directory. Blind to keys/EXPECTED,
  English fixed, brief format.
- Grading: current frozen keys + grader (case-C decision = "No actionable
  findings" per the update's rule).

## Pre-registered prediction

- Cases A, B, D: NO difference expected. The negatives block does not
  trigger on in-scope review tasks; the Incomplete rule is irrelevant
  there. Any delta = noise or grading artifact, not update effect.
- Case C: `without` may say Incomplete OR No actionable findings
  (ambiguity — the smoke run already produced the latter under the
  ambiguous text); `with` should say No actionable findings.
- Predicted measurable difference at K=1: likely 0 cases; at most case C,
  and that would measure COMPLIANCE SHIFT toward the newly defined rule,
  not absolute quality gain (the `without` side is graded against a rule
  written after it).

## Results

- WITHOUT (HEAD skill): 4/4 PASS, gate MET (grading-without.json).
- WITH (updated skill): 4/4 PASS, gate MET (grading-with.json).
- Measurable difference at K=1: 0 cases, 0%.

Matches the pre-registered prediction. The without-condition case-C agent
also chose "No actionable findings", so the Incomplete clarification
produced no observable compliance shift on this model at K=1 (same as the
smoke run under ambiguous text). Conclusions: (1) the update causes no
regression on in-scope review tasks — the correct expectation for a
negatives-block addition; (2) its value (out-of-scope refusal, ambiguity
removal across models/runs) needs negative-trigger fixtures and K>=6 to
observe — see Phase 4.
