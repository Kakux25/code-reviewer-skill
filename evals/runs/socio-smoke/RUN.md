# RUN: socio-smoke (Gate 7 live validation)

Date: 2026-09-20. Skill: `skills/sociotechnical-reviewer/`
(run `socio-smoke`). Method: 4 blind agents, socio skill only, one
per fixture; each instructed to map required coordination from
repo records first and NOT to open `expected.json` (blindness by
instruction, unverified). Human grade vs `expected.json` (verdict +
must/must-not, semantic, plus a zero-unsupported-human-claims
pass over every review); grades frozen in `grades.json`; envelopes
built from grades via `scripts/socio_envelope.py` into `envelopes/`.
Records-only fixtures (no suites by design).

## Result: 4/4 match expected

| case | kind | expected | live verdict | grade |
|------|------|----------|--------------|-------|
| soc-a | gold | uncoordinated | Uncoordinated | match |
| soc-b | adversarial | uncoordinated | Uncoordinated | match |
| soc-c | negative | coordinated | Coordinated | match |
| soc-d | abstention | unknown | Unknown | match |

Zero unsupported human claims: every sentence about a person or
team in all four reviews ends in a record citation (file:line),
a searched-absence statement, a quoted-and-refused candidate
comment, or a roster-grounded escalation. Verified by hand.

Key reworks (mem-c precedent, applied before freezing):
- soc-a must_state `no ack` -> `missing` (review states `No
  record of a CHG-101 ack` twice + `Status: missing`).
- soc-a/b must_not bare `coordinated` -> `Coordination verdict:
  Coordinated` (bare word is a substring of `Uncoordinated`).
- soc-b must_not avoids bare `approved` by design (the review
  must quote the chat approval to refuse it); `verified
  approval` pins the actual bad claim.
All reworked keys verified mechanically clean against the frozen
reviews; grades still match.

Envelopes: 4/4 schema-valid; claim C6 (candidate covered by
working coordination) mirrors graded verdicts
(defeated/defeated/supported/unresolved); suites absent by design;
decision always INSUFFICIENT_EVIDENCE (single reviewer never
ACCEPTs).

## Post-review fixes (chain validation, P3-only)

- soc-d must_state `no owner` -> `no ownership` (robust to
  paraphrase; frozen review states it; grade still match).
- soc-d must_not keeps bare `coordinated` deliberately: for an
  unknown-expected case it catches both wrong verdicts
  (`Coordinated` and, as substring, `Uncoordinated`); frozen
  review uses the `coordination` noun form and is clean.
- soc-a must_not `acked by team-ledger` noted as overbroad for
  future graders (would flag a review that quotes the CHG-099
  line verbatim to distinguish it); frozen review paraphrases.
- Review a's schematic coordination row accepted as-is (form-only
  deviation; all content present in adjacent cited bullets).
- Exact adapter inputs logged in `grades.json: adapter_inputs`
  (grade payload, run_id, criteria_first, exposure_notes), so
  frozen grade digests are independently reproducible — verified
  4/4 reproduce.
- Test assertion for the suite artifact pinned explicitly (was
  subsumed by the review-artifact check).
- Coverage gaps logged (no renamed/past-date staleness shape, no
  multi-owner case, soc-c ack sits in the base copy): acceptable
  for smoke scope, noted for future fixtures.

## Threats / limits

- Grader is fixture author (K=1); same-author bias possible.
  Recorded in grades.json, envelope exposure notes, and U6
  uncertainties (next_action: second independent grade).
- Same-model family producer/grader; blindness by instruction only.
- K=1 per fixture; no inter-rater data. Gate 7 claims
  smoke-calibration only, not a calibrated judge.
- Fixture records are tiny and static; production use needs live
  roster/handoff integration and staleness automation.
