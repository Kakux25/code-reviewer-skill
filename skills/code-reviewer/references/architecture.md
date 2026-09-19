# Architectural Rubric and Assessment

## Build the Rubric from the Base Revision

Classify the primary purpose: bug fix, feature addition, refactoring, or architectural change. Assess a deliberate architectural change against the agreed objective and its transition requirements; do not require preserving what the change is intended to replace.

Derive criteria from the repository rather than a preferred architecture. For each axis, record an identifier, property, priority, rationale, evidence from the base revision, and two anchors: what would preserve the property and what would violate it. For example, “readers never observe partially updated state” allows different solutions; “must call function X” may impose an unnecessary mechanism.

A primary criterion protects a property essential to this change; a secondary criterion affects consistency or maintainability; a minor criterion addresses local details. Use only sufficiently supported patterns. Do not invent confidence percentages. If documentation and code conflict, explain the discrepancy and avoid presenting the convention as established fact.

With sufficient context, there must be at least one defensible primary axis. If you cannot establish one, return `Insufficient evidence` rather than inventing it. Freeze the axes before assessing the candidate.

## Evaluation

For each axis, describe the result using evidence from the base revision and the candidate. For primary axes, trace effects beyond the modified files and identify affected consumers or subsystems. Check that multiple axes do not penalize the same cause twice.

List `gaps`: concrete deviations from the anchors, with the relevant axis, impact, and evidence. A different mechanism that preserves the property is not itself a gap. Do not invent gaps to avoid a favorable result.

| Architectural verdict | Rule |
| --- | --- |
| `High` | No primary-axis violations or identified gaps. |
| `High with concerns` | No primary-axis violations; minor deviations are documented. |
| `Acceptable` | A primary-axis deviation is contained or represents a justified tradeoff, without a fundamental structural break. |
| `Low` | A significant primary-axis violation, improper boundary crossing, or fundamental pattern bypass is present. |

Secondary and minor axes contribute gaps and nuance; they do not independently lower the verdict to `Acceptable` or `Low`. A functional or security issue on a secondary axis can separately prevent overall acceptance. Gaps must also capture the deviations that justify `Acceptable` and `Low`.

Use `Insufficient evidence` when the available context cannot support an architectural verdict. Do not turn a lack of evidence into `High`. Avoid aggregate scores, averages, and “quality” percentages.

## Practical Limits

Exclude supporting files from the architectural verdict only when they are demonstrably unrelated to production. Do not classify them by name or location: a script in the repository root may run in CI or production. Still review their potential functional and security effects.

When comparing candidates, use the same base revision, scope, and rubric, hiding the author or model where possible. Allow ties and document limitations. Do not claim a blind, independent evaluation if you already know who produced the candidate.

Complexity guides the effort; it does not determine which code deserves review.
