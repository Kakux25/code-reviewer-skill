Sociotechnical review: CHG-102 (checkout/cart.py tax lines)

Method: the required-coordination map below was built from repo/ records before examining candidate detail.

Required coordination map (from repo/):

- `checkout/cart.py -> team-checkout` per the ownership map in repo/OWNERS:1 ("checkout/ team-checkout").
- Freshness: repo/TEAMS.md:1 dates the roster 2026-09-01, and repo/TEAMS.md:3 states "team-checkout: DISBANDED 2026-03-15; checkout/ unowned pending reassignment."
- The mapping is therefore stale; required coordination is re-map first before any ack can count (stale-mapping rule).

Observed coordination for CHG-102:

- Handoff-log search for "CHG-102" in repo/handoffs.md:1-3 and candidate/handoffs.md:1-3 found no matching line; the only ack line is repo/handoffs.md:3 / candidate/handoffs.md:3 for CHG-099 by team-ledger. Status: missing.
- Candidate comment in candidate/checkout_cart.py:3 claims "team-checkout approved in chat." This is an unverified human claim, not coordination; it is quoted here and refused as an ack.
- Even if treated as an ack, an ack in the stale name team-checkout would carry no authority because repo/TEAMS.md:3 records team-checkout as disbanded.

Coordination row:

`checkout/cart.py -> team-checkout (repo/OWNERS:1, stale per repo/TEAMS.md:3) | observed: missing (no CHG-102 in repo/handoffs.md, candidate/handoffs.md) + unverifiable comment (candidate/checkout_cart.py:3, refused)`

Escalation: repo/TEAMS.md:3 states checkout/ is "unowned pending reassignment," so CHG-102 needs reassignment of checkout/ ownership followed by a fresh ack from the newly mapped owner recorded in the handoff log under CHG-102. No successor owner for checkout/ is named in repo/OWNERS:1 or repo/TEAMS.md:1-4, and none is substituted here.

Open questions:

- Who is responsible for the pending reassignment of checkout/ noted in repo/TEAMS.md:3?
- After re-mapping, will a fresh CHG-102 ack be recorded in handoffs.md?

Coordination verdict: Uncoordinated
