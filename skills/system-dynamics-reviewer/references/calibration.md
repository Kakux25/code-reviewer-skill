# Calibration

Dynamics claims need numbers: arrival rates, service capacity,
queue bounds, retry counts, delays, timescales. The repository
must supply them; you must not invent them.

## Rules

- Stocks and flows first: name what accumulates (queue, backlog,
  connections) and what moves it (arrivals, service, retries,
  timeouts, scaling). A dynamics verdict without identified
  stocks is speculation.
- Delays decide: for every balancing loop, compare the loop delay
  against the disturbance duration with numbers from the
  repository. Delay longer than disturbance = the loop cannot
  save you; say so with the ratio.
- Simulators are evidence, not oracles: run them, quote their
  numbers, and check the numbers against your loop structure. If
  the sim disagrees with your model, fix the model — do not
  explain the sim away.
- Suites can pass on disaster: a green suite whose assertions
  document explosion (peak > 1000) supports Unstable, not Stable.
  Read the assertions, not the color.

## Uncalibrated

When no load, latency, rate, or capacity numbers exist in the
repository, STOP: report `Uncalibrated`, list the measurements
that would calibrate the verdict (what to measure, where), and
escalate. Never upgrade Uncalibrated to Stable because the change
"looks small". Small changes move TTLs; TTLs move stampedes.
