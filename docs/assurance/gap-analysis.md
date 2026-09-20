# Baseline Gap Analysis

Baseline: repository commit `950ae7990392d2c445e650a8f2f5c35329785c9b`, `skills/code-reviewer/SKILL.md` and its references. The remote had advanced beyond the earlier `ai-code-reviewer` installation. This design uses the current `code-reviewer` contract and preserves its files unchanged.

| Existing capability | Evidence in baseline | Required development |
| --- | --- | --- |
| Criteria before candidate judgment; disclose prior exposure | Establish independent criteria | Persist criterion IDs, versions, timing and scope |
| Concrete findings, guards, regressions and verification | Review the change and its effects | Machine-readable evidence/claim/refutation records |
| Architecture separate from functional correctness | Architectural complexity; architecture reference | Specialist ownership, quality scenarios, ADR observability and controlled delegation |
| Documented essence only; absent essence is Unverifiable | Soul verification; soul.md | Preserve during decomposition; never manufacture principles |
| Bounded checks; skipped tests are not success | Verify functionality separately | Tool receipts, artifacts, freshness and failed-collector semantics |
| Lexical Python caller discovery | scripts/trace_callers.py | Preserve unresolved aliases/dynamic dispatch limitations; do not promote to complete call graph |
| Human-readable findings and brief mode | report-format.md | Stable envelopes with module/producer/dependence information |
| Four review fixtures including principle violation | tests/review-cases | Broader independent gold labels, counterexamples and abstention cases |

Missing: dynamic feedback models, system-level hazard/control analysis, structured incident applicability, coordination evidence, assurance arguments, defeaters, dependence accounting, revision-aware invalidation, and comparative evaluation.

The review skill already has strong local discipline. Replacing it wholesale would risk losing known behavior. Keep standalone behavior stable until the composed mode has parity tests. In composed mode, restrict local conclusions to behavior and route architectural judgments to the architecture specialist. A migration must preserve regression discrimination, alternative implementations, partial coverage, principle versioning, and the no-authorship rule.

No claim of better review accuracy is supported by the current fixtures. The new contracts provide record structure, not additional validated reviewer capability.
