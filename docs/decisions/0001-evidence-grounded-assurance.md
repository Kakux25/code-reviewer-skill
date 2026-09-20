# ADR-001: Evidence-Grounded Assurance Contracts

Status: accepted for the design foundation; specialist runtime delivery remains gated.

## Decision

Use separate specialist assessments over versioned raw evidence, with a nonvoting assurance case and a distinct authorization boundary. Keep the current standalone code-reviewer unchanged. Introduce schema and consistency checks before runtime orchestration.

## Context

The existing skill combines useful local, architectural and documented-principle review. The proposed additional disciplines require different evidence and cannot be justified by relabeling a common quality prompt. Research provenance is now explicitly required in the technical registry; product presentation remains independent of attribution.

## Alternatives

A linear verdict cascade is simple but amplifies unexamined conclusions. Majority voting is cheap but ignores shared failure and missing obligations. A monolithic reviewer has low overhead but obscures discipline-specific evidence. Full immediate implementation would lack validated contracts and comparison data.

## Evidence

The frozen baseline demonstrates rubric, counterexample and uncertainty requirements. Source-specific evidence and access limits are recorded in the registry; the traceability matrix determines which verified claims may support rules. Bibliographic verification is not normative access to a standard.

## Tradeoffs

Explicit contracts add record-keeping and cannot prove truth. Separate first-pass contexts reduce conclusion contamination but do not guarantee model independence. The first milestone delivers design and checkable records while deferring operational collectors and new reviewer accuracy claims.

## Source IDs

LOCAL-code-reviewer and the verified claim subsets of S01–S16, as assigned per rule in traceability.yaml. Unverified identifiers or unavailable implementation documents cannot justify a normative rule.

## Confidence and uncertainty

High confidence in the need to preserve provenance and avoid score averaging; empirical benefit of specialization and the integrator remains unmeasured. System-specific safety and organizational assumptions require domain evidence.

## Reversal conditions

Revise boundaries if parity tests expose lost baseline behavior, specialists duplicate the same judgment, or comparative evaluation shows unjustified complexity. Revise contracts when concrete counterexamples expose missing provenance or unsafe acceptance. Record revisions with migration rules rather than silently reinterpreting existing data.
