# RUN: judge-demo (judge envelope + full loop)

Date: 2026-09-20. Tool: `scripts/judge_envelope.py` (run
`judge-demo`). The 7th module, `final-engineering-judge`, renders
an independent verdict (concur/dissent/abstain) with written
reasons on an assembled case, per `docs/assurance/judge-protocol.md`
(written BEFORE the verdicts below). Inputs in `inputs/`
(integrator-demo artifacts, copied frozen, plus ok3/ok4 with
independent digests and their accept2 assembly); verdicts in
`verdicts/`; fragments in `fragments/`; full loop in
`final-loop.json`.

## Verdicts (human judge, K=1, protocol-bound)

| verdict | assembly judged | norm findings |
|---------|-----------------|---------------|
| concur-defeated | defeated.json (INSUFFICIENT, defeated STPA claim) | N1 re-derivation agrees; N2 n/a (refusal); N3/N4 hold |
| concur-refusal | real-refusal.json (cross-context refusal) | N1: refusal the only sound move; N2 n/a; N3/N4 hold |
| dissent-accept | accept.json (ACCEPT, 0 defeaters) | N1 holds (mechanics correct); **N2 violated**: E-ASM records 2 items deduped to 1 unique digest — no independent corroboration; repair prescribed (accept2 demonstrates it) |
| concur-accept2 | accept2.json (ACCEPT, independent evidence) | N1 holds; N2 holds (`ff2f2ce7f957…` vs `d8d60e8d3ecc…`, 2→2); N3/N4 hold |

The dissent is the point: structure said ACCEPT and was
mechanically right, but the judge's independence norm caught
corroboration collapse the checks cannot see. Norms overrule
mechanics, with reasons and a repair — not vibes.

## Full loop

`final-loop.json` = assemble(ok3, ok4, concur-accept2-fragment)
with required = code + arch + judge: INSUFFICIENT_EVIDENCE with
exactly ONE defeater — the judge's own K=1 assumption. Coverage,
agreement, support, independence: all clean. The loop lands one
named assumption from ACCEPT, and the defeater names precisely
what is missing (second judge / verified faithfulness).
Assembling (ok1, ok2, dissent-accept) instead yields
INSUFFICIENT with defeated C7 (pinned by test, not frozen).

## Post-review fixes (chain validation, P3-only)

- Docstring usage corrected to JSON `--verdict`
  `'{"verdict": "concur"}'` (bare word crashes json.loads).
- `rubric_version` now hashes the protocol (was: assembly bytes),
  matching `criteria=["judge-protocol.md"]`; fragments regenerated.
- Empty verdict records raise ValueError (protocol R5: reasons
  mandatory), pinned by `test_empty_verdict_raises`.
- concur-refusal cites literal `fixture:*-a` ids from the record
  (was: paraphrased context names).
- Protocol committed separately BEFORE this run's artifacts, so
  "protocol-first" is repository-evidenced, not asserted.

## Honest ceilings (not bugs)

- No full ACCEPT exists in this repo: every human-grade claim
  (C1-C7) carries its K=1 assumption, which the contract counts
  as unclosed. ACCEPT stays reachable only for assumption-free
  (synthetic/mechanical) assemblies. The pipeline surfaces the
  gap instead of waiving it.
- The judge is K=1 (this session's human operator). U7 records
  the missing second verdict. Abstain is unit-tested, not
  demonstrated live (no unreadable assembly at hand; documented
  rather than staged).
