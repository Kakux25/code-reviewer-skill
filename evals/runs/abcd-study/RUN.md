# RUN: abcd-study (Gate 9 results)

Date: 2026-09-20. Protocol: `PROTOCOL.md` (pre-registered before
any study run; ordering is mtime-anchored — PROTOCOL written
before any review/grade file — not commit-anchored, disclosed
per chain review). 22 key-blind cells (6 cases x 3 arms + 2 probes
x 2 arms), human-graded K=1 against frozen keys (semantic rubric).
Reviews frozen in `reviews/`, grades in `grades.json`, D pipeline
outputs in `D/`.

## Results

| arm | verdict accuracy | mean substance | false-claim rate |
|-----|------------------|----------------|------------------|
| A generic (8 cells) | 7/8 | 0.90 | 1/8 |
| B code skill (8 cells) | 8/8 | 0.96 | 0/8 |
| C specialist (6 cells) | 6/6 | 1.00 | 0/6 |

Cell notes in `grades.json`; every resolution documented there.

## What each layer adds (mechanism, not benchmark)

- A is strong on legible fixtures: 6/6 main-case verdicts,
  exact sim numbers (dyn-A: 20 / 7.2e19), executed suite reads,
  even unprompted case-file use (mem-A). The fixture requests
  scaffold the frame (pre-registered threat) — A measures
  "generic reviewer with good context", not "no context".
- B over A: abstention discipline. abs-stpa-A declared Safe with
  no model (the study's only false claim); abs-stpa-B refused
  the safety verdict with Insufficient evidence. Everywhere else
  B matches A on verdicts with fuller method (rubrics, execution
  proofs, scope discipline: dyn-B declined the dynamics verdict
  as outside-skill).
- C over B: domain method + precedent linkage. mem-B found the
  bug but never named INC-001 (substance 0.67); mem-C recorded
  the ranking (INC-001=9, reproduced exactly) and transferred by
  mechanism. stpa-C/dyn-C/soc-C add UCA variants, closed loops,
  map-first rows — the vocabulary the integrator and future
  judges can check mechanically.
- D over C: pipeline mechanics, not judgment. 6/6 fragments
  schema-valid; per-case assembly (required=all-6) yields
  INSUFFICIENT_EVIDENCE with 7 defeaters each (5 missing +
  defeated + unclosed): single-reviewer-never-accepts composes
  through the integrator. Arch-solo assembly shows a defective
  change correctly unassured via defeated-claim defeater.
  Required=all-6 excludes `final-engineering-judge` (no judge
  envelope exists anywhere yet); per the Gate 8 owner decision,
  narrowing is documented process, not a silent default cut.

## D finding: mechanical grader false positive

D/code's C1 claim is defeated although code-C is semantically
perfect (decision/arch/soul/plant/suite all correct): control
A-C1 trips lexically on correct traceability prose
("propagating through `checkout.py:5`" inside the P1 line).
This is the documented lexical-proxy limitation
(`evals/thresholds.json` notes: "coarse lexical proxy, not review
quality"), now observed in the wild. The pipeline surfaces it
honestly (defeated + unclosed defeaters) instead of laundering
it. Human grade stays correct; no key/threshold was changed
post-hoc (frozen rule).

## Post-review fixes (chain validation, P3-only)

- `criteria_before_candidate` now true on all 6 D fragments:
  D/code was regenerated with `--criteria-first` (its semantics
  for the code adapter = answer key frozen before the run, true:
  battery v2.1 predates the study). Specialist adapters use
  rubric-first semantics, evidenced structurally in each review.
- RUN clarifies judge exclusion (above) and mtime-anchored
  pre-registration (header); "blind" -> "key-blind" throughout
  the header claim.
- Study test renamed to `test_protocol_present` with content
  markers (was existence-only under an overclaiming name).

## Threats (as pre-registered, plus observed)

- K=1, same-model family, grader-is-author, blindness by
  instruction only, 6 hand-picked cases: no statistical power
  claimed. One run per cell; variance unmeasured.
- Request scaffolding inflates A (see above). A cleaner A/B gap
  would need unscaffolded prompts — future work, disclosed here
  rather than re-run post-hoc.
- B/C agents necessarily read candidate files while rubric-building
  (exposure disclosed in-review, not blind); keys stayed blind.
