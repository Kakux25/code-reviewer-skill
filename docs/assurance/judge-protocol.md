# Final-engineering-judge protocol

Date: 2026-09-20. The judge renders an independent verdict on an
assembled assurance case. Structural checks are the integrator's
job; the judge adds substantive judgment the structure cannot see.
Every verdict ships written reasons; a verdict without reasons is
not a verdict.

## Procedure

1. Read the assembly: decision, claims, evidence, defeaters,
   uncertainties, reviews. Re-derive the decision from the parts;
   if the decision does not follow, dissent (structural ground).
2. Apply the norms below. Any violated norm blocks concurrence.
3. Write the verdict record: verdict (concur/dissent/abstain),
   norm-by-norm findings with file/claim/evidence citations, and
   the smallest repair that would change a dissent.
4. Convert to a fragment via `scripts/judge_envelope.py`. The
   fragment carries the assembly's scope so it merges back.

## Norms

- N1 structural soundness: the decision follows from the
  integrator's checks (coverage, agreement, closure, no blocking
  doubts, no confirmed findings). Re-derive, do not trust.
- N2 evidence independence: an ACCEPT concurrence requires at
  least two subclaims supported by distinct evidence digests.
  Corroboration cannot come from one shared item counted twice —
  dedupe-by-digest makes sharing visible, and the judge enforces
  the consequence. A single shared item caps the verdict at
  dissent (assembly overstates its support), with the repair:
  add an independent evidence item.
- N3 coverage honesty: every required reviewer is complete and
  in-scope for the change; a complete-but-irrelevant review does
  not cover its module. Missing or out-of-scope coverage blocks
  concurrence.
- N4 no laundering: mechanical grades, lexical proxies, and K=1
  human grades are what they are. Concurrence never upgrades
  their stated limits; cite them as carried.

## Verdicts

- `concur`: N1-N4 hold (for the assembly's decision, ACCEPT or
  refusal alike — a correct refusal deserves concurrence).
- `dissent`: at least one norm fails; name it, cite it, prescribe
  the repair.
- `abstain`: the judge cannot evaluate (assembly unreadable,
  domain beyond competence, conflict). State why; never guess.
