# Engineering Assurance Foundation

Status: implemented per the roadmap gates — evidence adapters, code-reviewer envelope, five specialists, assurance integrator, A/B/C/D study, judge protocol, and K-2/K-3 independent re-grading. Each gate is recorded as a frozen run under `evals/runs/` with integrity tests under `tests/`. The existing `code-reviewer` remains executable as a standalone skill. No deployment permission is produced by this release.

## Deliverables

| Deliverable | Artifact |
| --- | --- |
| Source registry (verification-scoped) | [source-registry.yaml](../../references/source-registry.yaml) |
| Source-to-module traceability | [traceability.yaml](../../references/traceability.yaml) |
| Baseline gap analysis | [gap-analysis.md](gap-analysis.md) |
| Module boundaries | [epistemic-boundaries.md](epistemic-boundaries.md) |
| Evidence contracts | [evidence-model.md](evidence-model.md), [schemas](../../schemas/v0.1.0/assurance.schema.json) |
| Assurance-case contract | [assurance-case.md](assurance-case.md) |
| Dependency and independence model | [architecture.md](architecture.md) |
| Risk and escalation policy | [escalation-policy.md](escalation-policy.md) |
| Implementation roadmap | [roadmap.md](roadmap.md) |
| Research validation plan | [validation-plan.md](validation-plan.md) |

The research registry is technical design evidence. Verified bibliographic identity does not imply that every methodological claim has been verified, that a standard's full text was accessible, or that this system conforms to that standard. Read each entry's verification scope and limitations. Unverified material is not a normative basis.

Version 0.1.0 contracts support discussion and validation of example records. Passing the contract checker establishes record consistency only; it does not establish truth, causal validity, reviewer independence, safety, or deployment authority.

Key qualifications and design consequences: [research-findings.md](research-findings.md).
