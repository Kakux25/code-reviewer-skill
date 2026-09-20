# RUN: arch-smoke (Gate 3 live validation)

Date: 2026-09-20. Skill: `skills/architecture-reviewer/`
(run `arch-smoke`). Method: 4 blind agents, arch skill only, one per
fixture; each instructed to read repo docs before the candidate and
NOT to open `expected.json` (blindness by instruction, unverified).
Human grade vs `expected.json` (verdict + must/must-not, semantic);
grades frozen in `grades.json`; envelopes built from grades via
`scripts/arch_envelope.py` into `envelopes/`.

## Result: 4/4 match expected

| case | kind | expected | live verdict | grade |
|------|------|----------|--------------|-------|
| arch-a | negative | conforms | Conforms | match |
| arch-b | gold | violates | Violates | match |
| arch-c | abstention | uncertain | Uncertain | match |
| arch-d | adversarial | violates | Violates | match |

Semantic resolutions (lexical pre-check flagged, human resolved):
- a: `forbidden` appears only inside the quoted C2 criterion text
  while concluding Conforms: clean (no violation claimed).
- b: `api/ imports store/ directly` is a punctuation-only variant
  of must_state `api imports store`: accepted.
- c: `conforms` appears only in negations (`no supportable
  Conforms/Violates verdict exists`; `do not treat ... as
  conformance`): clean. `no ADR`/`ownership unknown` covered
  semantically (`no covering record found`; `who owns the app`
  escalated 3x).
- d: full lexical pass; rationale explicitly named adversarial.

Envelopes: 4/4 schema-valid; claim statuses mirror graded verdicts
(supported/defeated/unresolved/defeated); decision always
INSUFFICIENT_EVIDENCE (single reviewer never ACCEPTs).

## Post-review fixes (chain validation findings)

- P1 (claim semantics): claim restated from "review matches
  expected" to "Candidate arch-X conforms to its documented
  architecture (per human-graded review)", so defeated for b/d is
  coherent (all grades match expected; statuses mirror verdicts).
  Pinned by `test_claim_is_about_candidate_conformance`.
- P2 (arch-a suite exit=1): `test_conformance.py` opened a
  cwd-relative path and failed under the Gate 1 collector while the
  review claimed 2/2 pass. Fixed to `__file__`-relative paths in
  both repo/ and candidate/ copies; envelopes regenerated (a now
  exit=0; candidate revision hash changed accordingly). Pinned by
  `test_declared_suites_executed_green`. The live agent ran the
  suite from inside candidate/ (hence 2/2); the envelope now agrees.
- P3 (criteria_before_candidate): regenerated with
  `--criteria-first`; justified by frozen review structure (rubric
  sections built from repo docs precede candidate assessment in all
  four reviews). Code-review P3s also applied: is_dir guards in
  arch adapter, tempfile stub reviews, run dir committed.

## Threats / limits

- Grader is fixture author (K=1); same-author bias possible.
  Recorded in grades.json, envelope exposure notes, and U2
  uncertainties (next_action: second independent grade).
- Same-model family producer/grader; blindness by instruction only.
- K=1 per fixture; no inter-rater data. Gate 3 claims
  smoke-calibration only, not a calibrated judge.
