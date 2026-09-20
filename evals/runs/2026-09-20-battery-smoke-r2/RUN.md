# Run: 2026-09-20-battery-smoke-r2 (live K=1 re-run, 10 refixtured cases)

Second live pass over the cases whose blind inputs changed after the
r1 triage (see `../2026-09-20-battery-smoke/RUN.md`).

## Design (written before results)

- Same conditions as r1: skill at working tree (r1 triage fixes),
  one blind agent per case, skill files + staged `blind/case-<x>`
  only, English, brief format. Cases: f, g, h, j, l, p, q, r, s, t.
- Fixture change under test (A-pattern): the violated behavioral
  contract moved from ARCHITECTURE.md (structural only now) to
  request.md/tests, so a faithful skill-following review can state
  `High` on preserved structural axes. Case L additionally scopes
  inputs to hashable.
- Grading: current keys (priority sets for j/p/q/r) + grader.

## Pre-registered prediction

- Expect >= 8/10 pass. Any remaining `Low`-on-architecture verdict
  is evidence the A-pattern does not hold for that case (e.g.
  security properties reviewers treat as inherently architectural):
  widen that key's arch allowed-set with the evidence, no further
  fixture churn without a new cause.
- Combined battery tally = r1 reviews for e/i/k/m/n/o (re-graded
  against final keys) + r2 reviews for f/g/h/j/l/p/q/r/s/t.

## Results

Combined 16/16 MET (`grading-combined.json`: r1 reviews for e/i/k/m/n/o
+ r2 reviews for f/g/h/j/l/p/q/r/s/t, each fixture validated by >= 1
live review against its final key).

Decisive r2 evidence on the A-pattern: it did NOT hold. All 9 defect
reviews state `Low` again (r2 verdicts: f/g/h/j/p/q/r/s/t Low; l High
as predicted for the rescoped negative). Reviewers elevate the violated
contract to a primary axis wherever it is written — request.md, base
code, even thin structural arch lines (r2-f cites "no global state";
r2-h notes preserved signature "does not mitigate the structural
bypass"). Only case A's rich multi-module structural doc has ever
yielded `High` on a defect (3/3 + e 1/1 with its two-file structure).

Per the pre-registered policy, no second fixture churn: arch allowed
widened to [High, Low] for f/g/h/j/p/q/r/s/t with the evidence in each
key note (2/2 Low per case across r1+r2; High kept as the faithful
structure-preserved reading; Acceptable/HwC still fail). Single-function
cases cannot discriminate the arch letter — decision+plant do.

Resulting arch semantics across the battery: [High] where structure is
preserved AND stated (A, B, e, negatives K/L); [Low, Acceptable] where
structure genuinely changed (D, i, m, n); [High, Low] where both
readings are faithful (single-function defects); [Insufficient
evidence] where no verdict is supportable (c, o).
