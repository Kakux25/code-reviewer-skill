# Baseline Gap Analysis

Baseline: merge `3c5b1d9` as amended by `8ed6b94` (remote assurance
design foundation composed with the local validated eval program).
Supersedes the `950ae79`-era analysis, which described 4 fixtures and
no comparative evaluation; both statements are stale after the merge.

Validated local program (all in-tree, all green):

- Phase 1 eval harness: mechanical grader (plants/controls), frozen
  answer keys, pre-declared thresholds, deterministic CI gate
  (`evals/check_integrity.py`, stdlib only).
- Phase 2 calibrated LLM judge: rubric, frozen prompt, hand-score
  gold over 16 reviews, agreement 95/96 = 0.990 vs pre-declared
  gate >= 0.75 (cases A–D; judge outside the merge gate).
- Phase 3 battery: 20 fixtures (a–t) incl. shadow subset r/s/t
  (real-bug patterns), each with a key declaring its suite outcome
  (suites except c/o, whose absence is declared) + good/bad samples
  graded by the gate (co-located except a–d legacy in evals/samples/).
- Live calibration: blind with-skill smoke r1 3/16 → triaged refixture
  → r2 combined 16/16; every fixture validated by >= 1 live review
  against its final key.
- A/B lift: without-skill baseline 2/16 vs with-skill 16/16 (+14) on
  E–T, K=1, same model/day/keys. Lift is verdict/severity/essence
  discipline, not bug detection (baseline finds the bugs).

| Existing capability | Evidence in baseline | Required development |
| --- | --- | --- |
| Criteria before candidate judgment; disclose prior exposure | Establish independent criteria | Persist criterion IDs, versions, timing and scope |
| Concrete findings, guards, regressions and verification | Review the change and its effects | Machine-readable evidence/claim/refutation records |
| Architecture separate from functional correctness | Architectural complexity; architecture reference | Specialist ownership, quality scenarios, ADR observability and controlled delegation |
| Documented essence only; absent essence is Unverifiable | Soul verification; soul.md | Preserve during decomposition; never manufacture principles |
| Bounded checks; skipped tests are not success | Verify functionality separately | Tool receipts, artifacts, freshness and failed-collector semantics |
| Lexical Python caller discovery | scripts/trace_callers.py | Preserve unresolved aliases/dynamic dispatch limitations; do not promote to complete call graph |
| Human-readable findings and brief mode | report-format.md | Stable envelopes with module/producer/dependence information |
| 20-case battery, calibrated judge, A/B lift run | tests/review-cases; evals/ | Cross-model/family replication, K>=6, judge validation on E–T, held-out battery |

Missing: dynamic feedback models, system-level hazard/control analysis,
structured incident applicability (no production corpus), coordination
evidence, assurance arguments, defeaters, dependence accounting,
revision-aware invalidation, and the full A/B/C/D specialist comparison
(only the with/without-skill A/B exists; C/D need the specialists).

The review skill already has strong local discipline, confirmed by the
lift run. Replacing it wholesale would risk losing known behavior. Keep
standalone behavior stable until the composed mode has parity tests. In
composed mode, restrict local conclusions to behavior and route
architectural judgments to the architecture specialist. A migration must
preserve regression discrimination (case a), alternative implementations
(b/k/l), partial coverage (c/o), and principle-violation detection (d/m/n soul
verdicts) — all exercised by the battery and the integrity gate. The
no-authorship rule has no dedicated fixture yet (rule text only, in
SKILL.md); it needs a parity test before composed mode can claim it.

Accuracy claims supported: with-skill over without-skill (+14, K=1,
E–T, mechanical grading, same model) and judge-vs-hand agreement
(0.990, A–D). Broader superiority, cross-model generality, and any
specialist/integrator capability claims remain unsupported pending the
validation plan.

## Status update 2026-09-20 (addendum; analysis above preserved)

The "Missing" paragraph is now implemented as roadmap gates 3–9
plus judge and K-2/K-3 re-grading: five specialists with 4/4 smoke
runs, shared envelopes, assurance integrator, A/B/C/D study (22
cells), calibrated judge (A–D), and independent tie-break
confirmation — all frozen under `evals/runs/`. Still open from
this analysis: cross-model/family replication, K≥2, judge
validation on E–T, a held-out battery, and the no-authorship
parity fixture (rule text only, no dedicated fixture yet).
