# Causal links

Every causal claim in the review takes exactly one row:

`cause -> effect (polarity) [provenance: status]`

## Polarity

- `(+)`: more cause → more effect (same direction).
- `(-)`: more cause → less effect (opposite direction).

A loop's character is the product of its signs: even negatives =
reinforcing (R), odd = balancing (B). Label each loop R or B with
its evidence. Never assert a loop you cannot close link by link.

## Provenance

- `observed`: you ran it (simulator output, measurement, log).
  Cite the command and the numbers.
- `documented`: the repository states it (docs, config, code
  constant). Cite the file and line.
- `assumed`: neither — your hypothesis. Mark it LOUDLY and never
  let an assumed link carry a verdict alone.

## Status

- `holds`: evidence supports the link under the candidate.
- `broken`: the candidate severs or inverts it; cite the change.
- `untested`: no evidence either way; downgrade any verdict that
  needs it.

A review with zero `observed` or `documented` links is
`Uncalibrated`, not Stable. Links without provenance are stories.
