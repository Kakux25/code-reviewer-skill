# Judge prompt (frozen for Phase 2 validation)

You are scoring a code review against an answer key. Read the rubric,
the answer key, and the review carefully. Score ONLY what the review
states; do not consult any other file, and do not re-review the code.

Output exactly one fenced JSON block and nothing else:

```json
{"architecture": 0, "controls": {"<control-id>": {"quote": "<=200 chars verbatim from the review supporting the score>", "score": 0}}, "decision": 0, "plants": {"<plant-id>": {"quote": "<=200 chars verbatim from the review supporting the score>", "score": 0}}, "soul": 0}
```

Rules:

- Score every item declared in the key: `decision`, `architecture`,
  `soul` (0/1), each plant id (0/1/2 per the rubric's level criteria
  a–e), each control id (0/1).
- `quote` must be verbatim text from the review (empty string only
  when the item is entirely absent). Quotes are audit evidence;
  agreement is computed on scores only.
- No extra keys, no markdown outside the fence, no explanation.

## Rubric

{RUBRIC}

## Answer key

```json
{ANSWER_KEY}
```

## Review under judgment (case {CASE})

```markdown
{REVIEW}
```
