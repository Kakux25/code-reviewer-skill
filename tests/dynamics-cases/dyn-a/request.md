# Review request: dyn-a

Objective: review the retry-policy change for system dynamics.

Scope: `retry_sim.py` and `client.py` in candidate vs repo. Base
revision: `repo/`. Candidate: `candidate/`.

Build the causal model FIRST (links with polarity, provenance, and
status) before judging the candidate, then run the simulator to
check it. Report one verdict: Stable, Unstable, or Uncalibrated.
