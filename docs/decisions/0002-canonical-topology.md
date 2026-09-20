# ADR-0002: Canonical Assurance Topology and Requirement-Model Ownership

Status: accepted for the design foundation; runtime orchestration remains gated per roadmap.

## Decision

1. The canonical execution topology is the fan-out in
   `docs/assurance/architecture.md`: versioned criteria and risk scope
   → immutable evidence store → six independent specialist assessments
   → assurance case → defeater challenge (loops back to re-scope)
   → scoped recommendation.
   The linear reviewer chain in the originating reference brief is
   superseded for execution semantics. A scheduling order (e.g. the
   roadmap's gate order) remains useful for implementation and for
   staged rollout, but it is not an epistemic dependency: no
   reviewer's verdict is a premise for another reviewer's first pass.
2. The reference brief's `REQUIREMENT MODEL` box is owned by the
   evidence layer's scoping step, not by the final judge. It is the
   versioned record of risk class, required reviewer coverage,
   obligation set, context, and assumptions, produced from change
   objective + system context + base before detailed candidate
   assessment (per `escalation-policy.md`). All specialists consume
   it; the judge assembles against it but never re-scopes silently —
   a scope change versions the record and reopens dependent claims.

## Context

The originating brief (USER-BRIEF, external to this repo — its text is
not in-tree, so this characterization is recorded, not repo-verifiable)
drew a linear pipeline (code → architecture → dynamics → safety →
incident-memory → sociotechnical → judge). Linear cascades amplify
unexamined conclusions: an early verdict becomes a silent premise
downstream. The brief also placed an unowned `REQUIREMENT MODEL` at
the top. Meanwhile `architecture.md`
(scheduling-independent fan-out with a `Criteria` node) and
`escalation-policy.md` (scope set before assessment, owner recorded)
already describe the intended semantics; this ADR resolves the
conflict in their favor and assigns the missing owner.

## Alternatives

A strictly linear chain is simpler to schedule and to narrate, but it
contradicts the non-negotiable epistemic-separation principle: shared
conclusions must remain traceable, and reviewer outputs are evidence
to examine, not authority. A judge-owned requirement model was
rejected because scoping-by-integrator lets coverage obligations be
redefined to fit available evidence; scoping belongs before and
outside judgment.

## Evidence

- `docs/assurance/architecture.md`: fan-out diagram, independence
  ledger, two-pass protocol (independent first pass, challenge pass
  with provenance, both versions preserved); cross-reviewer claims
  remain cited claims, not raw observations.
- `docs/assurance/epistemic-boundaries.md`: observation/inference/
  judgment separation for every specialist finding.
- `docs/assurance/escalation-policy.md`: risk class and coverage set
  before assessment; scope owner recorded; low risk never inferred
  from diff size.
- `docs/assurance/evidence-model.md`: criteria and rubrics versioned;
  criterion changes invalidate dependent claims until reassessed.
- Local validated precedent: blind-review runs keep reviewers
  isolated per case with frozen keys (`evals/runs/*/RUN.md`).

## Tradeoffs

Fan-out costs parallel context and a separate challenge pass, and it
defers contradiction-handling to the integrator instead of resolving
it inline. In exchange, first-pass verdicts are uncontaminated and
revisions are attributable to new evidence vs changed argument.
Evidence-layer-owned scoping adds an explicit pre-review step, but it
makes coverage obligations auditable before any judgment exists.

## Source IDs

LOCAL-code-reviewer (blindness/isolation practice) and the verified
claim subsets of S11–S13 (nonvoting integration, defeaters, residual
doubt), per traceability.yaml. No new source required.

## Confidence and uncertainty

High confidence that fan-out preserves verdict independence better
than a cascade; the mechanism is structural, not empirical. Whether
the two-pass protocol catches real contradictions at acceptable cost
is unmeasured (validation plan RQ7/RQ8). REQUIREMENT MODEL ownership
by the evidence layer is a design assignment; its adequacy depends on
the gate-1 adapters, which do not exist yet.

## Reversal conditions

Revisit if comparative evaluation shows the challenge pass adds no
defeaters over a cascade at equal cost, if scoping-before-evidence
proves unworkable (e.g. risk class unknowable without specialist
input — then allow a scoped preliminary pass with explicit
provisional status), or if concrete counterexamples show the
fan-out/checker semantics accepting what the cascade would catch.
Record revisions with migration rules; never silently reinterpret
existing assurance records.
