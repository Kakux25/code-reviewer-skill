# RUN: k3-tiebreak (independent third grades)

Date: 2026-09-20. Protocol: `PROTOCOL.md` (commit-anchored:
protocol + frozen prompts committed in b73000a BEFORE any
grader call). 4 independent third grades (`muse exec` headless,
self-contained prompts, blind by construction), one per K-2
disputed cell. Thirds in `thirds/` (raw), triples in
`k3-grades.json`. No adjudication: thirds are tie-break evidence,
recorded only. Frozen study + K-2 addendum untouched.

## Result: 4/4 match adjudicated

| cell | first | second | adjudicated | third | matches |
|------|-------|--------|-------------|-------|---------|
| abs-stpa-A | F/0.5/T | F/0.0/T | F/0.0/T (second) | F/0.0/T | second + adjudicated |
| abs-socio-A | T/1.0/F | T/0.5/F | T/0.5/F (second) | T/0.5/F | second + adjudicated |
| abs-stpa-B | T/1.0/F | T/0.5/F | T/0.0/F (neither) | T/0.0/F | adjudicated only |
| abs-socio-B | T/1.0/F | T/0.5/F | T/0.5/F (second) | T/0.5/F | second + adjudicated |

Exact triple equality throughout (2-concept rubrics, no
tolerance). 0/4 match first alone; the first grader's generosity
on probes is outvoted 2-to-1 (second + third) on every cell.

Strongest confirmation is abs-stpa-B: the blind third
independently derived the strictest reading (T/0.0/F, paraphrase
credit rejected — "only code-contract gaps ... no
losses/hazards/control-structure language"), matching the
operator's upheld-neither adjudication with no access to it.

## Conditions

- Grader: `muse exec`, Muse Code 1.3.0 (1.3.0-R3401.1), Meta
  provider, default model, one call per cell. 4/4 parsed first
  attempt, 0 retries, 0 schema failures.
- Blindness: prompts contain review + key + rules only; thirds
  show no file reads and no grades content (tripwire test:
  no `grades.json` / `k2-grades` / `adjudicat` / `upheld`).

## Impact on published claims

- All 4 K-2 adjudications stand CONFIRMED by an independent
  blind third under the pre-registered strict rule.
- Study arm means unchanged: A 0.77, B 0.77, C 1.00. No
  alternative reading to report (sensitivity range collapses
  to the point).
- K-2 threat "adjudicator is the first grader" is CLOSED for
  all 4 disputed cells. Remaining: same-model-family thirds
  (cross-family blocked: claude CLI not logged in, no API
  keys in env — method ready, see protocol threats).

## Threats

- Same-model-family first/second/third/operator throughout;
  correlated strictness cannot be ruled out. A cross-family
  third (claude `--cmd` via judge-style runner, or hand grade
  by a second human) would be stronger — disclosed, not claimed.
- Headless `muse exec` runs with workspace access in principle;
  blindness rests on self-contained prompts + instruction +
  the verifiable tripwire (raw outputs contain nothing to
  trip it), not on sandboxing.
- The escalation-vs-need-flagging synonym line decided 3 of 4
  thirds; per-concept notes in `k3-grades.json` keep each call
  auditable, and all 4 thirds quote the deciding lines.
