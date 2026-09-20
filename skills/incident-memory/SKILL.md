---
name: incident-memory
description: Consult the repository's structured incident case base before judging a change: retrieve candidate precedents, decide transfer by mechanism, and apply lessons. Use when past incidents may bear on a change; not to write code or determine authorship.
---

# Incident Memory

Past incidents are evidence, not vibes. Retrieve candidate cases
from the structured case base, decide transfer by mechanism match
(not by ranking or keyword overlap), and apply the lesson of every
case that transfers. Respond in the user's language. Apply the same
standards to all code within the change, regardless of author; do
not attempt to determine authorship.

Do not use this skill to write new code, to attribute authorship, to
authorize merging or deployment, or to certify compliance.

## Retrieve first

Run the case-base retrieval (`scripts/incident_memory.py`) with
tags and text drawn from the CHANGE itself; author motivation in
the request is a claim, not a criterion — include it in the query,
but never let it decide transfer. Record the ranking before
judging. Retrieval proposes; you dispose: a top-ranked case whose
mechanism does not transfer must be explicitly rejected, never
followed.

If the ranking is empty, STOP: report `No match`, state that no
case ranked, and abstain. Never force an incident onto a change it
does not fit. A fabricated transfer is worse than no transfer.

## Decide transfer by mechanism

For each ranked case, use
[applicability.md](references/applicability.md): the case transfers
only if the change matches its `applies_when` AND matches none of
its `not_when`. Check the candidate code against both lists;
quote the lines that decide. Rank position, shared keywords, and
author motivation never transfer a case by themselves.

For each case, record one decision with its evidence:

- **Applied**: mechanism matches; state the lesson and what the
  candidate must change. The candidate is blocked until it does.
- **Rejected**: mechanism does not match; state which condition
  fails and why. A rejected case clears nothing else.
- **Satisfied**: mechanism matches but the candidate already
  upholds the lesson (`not_when` holds); cite the code that
  satisfies it. The candidate is clear on this case.

## Protect restricted fields

Cases carry `restricted` fields (costs, customers, hosts). Use
[redaction.md](references/redaction.md): never quote, paraphrase,
or hint at restricted content. Cite case id, title, mechanism, and
lesson only. If a lesson cannot be stated without restricted
content, say the case exists and escalate — do not leak it.

## Report

End with exactly one verdict line:

`Memory verdict: Blocked | Clear | No match`

`Blocked` means at least one case applies and the candidate does
not satisfy its lesson. `Clear` means every ranked case was
rejected or satisfied, with reasons. `No match` means the ranking
was empty and you abstained. List each case decision with evidence,
then open questions separately.
