# Unsafe control actions

For each control action in the documented control structure, test
four variants against each hazard. A variant is unsafe only if you
can trace it from the candidate through a hazard to a loss, citing
repository files at every step.

## The four variants

1. **Omitted**: the action is not issued when the process model
   requires it (missing guard, ignored feedback, dead code path).
2. **Wrong**: the action issued is incorrect for the process state
   (wrong branch, inverted condition, acting on faulty feedback).
3. **Timing**: issued too early or too late relative to the
   documented timing constraint (delays, debounces, confirmation
   windows that exceed the allowed bound).
4. **Duration**: applied too short or too long (early release,
   missing hold-until, runaway without timeout).

Timing and duration are first-class failures: a correct action at
the wrong time is unsafe. Check numeric bounds against the
documented constraints; do not invent bounds the repository never
states.

## Traceability rule

Every scenario needs: control action + variant, candidate location,
hazard id, loss id, and the violated constraint id. Missing any
link, it is an open question, not a finding. Never upgrade an open
question to a finding because the code "looks dangerous".
