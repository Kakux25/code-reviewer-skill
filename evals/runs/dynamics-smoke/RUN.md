# RUN: dynamics-smoke (Gate 6 live validation)

Date: 2026-09-20. Skill: `skills/system-dynamics-reviewer/`
(run `dynamics-smoke`). Method: 4 blind agents, dynamics skill
only, one per fixture; each instructed to build the causal model
first, run the simulator read-only where one exists, and NOT to
open `expected.json` (blindness by instruction, unverified). Human
grade vs `expected.json` (verdict + must/must-not, semantic);
grades frozen in `grades.json`; envelopes built from grades via
`scripts/dynamics_envelope.py` into `envelopes/`.

## Result: 4/4 match expected

| case | kind | expected | live verdict | grade |
|------|------|----------|--------------|-------|
| dyn-a | gold | unstable | Unstable | match |
| dyn-b | adversarial | unstable | Unstable | match |
| dyn-c | negative | stable | Stable | match |
| dyn-d | abstention | uncalibrated | Uncalibrated | match |

Simulator honesty: every quoted number was reproduced exactly
(a: base peak 20, candidate ~7.2e19; b: run(1)=20, run(300)=60;
c: peak 14 plus sensitivity variants). Agents ran the sims;
no fabricated numbers. Green suites documenting disaster were
read as supporting Unstable, per the calibration rule.

Semantic resolutions (lexical pre-check flagged, human resolved):
- a: `bounded` describes the base peak factually and sizes a fix;
  `Stable` only in `supports Unstable, not Stable`: clean.
- b/d: `Stable` only in negations (`not Stable`, `forbid
  upgrading ... to Stable`): clean.
- c: full lexical pass.

Envelopes: 4/4 schema-valid; claim C5 (candidate exhibits no
unhandled destabilizing feedback) mirrors graded verdicts
(defeated/defeated/supported/unresolved); declared suites
executed green (a/b/c dynamic exit=0; d absent by design);
decision always INSUFFICIENT_EVIDENCE (single reviewer never
ACCEPTs).

## Post-review fixes (chain validation: 1 P2 + P3s)

- P2 (stray `__pycache__` in fixture dirs): removed; verified
  `__pycache__/` + `*.pyc` are git-ignored, so no commit risk
  existed — hygiene only. Source: live agents importing sims
  without the bytecode flag; the Gate 1 collector always sets it.
- dyn-c suite pins the exact peak (`assertEqual(run(), 14)`)
  instead of a margin-1 bound, in both copies.
- dyn-c request.md notes the fixture tests candidate-only
  stability (base policy unmodeled).
- dyn-a key narrowed: must_not `bounded` -> `candidate stays
  bounded` (base descriptions no longer trip it); remaining
  `stable` hit is the documented `not Stable` negation.
- Missing exposure disclosures in a/b reviews accepted as-is:
  frozen live artifacts, not back-filled.
- Envelopes regenerated (hashes updated); run dir committed with
  the gate.

## Threats / limits

- Grader is fixture author (K=1); same-author bias possible.
  Recorded in grades.json, envelope exposure notes, and U5
  uncertainties (next_action: second independent grade).
- Same-model family producer/grader; blindness by instruction only.
- K=1 per fixture; no inter-rater data. Gate 6 claims
  smoke-calibration only, not a calibrated judge.
- Simulators are stylized (fixed schedules, no noise); they test
  loop reasoning, not production prediction.
