# Judge verdict: concur-accept2 (inputs/accept2.json)

Assembly: `AC-ASM-demo2`, decision ACCEPT, 0 defeaters. Structural
re-derivation per N1: coverage holds (code-reviewer +
architecture-reviewer complete), scopes agree
(demo-base@2/demo-cand@2), both subclaims supported and closed,
evidence verified, no blocking doubts, no confirmed findings.
ACCEPT follows from the checks.

- N1 structural soundness: HOLDS (re-derivation agrees).
- N2 evidence independence: HOLDS. Subclaim `C-ok3` is supported
  by `E-ok3` (digest `ff2f2ce7f957…`) and subclaim `C-ok4` by
  `E-ok4` (digest `d8d60e8d3ecc…`): two distinct digests, no
  dedupe collapse (integration record confirms 2 items -> 2
  unique). Corroboration is real.
- N3 coverage honesty: HOLDS (both reviewers complete, in-scope
  for demo-chg-2).
- N4 no laundering: HOLDS (synthetic assumption-free claims;
  nothing upgraded).

Verdict: concur
