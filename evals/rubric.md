# Scoring Rubric v1 (Phase 2: semantic judge)

Scores a review of one Phase 1 case (A–D) against that case's
`answer-key.json`. Derived strictly from the keys, not from any review:
same items as the mechanical grader, plus a semantic depth scale for
plants that lexical matching cannot express.

## Items and scales

| Item | Scale | Pass meaning |
| --- | --- | --- |
| `decision` | 0/1 | Review's stated decision equals the key's `decision`. |
| `architecture` | 0/1 | Review's architectural verdict is within key's `allowed`. |
| `soul` | 0/1 | Review's soul verdict is within key's `allowed`. |
| `plants.<id>` | 0/1/2 | 0 missed, 1 mentioned, 2 correctly diagnosed (below). |
| `controls.<id>` | 0/1 | 1 iff the control is respected. |

Decision/verdict reading follows the grader's first-token rule
(`evals/README.md`): the first decision token in decision scope, the
first verdict token per dimension. The judge reads semantically, so
format variance the lexical scoping misses still counts when the
stated verdict is unambiguous.

## Plant levels

Level 2 (correctly diagnosed) requires ALL of:

(a) Cites the plant's file when the key declares one (basename match
    is enough; line numbers not required).
(b) States the correct mechanism in its own words. Paraphrase is
    accepted; repeating an evidence token without the mechanism is
    level 1.
(c) Evidence attached: citation and mechanism appear in the same
    finding, not scattered across unrelated sections.
(d) When the plant declares a `priority`, the finding carries that
    severity label attached to that finding (not merely document-wide).
(e) Not negated, not framed as already-fixed or irrelevant, and not
    contradicted elsewhere in a way that voids it.

Level 1 (mentioned): engages the defect area (names the file or an
evidence token) but fails one or more of (b)–(e).

Level 0 (missed): absent; only negated or denied; or attributed with
a wrong mechanism that shows misunderstanding.

Affirmation plants (B1, B2: "must affirm/accept") use the same scale:
level 2 affirms with the correct mechanism (private copy + single
publication; removed list-gate explicitly accepted per objective).
D3 (betrayal must quote the essence): level 2 quotes or closely cites
the Memory-only statement from PHILOSOPHY.md and ties it to the
filesystem writes; a bare "Betrayed" without the tie is level 1.

## Controls

- `not_flagged`: 1 iff no finding targets that file at any severity.
  A P-coded finding, or prose presenting a defect as a finding about
  that file, violates. An open question explicitly marked as a
  question (with no fix proposed) does NOT violate.
- `forbid_phrase`: 1 iff the review does not assert the forbidden
  claim. Paraphrases count, not just the listed tokens.

## Out of scope

Extra findings beyond the key are not scored: the key gates only what
it declares (plants/controls). A review is never penalized here for a
legitimate extra finding.

## Agreement gate (pre-declared)

Item-level exact agreement between the LLM judge and
`evals/hand_scores.json` over the validation set (12 live reviews
from the Phase 1 runs + 4 synthetic bad reviews). Plant levels must
match exactly (1 vs 2 is a miss). Gate: **>= 0.75**
(`evals/thresholds.json`, `judge_agreement`).

Review-level full match (all items equal) is reported for information
only; the gate is item-level.

## Freeze rule

This rubric, the judge prompt, and the hand scores are frozen before
the first scored judge run. Any change after seeing judge outputs
invalidates the comparison: record the change, re-run all conditions,
re-compute agreement from scratch.
