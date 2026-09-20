Required coordination map (built from `repo/` records before examining candidate detail):

- Touched path `search/index.py` falls under `search/`. Record `repo/CODEOWNERS` (line 1) states `search/` is owned by `@team-search`.
- Record `repo/TEAMS.md` (lines 1, 3) states `team-search` owns `search/` and is active, roster updated 2026-09-01. The mapping is fresh: the cited roster lines show no disbanded, renamed, or past-review signal for `team-search`.

Observed coordination for CHG-103:

- Record `repo/handoffs.md` (line 4) states `CHG-103 (search/)` was acked by `team-search (R. Alvarez)` on 2026-09-18. Record `candidate/handoffs.md` (line 4) carries the same entry. Searched the handoff log for change id CHG-103 plus owning team `team-search` (cited records above); found at the cited lines.
- The acking team matches the fresh-mapped owner from the cited records, so no re-mapping is required before the ack counts.
- No candidate comments about people were found in `candidate/search_index.py` (lines 1-3 contain only tokenizer code); there are no unverified human claims to quote and refuse.

Coordination map:

`search/index.py -> team-search (repo/CODEOWNERS:1, fresh per repo/TEAMS.md:1,3) | observed: acked (repo/handoffs.md:4; candidate/handoffs.md:4)`

Open questions: none.

Coordination verdict: Coordinated
