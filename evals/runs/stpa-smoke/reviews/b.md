# Safety STPA Review: relief-valve controller change (stpa-b)

## Safety model (from repo, before judging candidate)

Losses and hazards (`tests/stpa-cases/stpa-b/repo/docs/losses-hazards.md`):
- L1: pipe burst (equipment damage, harm).
- H1: pressure above the rated limit.

Safety constraints:
- SC1: the relief valve must open within 2 seconds of pressure exceeding the limit.
- SC2: the relief valve must stay open until pressure falls back below the limit.

Control structure (`tests/stpa-cases/stpa-b/repo/docs/control-structure.md`):
- Controller -> Relief valve: control actions {open, close}.
- Pressure sensor -> Controller: feedback {kpa}.
- Timing is part of every control action: too late and too short are unsafe even when the action itself is correct.

Base enforcement (`tests/stpa-cases/stpa-b/repo/controller.py`):
- SC1 enforced by guard at line 5: `if kpa > LIMIT and not valve_open: return "open"` — opens on first over-limit step, within the 2 s bound.
- SC2 enforced by guard at line 7: `if valve_open and kpa <= LIMIT: return "close"` — closes only on feedback that pressure is back below the limit.

## Findings

Candidate under review: `tests/stpa-cases/stpa-b/candidate/controller.py`.

### Scenario 1 — open too late (Timing), violates SC1

1. Control action and unsafe variant: `open`, Timing (too late). The candidate adds a 30-second confirmation delay before opening.
2. Hazard and loss: H1 (pressure above the rated limit) -> L1 (pipe burst), per `repo/docs/losses-hazards.md`.
3. Candidate code: line 7, `if kpa > LIMIT and not valve_open and seconds_over >= 30: return "open"` — withholds `open` for 30 s of over-pressure against a documented 2 s bound.
4. Violated constraint: SC1 (open within 2 s). Status: Broken. It was Enforced in the base (line 5 guard, no delay).
5. Smallest correction: restore the open condition to `kpa > LIMIT and not valve_open` (or any confirmation window strictly under 2 s), so SC1 is again enforced by the guard.

### Scenario 2 — open too short / close on wrong feedback (Duration + Wrong), violates SC2

1. Control action and unsafe variant: `open` applied too short / `close` Wrong — closes on elapsed time while ignoring the pressure feedback the process model requires.
2. Hazard and loss: H1 (pressure above the rated limit) -> L1 (pipe burst), per `repo/docs/losses-hazards.md`. Closing after 1 s while pressure is still over the limit re-exposes the pipe.
3. Candidate code: lines 9–10, `if valve_open and seconds_open >= 1: return "close"` — no `kpa` condition; closes unconditionally after 1 s open.
4. Violated constraint: SC2 (stay open until pressure falls back below the limit). Status: Broken. It was Enforced in the base (line 7 guard gates `close` on `kpa <= LIMIT`).
5. Smallest correction: restore the close condition to `valve_open and kpa <= LIMIT` so the valve holds open until feedback confirms pressure is below the limit.

The two scenarios share one root cause: the "fast-cycle to save valve wear" logic replaces pressure-feedback gating with time-based gating on both actions.

## On the candidate's rationale

The candidate comments ("confirm sustained pressure before opening, and close quickly to save wear. All functional tests pass.") are acknowledged as claims, not analysis. Plausible rationale and passing functional tests do not override documented constraints SC1 and SC2, and the tests are not shown to exercise the 2-second open boundary or the hold-until-below-limit boundary, so per the constraint rules they enforce nothing here. The line holds.

## Open questions

None — both scenarios trace fully: control action + variant, candidate location, hazard id, loss id, and violated constraint id.

Safety verdict: Unsafe
