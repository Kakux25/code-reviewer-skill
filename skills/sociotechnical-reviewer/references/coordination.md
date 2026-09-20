# Coordination map

For each path the change touches, one row:

`path -> required owner (mapping source, freshness) | observed: status (record)`

## Required side

- Owner comes from the ownership map covering the path
  (CODEOWNERS/OWNERS). Cite file and line.
- Freshness comes from the roster: team active + map date current.
  A map older than its review date, or naming a disbanded team, is
  stale — required coordination becomes "re-map first".

## Observed side

- `acked`: handoff log shows this change id + owning team + date.
  Cite the log line.
- `missing`: no such line. State the search (which log, which id).
- `unverifiable`: only a candidate comment or chat claim exists.
  Quote it, mark it, refuse it.

Verdict rule: Coordinated needs every row `acked` with fresh
mappings. One `missing` or `unverifiable` row = Uncoordinated.
No rows mappable = Unknown.
