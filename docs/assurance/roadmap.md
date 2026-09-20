# Implementation Roadmap

Status 2026-09-20: gates 1–9 complete, each with a frozen run under
`evals/runs/` and integrity tests under `tests/`, followed by the
judge protocol and K-2/K-3 independent re-grading. The gate list
below is preserved as the plan of record.

## Current release

Complete the source registry, traceability, boundaries, gap analysis, decision records, versioned contracts, synthetic examples and contract checks. Preserve the existing reviewer. This is the complete first design milestone, not a claim that the seven-module system is operational.

## Ordered implementation gates

1. **Evidence adapters.** Revision-safe Git acquisition, receipts for existing project checks, ADR/ownership inventories and lexical graph leads. Gate: dirty-tree, failed-tool, stale-artifact and incomplete-parser cases must never appear successful. Reuse available tools; do not promise compiler/formal/runtime coverage without adapters.
2. **Code reviewer adapter.** Convert existing output to the shared envelope without weakening its standalone contract. Gate: existing fixtures plus guard-present, pre-existing-defect, alias and abstention controls retain expected outcomes.
3. **Architecture reviewer.** Independent criteria, views/concerns, ADR observability and quality scenarios. Gate: correct unusual designs accepted, local-success/global-damage detected, undocumented organizational decisions escalated. Only then route composed architecture ownership away from code-reviewer.
4. **STPA reviewer.** Losses and control structure before code constraints. Gate: omitted action, wrong action, timing/order and duration scenarios; distinguish unverified constraints from enforced ones. Qualified domain review is needed for safety-critical claims.
5. **Incident memory.** Start with curated structured cases and explicit applicability rules. Gate: superficial matches rejected, applicable mechanisms recovered, no-match abstention, authorized retention and redaction verified.
6. **Dynamics reviewer.** Evidence-tagged variables/links, stock/flow consistency, delay and sensitivity checks. Gate: retry amplification/queue growth cases, balancing counterexamples and uncalibrated-model abstention.
7. **Sociotechnical reviewer.** Required-versus-observed coordination graph. Gate: ownership ambiguity, stale mappings and valid alternate handoffs; zero unsupported claims about human traits.
8. **Assurance integrator.** Assemble claims and investigate defeaters only after specialist contracts stabilize. Gate: shared evidence cannot be counted repeatedly; contradictions, cycles, missing coverage and changed context prevent acceptance.
9. **Comparative research evaluation.** Run the controlled A/B/C/D study before any accuracy or superiority claim.

Each specialist must have gold cases, negative controls, adversarial inputs, known false positives/negatives and abstention tests. Each gate creates a release decision; unfinished work remains explicitly pending. No automatic remote model spending, deployments, or production incident retention is introduced by this roadmap.
