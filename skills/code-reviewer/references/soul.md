# Soul Verification

Soul verification checks whether a change preserves the repository's
documented essence: the principles that define what the project IS. It is distinct from architecture (how the project is
built) and function (what the change does). A change can be correct and
well-structured while betraying the project's soul.

## Derive the Essence

Collect essence statements only from sources the repository or user
provides: a philosophy or manifesto file, canon documents, ADRs, or
principles declared in the README. Keep at most seven statements, each
with a quoted source. An essence statement describes identity or a
non-negotiable, not a mechanism: "memory-only, never touches the
filesystem" qualifies; "must use library X" does not.

If no essence is documented, return `Unverifiable` and continue the
review without it. You may ask the user to articulate one. Never invent
essence statements.

## Assess the Candidate

For each statement, determine whether the candidate preserves, tensions,
or betrays it, citing candidate evidence:

- `Preserved`: the change honors the statement.
- `Tense`: the change strains the statement. A documented tradeoff is recorded as-is; an undocumented one additionally becomes a finding or open question.
- `Betrayed`: the change contradicts the statement.

| Soul verdict | Rule |
| --- | --- |
| `Preserved` | No tensions or betrayals. |
| `Tense` | Strained statements, no betrayal. |
| `Betrayed` | At least one betrayal with evidence. |
| `Unverifiable` | No documented essence to assess against. |

A betrayal becomes a finding with priority by impact (typically P1); a
tension becomes a P3 or an open question. The soul verdict never
overrides the architectural verdict; report both.

## Evolution

Essence can change deliberately. Assess a change that updates the
essence documents themselves against its stated objective, not against
the statements it replaces. Version the statements and reassess
affected candidates, as with the architectural rubric.
