## Sociotechnical review: CHG-104 (soc-d)

Scope: change CHG-104 modifies `legacy/cron.py` (schedule `0 2 * * *` to `0 * * * *`). Base: `tests/socio-cases/soc-d/repo/`. Candidate: `tests/socio-cases/soc-d/candidate/`.

Exposure note: the candidate file was viewed during this review; the required-coordination map below was checked against the base `repo/` directory listing, not the candidate.

### Required coordination map (from repo records FIRST)

Searched in `tests/socio-cases/soc-d/repo/` for:

- Ownership maps: `CODEOWNERS`, `OWNERS` — not found. Directory contains only `legacy_cron.py`.
- Team rosters with freshness dates: `TEAMS.md` or equivalent — not found in the same directory.
- Handoff/ack logs: `handoffs.md` or equivalent — not found in the same directory.

No record of a required owner for `legacy/cron.py` was found in the searched places listed above.

Coordination map:

- `legacy/cron.py -> required owner: unmappable (no ownership map in tests/socio-cases/soc-d/repo/) | observed: uncheckable (no handoff log in tests/socio-cases/soc-d/repo/ searched for CHG-104)`

The `repo/legacy_cron.py:1` docstring text "(no ownership records)" is a file comment, not an ownership, roster, or handoff record, and was not counted as one.

### Observed coordination for CHG-104

No record of an ack for CHG-104 was found in the searched places listed above, because no handoff log exists there to search.

No candidate comment about people or teams was found in `tests/socio-cases/soc-d/candidate/legacy_cron.py` to quote or refuse.

No stale-mapping assessment was possible: no ownership map or roster exists to compare dates or team status against.

### Open questions

- Who should own `legacy/cron.py`? No record names an owner; this needs assignment before coordination can be judged.
- Where should the ownership map, roster, and handoff log for this path live? None exist under `tests/socio-cases/soc-d/repo/`.
- Escalate CHG-104 to whoever should own `legacy/cron.py` for an ownership decision and, after mapping, a recorded ack.

Coordination verdict: Unknown
