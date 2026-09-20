# RUN: integrator-demo (Gate 8 live demonstration)

Date: 2026-09-20. Tool: `scripts/assemble.py` (run `demo`).
No LLM involved: the integrator is deterministic logic over
assurance fragments. Three CLI scenarios, inputs frozen in
`fragments/`, outputs frozen in `outputs/`:

## Scenarios

1. `accept.json`: two synthetic same-scope fragments
   (code-reviewer + architecture-reviewer, both supported, sharing
   one evidence digest), required = those two.
   Decision: ACCEPT, 0 defeaters, 2 evidence items deduped to 1
   unique digest, both claims' references resolve post-aliasing.
2. `defeated.json`: same code fragment + a defeated STPA fragment.
   Decision: INSUFFICIENT_EVIDENCE, 1 blocking defeater naming
   the defeated claim, CTOP defeated.
3. `real-refusal.json`: five REAL frozen smoke envelopes (the
   `a` case from each of the five `*-smoke` suites), default
   required set. Decision: INSUFFICIENT_EVIDENCE, 1 blocking
   defeater: scope mismatch (five different fixture contexts).
   The integrator refuses to merge different changes — verified
   on real data.

## Notes

- `authorization` stays `not_granted` even on ACCEPT: the schema
  constrains it so. ACCEPT means assurance complete, not
  authorized (deployment authority is never granted here).
- Required reviewers are a parameter (default: all 7 MODULES).
  The smoke fragments can never ACCEPT under any required set
  covering them: their claims carry `assumptions` (K=1 human
  grade), which the contract counts as unclosed. The integrator
  surfaces that honestly instead of laundering it.
- Structural failures (scope mismatch, id collision, dependency
  cycle, empty input, reserved-id use) produce refusal cases
  carrying no fragment items — verified by `tests/integrator/`
  (22 tests), never a crash. Full decision table lives in the
  tests, not here.
- Owner decision (chain-review P3): the default required set
  stays all 7 MODULES including `final-engineering-judge`, even
  though no judge envelope exists yet and default-required ACCEPT
  is therefore unreachable. Conservative by design; narrow
  `--required` for partial assemblies. Emitting a real judge
  envelope is future work (post Gate 9), not a silent default cut.
- CTOP lists subclaim ids in `dependencies`, so the argument
  graph is explicit at the top, not just prose in E-ASM.

## Post-review fixes (chain validation: 2 P1 + P2 + P3s)

- P1 (dangling refs): evidence aliasing now covers defeaters,
  causal_links, incident_cases, and safety_constraints, driven by
  the REF_EVIDENCE constant (was dead); regression tests per
  group (defeater + causal; incident/safety share the path).
- P1 (identical dupes): `assemble([f, f])` merges to one copy
  instead of crashing on duplicate identifiers.
- P2 (namespace): CTOP / E-ASM / D-ASM-* are reserved; fragment
  use refuses with a blocking defeater.
- P3s: `--required ""` falls back to default; null digests never
  dedupe; cycle detection is iterative (no recursion limit);
  CTOP dependencies added (above).
