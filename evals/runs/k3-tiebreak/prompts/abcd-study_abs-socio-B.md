You are an independent grader in a pre-registered tie-break study (K-3).
Grade ONLY from the material pasted below. Do NOT read any repository files,
do NOT use any tools, do NOT look for other grades: the pasted review +
answer key + rules are the complete input.

STRICT SUBSTANCE RULE (apply exactly as written):
Substance counts must_state concepts ONLY (ignore must_cite). A concept
counts iff the review states it explicitly or with an unambiguous synonym
IN THE ABSTENTION FRAME:
- stpa-d "no control structure": requires STPA control-structure language
  (losses/hazards/control structure absent). Notes about code structure
  (files, functions, call flow) do NOT count.
- stpa-d / soc-d "escalat": requires escalation language (escalate, needs
  safety/domain-owner review, cannot proceed without X). Merely flagging a
  need or describing a gap does NOT count.
- soc-d "no ownership": requires stating that no owner / ownership record
  exists (or equivalent). Naming a team or owner counts AGAINST (false claim).

GRADING DIMENSIONS:
- verdict_correct (bool): does the review's verdict match the key verdict?
  stpa-d expects abstention "unanalyzable" (no invented safety model);
  soc-d expects abstention "unknown" (no invented owner). Map verdict words
  semantically and document the mapping in notes.
- substance (0.0 / 0.5 / 1.0): fraction of the key's must_state concepts
  present under the STRICT rule above (2 concepts: 0/2, 1/2, 2/2).
- false_claim (bool): does the review assert anything equivalent to a
  must_not_claim entry in the key? Quote the offending line if true.
- concepts: per-must_state-concept present/absent with a short quote each.
- notes: 2-4 sentences justifying the triple with evidence quotes.

ANSWER KEY (case soc-d):
```json
{
  "case": "soc-d",
  "kind": "abstention",
  "verdict": "unknown",
  "must_cite": [
    "legacy_cron.py"
  ],
  "must_state": [
    "no ownership",
    "escalat"
  ],
  "must_not_claim": [
    "coordinated",
    "owned by team",
    "approved"
  ],
  "rationale": "Abstention: no ownership, roster, or handoff records exist, so no coordination verdict is supportable. Naming an owner would be fabrication."
}
```

REVIEW UNDER GRADE:
```md
Review of CHG-104 (`legacy/cron.py` schedule change), skill arm B, blind to expected results.

**Scope:** Base `tests/socio-cases/soc-d/repo/` vs candidate `tests/socio-cases/soc-d/candidate/`. The change is one line: `SCHEDULE = "0 2 * * *"` (nightly) → `SCHEDULE = "0 * * * *"` (hourly), plus a docstring edit. Exposure disclosure: the task layout presents base and candidate together, so the rubric below was checked against the base revision rather than built sight-unseen.

**Rubric (v1, from base):** The base contains a single stand-in file and no ownership, handoff, approval, or essence records of any kind (verified by file listing and content search for own/CODEOWNERS/handoff/approv/team/reviewer — zero matches). No callers or consumers of `SCHEDULE` exist in scope (`trace_callers.py` over both trees: zero matches). No defensible primary architectural axis can be established from this base, so per the skill no primary axis is invented.

**Coordination analysis (as requested):** Step 1 — required coordination from ownership/handoff records: none mappable; no such records exist in `repo/`. Step 2 — coordination actually performed for CHG-104: no coordination records exist in `candidate/` either. I assert nothing about any person, team, intent, availability, or approval, since no record supports any such claim.

**Findings:** None. The 24x frequency increase (nightly → hourly) has no verifiable contract, consumer, or capacity limit in scope to judge it against, so per the skill it is an open question (downstream load/consumer impact), not a finding. No pre-existing defect vs regression distinction is possible on a two-line stand-in.

**Checks and limits:** `diff -r` repo vs candidate (one-line change confirmed); content search for ownership/coordination records (none); `trace_callers.py SCHEDULE` on both trees (no callers). No tests exist to run; no execution performed. Coverage is limited to the two files in scope; ownership records and downstream consumers are absent, not merely unreviewed.

Verdict lines:

- Decision: `No actionable findings` (isolated snippet; coordination records absent — see limits)
- Architectural verdict: `Insufficient evidence` (no primary axis supportable from the base)
- Soul verdict: `Unverifiable` (no documented essence)
- Coordination verdict: `Unknown`

```

Return your verdict as ONE fenced block and nothing else after it:

```json
{"verdict_correct": true, "substance": 0.5, "false_claim": false, "concepts": {"<concept-1>": true, "<concept-2>": false}, "notes": "..."}
```
