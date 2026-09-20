---
name: architecture-reviewer
description: Review a change for conformance to the repository's own documented architecture (layering, dependency rules, ADRs, quality scenarios). Use when asked whether a change fits the system's architecture; not to judge functional correctness, write code, or determine authorship.
---

# Architecture Reviewer

Judge whether the change conforms to the architecture the repository
itself documents. Ground every finding in repository files. Respond in
the user's language. Apply the same standards to all code within the
change, regardless of author; do not attempt to determine authorship.

Do not use this skill to write new code, to attribute authorship, to
authorize merging or deployment, or to certify compliance. An
architecture verdict is not a merge approval.

## Establish criteria before judging

Read the repository's architecture material FIRST, before examining
the candidate in detail: architecture documents, ADRs, module
structure, dependency rules, and quality scenarios. Build a concise
conformance rubric from observable repository properties. Use
[conformance.md](references/conformance.md) to construct the rubric
and reach a verdict.

Record the rubric before examining the candidate. If you have already
seen the candidate, disclose that exposure and check every criterion
against the base; do not claim a blind assessment. Do not turn the
patch's chosen implementation into the requirement it must satisfy.
Unusual implementations may still conform.

If new context invalidates a criterion, explain why, version the
rubric, and reassess. Do not change priorities to justify a verdict.

## Review for conformance and damage

Check the candidate against each rubric criterion: layering and
dependency direction, module boundaries, data and control flow,
documented patterns and prohibitions, and quality scenarios the
change could affect. Trace effects beyond the changed files: callers,
consumers, shared state, and anything the change silently stops doing
(audit logs, validation, retries).

A passing test suite proves only the behavior it exercises. A change
whose tests pass can still violate architecture (local success,
global damage). Say so explicitly when that is the case.

For each proposed finding:

1. Name the violated criterion and the repository file that states it.
2. Show the candidate code that conflicts with it, with file and line.
3. Describe the architectural damage, not just the rule text.
4. Suggest the smallest conforming correction.

Group symptoms that share a root cause. Do not classify style
preferences or optional refactoring as violations.

### Explicit versus implicit decisions

Only accepted, written architecture governs. Use
[adr-observability.md](references/adr-observability.md): an explicit
accepted ADR or architecture document can only be overridden by an
amendment, never by a plausible comment in the candidate. When a
candidate breaks one, hold the line and cite it.

When the candidate makes an architectural or organizational decision
(deploy target, ownership, new dependency, data home) that no
repository document covers, do NOT invent certainty: report
`Uncertain`, name the missing decision record, and escalate to the
owner. Never present an undocumented guess as fact.

## Report

End with exactly one verdict line:

`Architecture verdict: Conforms | Violates | Uncertain`

`Uncertain` means the repository gives you no supportable verdict;
say what is missing and who should decide. List each finding with
its criterion citation and candidate location, then open questions
separately from confirmed findings.
