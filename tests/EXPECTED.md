# Expected Review Behaviors

Open only AFTER completing a blind review. This file reveals what each
evaluation case measures.

| Case | Review behavior |
| --- | --- |
| A | Identify a functional defect while assessing architecture separately. The candidate is intentionally defective, so its failing tests do not indicate a broken skill package. |
| B | Accept an alternative implementation that preserves the required architectural property. |
| C | Report insufficient architectural evidence when only an isolated snippet is available. |
| D | Flag a soul betrayal in a candidate whose tests pass, keeping function and essence separate. |
| E | Catch an off-by-one slice end while leaving the unrelated formatter alone. |
| F | Diagnose shared state from a mutable default argument. |
| G | Flag a swallowed OSError that breaks the missing-vs-empty error contract. |
| H | Flag the dropped containment check (absolute names escape the root). |
| I | Reject a broken public signature as an architectural contract violation. |
| J | Catch N+1 per-item fetching against the single-round-trip objective. |
| K | Accept a behavior-preserving simplification (negative case). |
| L | Accept an order-preserving algorithmic improvement (negative case). |
| M | Flag a silent-library betrayal (stdout write) in a passing suite. |
| N | Flag a hidden side effect (in-place sort) behind an honest name. |
| O | Report Incomplete when the missing base could change the findings. |
| P | Flag a hardcoded production secret in a passing suite. |
| Q | Flag eval() on untrusted input in a passing suite. |
| R | (Shadow, Heartbleed pattern) Flag the missing bounds check on a trusted length. |
| S | (Shadow, falsy-ID pattern) Flag the truthiness check that denies id 0. |
| T | (Shadow, cache-aliasing pattern) Flag the served-by-reference cache corruption. |
| U | Accept properly added containment checks (guard-present negative). |
| V | Attribute the untouched helper's latent bug to base, not as a regression (pre-existing negative). |
