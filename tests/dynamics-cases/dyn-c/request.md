# Review request: dyn-c

Objective: review the bounded-retry change for system dynamics.

Scope: `bounded_sim.py` and `client.py` in candidate vs repo. Base
revision: `repo/`. Candidate: `candidate/`.

Build the causal model FIRST (links with polarity, provenance, and
status) before judging the candidate, then run the simulator to
check it. Report one verdict: Stable, Unstable, or Uncalibrated.

Note: this fixture tests candidate-only stability. The base
`POLICY="unbounded"` is not modeled by an executable base sim; the
simulator describes the candidate policy.
