# PROTOCOL: A/B/C/D study (Gate 9, pre-registered)

Date: 2026-09-20. Question: what does each layer add — generic
review (A), code-reviewer skill (B), matched specialist skills (C),
full pipeline with envelopes + integrator (D)?

## Cases (ground truth = frozen keys)

| study id | fixture | expected |
|----------|---------|----------|
| code | tests/review-cases/case-a (discount /10 bug, suite FAILS by design, arch preserved) | decision Changes requested + /10 plant + arch High + suite-fails control |
| arch | tests/arch-cases/arch-b (api->store skip, tests pass) | violates |
| stpa | tests/stpa-cases/stpa-a (omitted presence guard + wrong on fault) | unsafe |
| mem | tests/incident-cases/mem-a (unbounded retry loop) | blocked (INC-001) |
| dyn | tests/dynamics-cases/dyn-a (immediate retries, 20 vs 7.2e19) | unstable |
| soc | tests/socio-cases/soc-a (CHG-101, no team-ledger ack) | uncoordinated |

Abstention probes (A/B only; C abstention already proven in Gates 4/7):

| probe id | fixture | expected |
|----------|---------|----------|
| abs-stpa | tests/stpa-cases/stpa-d (no safety docs) | abstain (no invented model) |
| abs-socio | tests/socio-cases/soc-d (no ownership records) | abstain (no invented owner) |

## Arms

- A (generic): no skill. Prompt: "Review this change for defects"
  + fixture request.md paths. Same fixtures, no method.
- B (code-reviewer): code-reviewer skill only, all cases.
- C (matched specialist): the domain skill per case
  (code/arch/stpa/memory/dynamics/socio). Fresh runs (K=1).
- D (full pipeline): C reviews converted to envelopes via the
  Gate 2-7 adapters + merged per case with scripts/assemble.py.
  D verdicts = C verdicts by construction; D measures pipeline
  mechanics (fragments validate, assembly decision + defeaters),
  not better judgment. CANNOT ACCEPT: each case has one reviewer,
  so the correct D outcome is INSUFFICIENT_EVIDENCE with missing-
  reviewer defeaters (single-reviewer-never-accepts composes).

## Grading rubric (human, K=1, semantic)

Per cell: `verdict_correct` (bool vs expected), `substance`
(fraction of expected must_state concepts present, 0..1),
`false_claim` (bool: any must_not-equivalent false statement),
`notes` (resolutions). Arm A/B agents may use different verdict
words; mapping to expected is semantic and documented per cell.
Citation discipline is recorded in notes, not scored (A was never
taught to cite).

## Threats (pre-registered)

- K=1 per cell; same-model family everywhere; grader is fixture
  author; agents blind to keys by instruction only.
- Arm A prompts still point at fixture request files (which name
  the review frame); A is "generic reviewer", not "no context".
- 6 hand-picked cases; no statistical power claimed. The study
  shows mechanism (what each layer adds), not a benchmark number.
