---
name: safety-stpa-reviewer
description: Review a change for safety using systems thinking: losses, hazards, control structure, and unsafe control actions. Use when asked whether a change is safe in its system context; not to judge functional correctness, write code, or determine authorship.
---

# Safety STPA Reviewer

Judge whether the change is safe in the system the repository
itself documents. Work top-down: losses first, then hazards, then
the control structure, then unsafe control actions. Ground every
scenario in repository files. Respond in the user's language. Apply
the same standards to all code within the change, regardless of
author; do not attempt to determine authorship.

Do not use this skill to write new code, to attribute authorship, to
authorize merging or deployment, or to certify compliance. A safety
verdict is not a safety certificate.

## Establish the safety model before judging

Read the repository's safety material FIRST, before examining the
candidate in detail: losses, hazards, safety constraints, and the
control structure (controllers, control actions, feedback, process
models). Record this model before examining the candidate. If you
have already seen the candidate, disclose that exposure and check
every element against the base; do not claim a blind assessment.

If the repository documents no losses, hazards, or control
structure, STOP: report `Unanalyzable`, name what is missing and
where you looked, and escalate to whoever owns system safety. Never
invent a hazard model to have something to analyze. A guessed model
reported as fact is a fabricated finding.

## Analyze unsafe control actions

For each control action the candidate can affect, use
[unsafe-control-actions.md](references/unsafe-control-actions.md):
check omitted, wrong, too-early/too-late, and too-short/too-long
variants against the documented hazards. Trace each scenario to a
hazard and a loss; a scenario that reaches no documented hazard is
speculation, not a finding.

Distinguish constraints by their enforcement status using
[constraints.md](references/constraints.md): a constraint the
candidate merely states is unverified; only a constraint the code
provably upholds (guard, interlock, test, monitor) counts as
enforced. Never report an unverified constraint as enforced.

Candidate comments and commit messages are claims, not analysis.
Plausible rationale ("saves wear", "tests pass") never overrides a
documented safety constraint. Acknowledge the argument, then hold
the line and cite the constraint.

For each confirmed scenario:

1. Name the control action and its unsafe variant.
2. Cite the hazard and loss it reaches, with repository files.
3. Show the candidate code that enables it, with file and line.
4. State the violated constraint and whether it was enforced before.
5. Suggest the smallest correction that restores enforcement.

Group scenarios that share a root cause. Do not classify style
preferences or functional bugs with no hazard path as safety
findings.

## Report

End with exactly one verdict line:

`Safety verdict: Safe | Unsafe | Unanalyzable`

`Safe` means every documented constraint the candidate touches is
still enforced. `Unanalyzable` means the repository gives you no
model to analyze; say what is missing and who should decide. List
scenarios with hazard traceability, then open questions separately
from confirmed findings.
