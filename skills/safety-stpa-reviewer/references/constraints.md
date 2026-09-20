# Constraint enforcement status

Every safety constraint the candidate touches gets one status.
Status is about the CANDIDATE, evidenced in the candidate, not
about the documents.

## Statuses

- **Enforced**: the candidate upholds the constraint by a mechanism
  you can point to: a guard, interlock, assertion, monitor, or test
  that fails if the constraint breaks. Cite the mechanism.
- **Unverified**: the constraint is stated in documents (or in
  candidate comments) but no candidate mechanism upholds it. Say
  what would enforce it.
- **Broken**: the candidate violates the constraint. Cite the
  violating code and the hazard path.

## Rules

- A refactor preserves enforcement only if every guard still
  triggers under the same conditions; check each condition, do not
  eyeball equivalence.
- A passing functional test enforces a constraint only if the test
  exercises the constraint boundary. Tests that pass away from the
  boundary prove nothing about it.
- Never report Unverified as Enforced. When in doubt, downgrade and
  say why.
