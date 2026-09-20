# Evidence Model

The versioned [JSON Schema](../../schemas/v0.1.0/assurance.schema.json) defines Evidence, Claim, Finding, Defeater, Uncertainty, IncidentCase, CausalLink, SafetyConstraint, AssuranceCase and ReviewEnvelope. The bundle is an AssuranceCase; named definitions can also validate individual records.

## Meaning and provenance

An Evidence record identifies an inspectable artifact, collection method, revision/context, integrity state and limitations. Static, dynamic, formal, historical, organizational and inferential records are distinguished. `inferential` is never sufficient by itself to confirm a defect. Execution receipts describe a command and result; an LLM's account of execution is not a receipt.

A Claim is a proposition with an explicit warrant connecting supporting observations to criteria. Counterevidence and defeaters are stored separately from supporting evidence. Findings express candidate defects and their status; rejected and uncertain candidates remain available for auditing false positives. An Uncertainty names the missing fact, consequence, owner and next verification action.

CausalLink records preserve status `observed`, `modeled` or `hypothesized`, evidence, polarity, delay and confidence basis. Observed temporal association does not itself establish causal identification. IncidentCase records carry both applicability and non-applicability conditions; neither an embedding score nor a matching label closes applicability. SafetyConstraint links explicit losses, hazards, actions and scenarios to a testable restriction, with enforcement and verification status distinguished.

## Lifecycle

Evidence IDs refer to immutable observations; changed artifact bytes require a new record. Claims and rubrics are versioned. A change to candidate revision, context, criterion, source record or warrant invalidates affected dependent claims until reassessed. Historical evidence may originate at another revision, but requires an explicit applicability rationale. Unknown integrity or stale context must remain visible.

Referential integrity, scope equality, claim-cycle detection and conservative acceptance eligibility are deterministic checks. Record identifiers are globally unique across evidence, claims, findings, defeaters, uncertainties, and reviews (one shared namespace, enforced by the checker), so a reference resolves without consulting its group. They cannot verify whether cited files exist in production, whether a quoted result is authentic, whether an inference is valid, or whether a human authorization is genuine. External artifact integrity and source authentication belong to future evidence adapters.

## Data handling

Store minimum necessary excerpts; never store credentials or personal speculation. Organizational and incident records require explicit retention permission and access controls. Record retention scope, provenance and deletion requirements before enabling persistent memory. This release provides synthetic examples, not a production incident database.

## Validator scope

The checker validates required fields, selected cross-record references, scope equality, claim cycles, finding refutation requirements and conservative acceptance exclusions. It does not implement a complete assurance logic. Acceptance checks are necessary conditions only: they do not establish argument completeness, relevance of every citation, independent evidence, model calibration or verified operational conditions. This version rejects acceptance while any claim carries assumptions or residual-doubt references; richer discharge semantics require a later version.
