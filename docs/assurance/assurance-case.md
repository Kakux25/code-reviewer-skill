# Assurance Case

The top claim is: change `<candidate>` is acceptable for `<integration|deployment>` in `<context>` under the stated assumptions. Behavioral, architectural, dynamic, safety, incident-applicability, coordination and coverage subclaims are distinct. An inapplicable concern needs evidence and a rationale; it is not a favorable vote.

Every claim has a statement, scope, assumptions, warrant, supporting evidence, counterevidence, defeaters, dependencies, independence notes, residual doubts and a status: supported, defeated, unresolved or not_assessed. Dependencies form an acyclic argument graph, not a confidence average. The top claim's support must explain how its subclaims jointly cover the scoped obligations.

For each significant positive claim, formulate an investigable defeater and a disconfirmation action. Defeaters are unresolved, sustained, refuted or partially_mitigated. Refuting one does not prove the entire parent claim. A sustained blocking defeater prevents acceptance; missing decisive evidence prevents a favorable conclusion. Unresolved nonblocking concerns require an explicit scope-based rationale.

## Recommendations

- `ACCEPT`: applicable obligations are supported, required reviews are complete, blocking doubts/defeaters/findings are closed, evidence provenance is adequate, and the argument explains coverage and dependence.
- `CONDITIONAL_ACCEPT`: the same acceptance prerequisites hold, with explicit prospective operational conditions. Conditions never excuse missing decisive evidence. No deployment occurs until conditions are independently verified by the authorized owner.
- `ESCALATE`: credible risk, conflicting evidence, safety significance or unclear authority requires a responsible person or specialist.
- `REJECT`: a substantiated unacceptable consequence or violated requirement defeats the scoped proposal.
- `INSUFFICIENT_EVIDENCE`: the available material cannot justify the requested conclusion; list the needed evidence and owner.

The result is a recommendation. Integration/deployment authorization is a separate human or organizational control outside this schema validator. The integrator must not bypass it, re-review all code, overwrite specialists, or convert model agreement into evidence independence.

The example decision record is deliberately insufficient; it is not a simulated successful deployment approval. Numerical assurance confidence is deferred until dependence, logical structure and calibration are supported.
