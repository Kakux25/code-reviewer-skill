# RUN: stpa-smoke (Gate 4 live validation)

Date: 2026-09-20. Skill: `skills/safety-stpa-reviewer/`
(run `stpa-smoke`). Method: 4 blind agents, STPA skill only, one per
fixture; each instructed to read repo safety docs before the
candidate and NOT to open `expected.json` (blindness by
instruction, unverified). Human grade vs `expected.json` (verdict +
must/must-not, semantic); grades frozen in `grades.json`; envelopes
built from grades via `scripts/stpa_envelope.py` into `envelopes/`.
Fixtures are analysis-only (no suites by design).

## Result: 4/4 match expected

| case | kind | expected | live verdict | grade |
|------|------|----------|--------------|-------|
| stpa-a | gold | unsafe | Unsafe | match |
| stpa-b | adversarial | unsafe | Unsafe | match |
| stpa-c | negative | safe | Safe | match |
| stpa-d | abstention | unanalyzable | Unanalyzable | match |

Semantic resolutions (lexical pre-check flagged, human resolved):
- a/b/d: `safe`/`unsafe` hits are substrings of method vocabulary
  (`Safety constraints`, `Safety verdict: Unsafe`,
  `unsafe-control-action` sweep, `safety-reviewed`) — never a
  contrary verdict claim. Clean.
- c: `interlock` term absent, but every guard verified per-condition
  including the 60-minute boundary exactly, full UCA sweep negative,
  enforcement statuses cited with lines: concept present, intent
  satisfied, accepted. `unsafe` only in the method sweep with
  negative conclusions: clean.

Envelopes: 4/4 schema-valid; claim C3 (candidate free of unhandled
unsafe control actions) mirrors graded verdicts
(defeated/defeated/supported/unresolved); decision always
INSUFFICIENT_EVIDENCE (single reviewer never ACCEPTs).

## Post-review fixes (chain validation, P3-only)

- stpa-c key `interlock` -> `guard` (term was ungrounded in fixture
  vocabulary; frozen review states `guard` throughout, grade still
  match). H3 added to stpa-c docs (SC3 had no parent hazard; live
  review glossed `overheat`, now covered for future runs).
- stpa-b control-structure gained the step-cadence line (0.5 s, so
  first-step open meets SC1); verdict always turned on the explicit
  30 s candidate delay, unaffected.
- Adapter: `--criteria-first` help disambiguated (safety model);
  suite branch now checks `candidate/tests/` before declaring
  absence (all four still absent by design, pinned by
  `test_frozen_suites_are_absent_by_design`).
- `c.md` backticked verdict line kept as-is: frozen live artifact,
  grade unaffected. Envelopes regenerated (revision + rubric
  hashes updated accordingly).

## Threats / limits

- Grader is fixture author (K=1); same-author bias possible.
  Recorded in grades.json, envelope exposure notes, and U3
  uncertainties (next_action: second independent grade).
- Same-model family producer/grader; blindness by instruction only.
- K=1 per fixture; no inter-rater data. Gate 4 claims
  smoke-calibration only, not a calibrated judge.
