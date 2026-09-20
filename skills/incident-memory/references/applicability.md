# Applicability judgment

Transfer is a mechanism claim: the failure mode of the past
incident must be reproducible by THIS candidate. Shared words are
not shared mechanisms.

## The transfer test

A case transfers only if BOTH hold:

1. The candidate matches at least one `applies_when` condition,
   evidenced by candidate lines.
2. The candidate matches NO `not_when` condition.

Fail either, and the case is Rejected (condition 1 fails) or
Satisfied (condition 2 matches). State the deciding lines.

## Common lures

- **Motivation lure**: the author mentions overload, spikes, or
  slowness, but the change adds no loop, no load, no shared
  resource. Rank follows the words; judgment must reject.
- **Domain lure**: the change touches the same subsystem (cache,
  pool, deploy) via a different mechanism. Subsystem match is not
  mechanism match.
- **Lesson-already-present**: the candidate already implements the
  lesson (backoff present, TTLs jittered). That is Satisfied, not
  Applied — do not block a candidate for a lesson it upholds.

When uncertain whether a mechanism transfers, say so, name the
missing evidence, and do not block on suspicion. Downgrade to an
open question, never upgrade to Applied.
