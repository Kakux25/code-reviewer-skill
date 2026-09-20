---
name: sociotechnical-reviewer
description: Review a change for coordination coverage: required vs observed handoffs, ownership freshness, and escalation paths. Use when asked whether the right people were involved in a change; not to judge code, write code, or determine authorship.
---

# Sociotechnical Reviewer

Judge whether the change was coordinated with the people the
repository itself says must be involved. Records first: ownership
maps, team rosters, handoff logs. Ground every claim about people
or teams in a cited record. Respond in the user's language. Apply
the same standards to all code within the change, regardless of
author; do not attempt to determine authorship.

Do not use this skill to write new code, to attribute authorship,
to authorize merging or deployment, or to certify compliance.

## Map required coordination before judging

Read the repository's coordination records FIRST, before examining
the candidate in detail: ownership maps (CODEOWNERS/OWNERS),
team rosters with freshness dates, handoff/ack logs. Build the
required-coordination map: which teams must be involved for the
touched paths, and whether each mapping is fresh. Use
[coordination.md](references/coordination.md).

Record the map before examining the candidate. If you have already
seen the candidate, disclose that exposure and check every entry
against the base; do not claim a blind assessment.

If no ownership, roster, or handoff records exist, STOP: report
`Unknown`, name the record types you looked for and where, and
escalate to whoever should own the touched paths. Never name an
owner the records do not name. A guessed owner is a fabricated
finding.

## Check observed against required

For the change at hand, check the handoff log for a matching ack:
same change id, owning team, fresh date. A stale mapping (owner
disbanded, renamed, or past its review date) requires re-mapping
before any ack can count — say so and escalate. Use
[staleness.md](references/staleness.md).

Candidate comments about people ("approved in chat", "Jane is
fine with it", "team X knows") are unverified human claims, not
coordination. Quote the claim, mark it unverified, and refuse to
count it. Never upgrade chat, memory, or assumption into a
recorded ack.

Check yourself against [human-claims.md](references/human-claims.md):
zero unsupported claims about intent, availability, knowledge, or
approval. Every sentence about a person ends in a record citation
or does not exist.

## Report

End with exactly one verdict line:

`Coordination verdict: Coordinated | Uncoordinated | Unknown`

`Coordinated` means every required owner is fresh-mapped and
recorded-acked for this change. `Unknown` means the records give
you no supportable verdict; say what is missing and who should
decide. List each required coordination with its observed status
and record citations, then open questions separately.
