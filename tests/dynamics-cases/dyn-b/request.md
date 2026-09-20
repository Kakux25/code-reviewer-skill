# Review request: dyn-b

Objective: review the autoscaler retuning for system dynamics.

Scope: `scale_sim.py` and `scaler.py` in candidate vs repo. Base
revision: `repo/`. Candidate: `candidate/`.

Build the causal model FIRST (links with polarity, provenance, and
status) before judging the candidate, then run the simulator to
check it. Report one verdict: Stable, Unstable, or Uncalibrated.
