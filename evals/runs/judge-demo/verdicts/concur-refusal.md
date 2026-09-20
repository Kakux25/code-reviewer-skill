# Judge verdict: concur-refusal (inputs/real-refusal.json)

Assembly: `AC-ASM-demo`, decision INSUFFICIENT_EVIDENCE, 1 defeater
(scope mismatch across five fixture contexts). Re-derived per N1:
the five input fragments span `fixture:arch-a`, `fixture:dyn-a`,
`fixture:mem-a`, `fixture:soc-a`, `fixture:stpa-a`
(`real-refusal.json:4`) — five different changes. Merging them
would fabricate cross-change assurance. The refusal case correctly
carries no fragment items (claims=[CTOP], reviews=[]), so no scope
rule is violated. INSUFFICIENT_EVIDENCE follows.

- N1 structural soundness: HOLDS (refusal is the only sound move).
- N2 evidence independence: NOT APPLICABLE (refusal, not ACCEPT).
- N3 coverage honesty: HOLDS (no coverage claimed; the defeater
  names the mismatch rather than pretending completeness).
- N4 no laundering: HOLDS (K=1 assumptions of the input fragments
  are not inherited — nothing is inherited).

Verdict: concur
