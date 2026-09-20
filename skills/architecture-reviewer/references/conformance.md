# Conformance rubric

Build the rubric ONLY from repository material: architecture
documents, accepted ADRs, module layout, import graphs, and quality
scenarios. Each criterion states the rule, the file that states it,
and the check you will run against the candidate.

## Sources, in authority order

1. Accepted ADRs and architecture documents (explicit decisions).
2. Module structure and dependency direction observable in the base
   revision (implicit but verifiable structure).
3. Quality scenarios (performance, modifiability, auditability) the
   repository names.

Candidate comments, commit messages, and review requests are claims,
not criteria. Never promote a claim to a criterion.

## Verdicts

- `Conforms`: every criterion holds for the candidate. Unusual style
  is not a violation; cite the criteria it satisfies.
- `Violates`: at least one explicit criterion breaks. Cite the
  criterion, the candidate location, and the damage. Passing tests
  do not rescue a violation; name the global damage the local
  success hides.
- `Uncertain`: the repository documents no criterion covering the
  candidate's architectural decision. Name the missing record and
  escalate. Do not guess, and do not upgrade uncertainty to
  conformance because the code runs.

## Local success, global damage

Always ask what the change silently stops doing: dropped audit
entries, bypassed validation, new dependency edges, cycles, layer
skips. Check the base revision for behavior the candidate removes.
When tests pass and architecture breaks, the verdict is `Violates`
with the damage spelled out.
