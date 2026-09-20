# Safety STPA Review: heater controller refactor (stpa-c)

## Safety model (from repo, established before judging candidate)

Losses (`tests/stpa-cases/stpa-c/repo/docs/losses-hazards.md`):
- L1: heater fire (property damage, harm).

Hazards:
- H1: heater energized while the room is unattended.
- H2: heater energized while the temperature sensor is faulty.

Safety constraints:
- SC1: controller must de-energize the heater when presence is lost (guards H1 -> L1).
- SC2: controller must never energize the heater on a faulty sensor reading (guards H2 -> L1).
- SC3: heater must de-energize after 60 minutes continuous run, watchdog (guards overheat -> L1).

Control structure (`tests/stpa-cases/stpa-c/repo/docs/control-structure.md`):
- Controller -> Heater: control actions {energize, de-energize}.
- Feedback: presence sensor {present, absent}, temp sensor {celsius} or {fault}, watchdog {minutes_on}.

Base enforcement (`tests/stpa-cases/stpa-c/repo/controller.py`):
- SC2: lines 3-4, `temp == "fault"` -> de-energize.
- SC1: lines 5-6, `not present` -> de-energize.
- SC3: lines 7-8, `minutes_on >= 60` -> de-energize.
- Energize only at lines 9-10 when all guards passed and `temp < 18`.

## Candidate analysis

Candidate (`tests/stpa-cases/stpa-c/candidate/controller.py`) consolidates the three guards into `_ok()` (line 3: `present and temp != "fault" and minutes_on < 60`), with `step()` returning de-energize when `not _ok(...)` (lines 6-7) and energizing only when `_ok` holds and `temp < 18` (lines 8-9).

Per-condition check (refactor rule: every guard must still trigger under the same conditions):
- SC1: `present` falsy -> `_ok` falsy -> de-energize. Same trigger as base. Enforced (lines 3, 6-7).
- SC2: `temp == "fault"` -> second conjunct false -> de-energize. Faulty reading can never reach the `temp < 18` comparison at line 8, same as base early return. Enforced (lines 3, 6-7).
- SC3: `minutes_on >= 60`, including exactly 60 (`60 < 60` is false) -> de-energize. Same boundary as base `>= 60`. Enforced (lines 3, 6-7).

Unsafe control action sweep (control actions {energize, de-energize}):
- Omitted de-energize: no — all three documented de-energize conditions still force de-energize.
- Wrong energize: no — energize still requires present AND non-faulty sensor AND minutes_on < 60 AND temp < 18, identical to base.
- Timing/duration: no — the 60-minute watchdog bound is preserved exactly; no delay, debounce, or hold-until was added or removed.

No scenario in the candidate reaches H1, H2, or any documented loss. No finding.

Open questions: none. Candidate docs are unchanged from repo docs.

## Constraint status in candidate

- SC1: Enforced (guard at lines 3, 6-7).
- SC2: Enforced (guard at lines 3, 6-7).
- SC3: Enforced (guard at lines 3, 6-7, boundary 60 preserved).

`Safety verdict: Safe`
