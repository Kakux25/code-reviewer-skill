# RUN: memory-smoke (Gate 5 live validation)

Date: 2026-09-20. Skill: `skills/incident-memory/`
(run `memory-smoke`). Method: 4 blind agents, memory skill only,
one per fixture; each ran `scripts/incident_memory.py` for ranking
and was instructed NOT to open `expected.json` (blindness by
instruction, unverified). Human grade vs `expected.json` (verdict +
must/must-not, semantic); grades frozen in `grades.json`; envelopes
built from grades via `scripts/memory_envelope.py` into `envelopes/`.

## Result: 4/4 match expected

| case | kind | expected | live verdict | grade |
|------|------|----------|--------------|-------|
| mem-a | gold | blocked | Blocked | match |
| mem-b | adversarial | clear | Clear | match |
| mem-c | abstention | nomatch | No match | match |
| mem-d | negative | clear | Clear | match |

Retrieval honesty: reported rankings for a/b/c were reproduced
exactly with the recorded queries (a: INC-001=8; b: INC-002=5,
INC-001=4; c: empty). For d the review records only a query
paraphrase, so INC-001=9 was reproduced with a reconstructed
query, not the exact invocation (chain-review P3-1; d.md kept
as-is as frozen live evidence — back-filling a command into it
would falsify the record).

Semantic resolutions (lexical pre-check flagged, human resolved):
- b: `blocked` appears only in `not blocked on suspicion`: clean.
- c: `INC-001/002/003` named only inside `none ranked`; empty
  ranking reported and abstained, no incident forced: clean.
  Post-review, the mem-c key was reworked (must_cite narrowed to
  `empty ranking`; must_not to decision-label `Applied`,
  `transfers`, `blocked`) so it reads correctly mechanically;
  grade still match.
- No restricted content (costs, customers, hosts) quoted in any
  review; d states restricted fields explicitly not quoted.

Envelopes: 4/4 schema-valid; claim C4 (candidate clear of
applicable incident precedent) mirrors graded verdicts
(defeated/supported/unresolved/supported); case-base revision
pinned by content hash; decision always INSUFFICIENT_EVIDENCE
(single reviewer never ACCEPTs).

## Post-review fixes (chain validation: 1 P2 + P3s)

- P2 (vacuous weight test): `test_exact_scores_pinned` now pins
  the recorded live scores (a: INC-001=8; b: INC-002=5, INC-001=4).
  Sensitivity proven: temporarily swapped 1/3 weights fail the new
  test, restored weights pass 16/16.
- Retrieval hardening: case entries tokenized like queries
  (multi-word entries can match); `render_public` deep-copies.
- mem-c key rework (above); `import time` added to mem-d
  candidate (judgment-only fixture, never executed; envelope
  revision hash updated).
- Producer `unknown/unknown` in envelopes = human-driven smoke run
  (live-agent reviews, human grades, no model attested): honest
  default, kept.

## Threats / limits

- Grader is fixture author (K=1); same-author bias possible.
  Recorded in grades.json, envelope exposure notes, and U4
  uncertainties (next_action: second independent grade).
- Same-model family producer/grader; blindness by instruction only.
- K=1 per fixture; no inter-rater data. Gate 5 claims
  smoke-calibration only, not a calibrated judge.
- Case base is a 3-case seed; production use needs curation,
  retention policy, and redaction review beyond the structural
  render_public strip.
