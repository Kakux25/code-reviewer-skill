Review: CHG-101 — payments/processor.py fee rounding

Change:
- `fee(cents)`: `cents // 100` → `(cents + 50) // 100`
- Behavior: floor → half-up rounding. Affects all payments fee calculations.

Ownership (required coordination):
- `CODEOWNERS`: `payments/ @team-ledger`
- `TEAMS.md` (2026-09-01): team-ledger owns payments/, active.
- So CHG-101 requires team-ledger coordination.

Actual coordination for CHG-101:
- `handoffs.md` lists only:
  - CHG-098 (search/): acked by team-search (R. Alvarez) 2026-09-10
  - CHG-099 (payments/): acked by team-ledger (M. Chen) 2026-09-12
- No entry for CHG-101; no ack from team-ledger recorded.

Finding: owning team is team-ledger per records, but no handoff/ack record exists for CHG-101.

Verdict: Uncoordinated
