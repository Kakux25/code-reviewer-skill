# Safety STPA Review: stpa-a heater controller

## Safety model (from repo, established before judging candidate)

Losses and hazards from `tests/stpa-cases/stpa-a/repo/docs/losses-hazards.md`:
- L1: heater fire (property damage, harm).
- H1: heater energized while the room is unattended.
- H2: heater energized while the temperature sensor is faulty.

Safety constraints:
- SC1: the controller must de-energize the heater when presence is lost.
- SC2: the controller must never energize the heater on a faulty sensor reading.

Control structure from `tests/stpa-cases/stpa-a/repo/docs/control-structure.md`:
- Controller -> Heater: control actions {energize, de-energize}.
- Feedback: presence sensor {present, absent}, temp sensor {celsius} or {fault}.
- Required process model: room occupancy, sensor health.

Base enforcement in `tests/stpa-cases/stpa-a/repo/controller.py`:
- SC2 enforced by lines 3-4 (`if temp == "fault": return "de-energize"`).
- SC1 enforced by lines 5-6 (`if not present: return "de-energize"`).

## Unsafe control actions

### Finding 1: energize on faulty sensor — Wrong
- Control action and variant: `energize`, Wrong (acting on faulty feedback).
- Hazard trace: H2 → L1 (`repo/docs/losses-hazards.md`).
- Candidate code: `tests/stpa-cases/stpa-a/candidate/controller.py:4` — `return "energize"  # keep heating through sensor faults`.
- Violated constraint: SC2. Status in candidate: Broken. It was Enforced before (base lines 3-4).
- Note on candidate claim: "keep heating through sensor faults" is a claim, not analysis; it does not override documented SC2.
- Smallest correction: restore `if temp == "fault": return "de-energize"` as the first guard.

### Finding 2: de-energize omitted when presence lost — Omitted
- Control action and variant: `de-energize`, Omitted (not issued when the process model requires it on `absent`); equivalently `energize`, Wrong for that process state.
- Hazard trace: H1 → L1 (`repo/docs/losses-hazards.md`).
- Candidate code: `tests/stpa-cases/stpa-a/candidate/controller.py:5-7` — presence feedback is ignored; `if temp < 18: return "energize"` fires even when unattended. The base guard (`repo/controller.py:5-6`, `if not present: return "de-energize"`) is gone.
- Violated constraint: SC1. Status in candidate: Broken. It was Enforced before.
- Smallest correction: restore `if not present: return "de-energize"` before the heating branch.

## Constraint summary
- SC1: Broken (candidate removes the presence guard).
- SC2: Broken (candidate inverts the fault guard to energize).

## Open questions
None. Both findings trace fully: control action + variant, candidate location, hazard id, loss id, constraint id.

Safety verdict: Unsafe
