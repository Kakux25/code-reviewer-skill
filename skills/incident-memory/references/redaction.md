# Redaction and retention

The case base mixes public lessons with restricted facts. The
boundary is structural: `render_public` drops `restricted`
entirely, and so must you.

## Rules

- Never quote a `restricted` value: no costs, customer names,
  hostnames, or internal notes — not verbatim, not paraphrased,
  not hinted ("a large customer", "a production host").
- Cite only public fields: id, title, mechanism, context, failure
  narrative, lesson, applies_when, not_when.
- If you catch yourself needing a restricted fact to make the
  case, stop: state the public lesson and escalate for the rest.
- Retention: your review keeps case ids and lessons; it must never
  become a second copy of restricted content. A review that quotes
  restricted fields fails redaction even if its verdict is right.
