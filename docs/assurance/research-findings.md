# Research Findings and Design Consequences

- S01/S02: official identity and summaries are accessible; complete normative text was not. Use vocabulary within that scope, not a compliance claim.
- S04: paper, prompts and runner were inspected. The runner can treat output-file existence as completion; this project requires validation. Dataset metadata and a frozen revision were verified, not the dataset contents or reported training gains.
- S05: a retrieval-based noncompliance rule can mistake missing evidence for violation. Preserve uncertainty unless positive evidence supports a conflict.
- S06: generated causal diagrams propose structures; they do not establish causality.
- S07: official handbook identity and identifier were verified, with limited full-text access. Detailed procedural conformance needs further handbook review.
- S08: bounded formal analysis is demonstrated; runtime enforcement is not established for arbitrary systems.
- S10: the study reports no statistical relationship with bugs/churn in its studied setting. It motivates careful coordination analysis, not a promise of quality gains.
- S11–S14: argument structure, defeaters, dependence and residual doubt support nonvoting integration. Numerical combination remains deferred; different decomposition assumptions do not share a universal aggregation formula.
- S15: metadata and abstract are accessible; empirical evaluation details remain unverified.
- S16: the inspected revision uses a custom non-commercial license. No code was copied. Interface ideas are informative; its AND/minimum-score combination does not determine this project's assurance decision.
- S17: Sterman's textbook gives the dynamics module a mature footing the Bot paper (S06) cannot supply alone; catalog identity only, full text not reviewed, automated generation still frontier.
- S18: Klein's NDM fieldwork (experts under pressure) grounds incident-memory's mechanism/applicability discipline; RPD specifics unverified, publisher page direct access failed (403).
- S19: ARTEM has NO license (API null) — reuse prohibited; two-line README, HEAD an upload-style snapshot commit, AAAI claim self-described only. Implementation-reference patterns at most.
- Registry `type` enum gains `book` (S17/S18); books verified at catalog/synopsis level, never normative beyond their verified scope.
- S20/S21/S22: record identity covers the full observation (Git objects), builder/materials are mandatory provenance (SLSA), agents are inseparable from records (PROV-DM). Consequence: the evidence store retains material drift as new revisions; pins detect rollback, never freeze reads.
- S23/S24: bare concatenation permits framing collisions (SequenceHash); framing defects are not hash breaks (FIPS 180-4). Consequence: length-prefixed directory hashing.
- S25/S26: fail securely on contradiction (OWASP); assurance integration drops nothing silently (SACM). Consequence: digest conflicts and cross-group id collisions refuse the merge.
- S27/S28: runner exits conflate errors with failures (CPython unittest); import failures are excluded from fail-to-pass (SWE-bench). Consequence: designed-fail suites must fail by executed tests.
- S29/S30/S31/S32: bool is int (PEP 285), objects stay open unless closed (JSON Schema), allowlist validation (OWASP), unvalidated input is CWE-20. Consequence: exact judge-verdict allowlist with true-int types and no-crash traversal.
- Traceability gains rule `status` = `implemented` and `test_status` = `implemented_contract_tests` for the six tooling rules above; they ship with passing contract tests. `assurance-checker-001` (iterative cycle detection) has an empty basis by design: standard practice, consulted but not normatively sourced.

See the source registry for canonical locators, verified scopes, access limitations and frozen revisions. These consequences are design choices, not claims of reproducing source results.
