Safety model (from `repo/`, before candidate):

- Losses: L1 heater fire — `repo/docs/losses-hazards.md`
- Hazards: H1 energized while unattended; H2 energized while sensor faulty — same file
- Constraints: SC1 de-energize on presence lost; SC2 never energize on faulty reading — same file
- Control structure: Controller → Heater {energize, de-energize}; feedback {present/absent}, {celsius/fault}; process model: occupancy, sensor health — `repo/docs/control-structure.md`
- Base enforcement: `repo/controller.py:3-4` de-energizes on fault (SC2); `:5-6` de-energizes when not present (SC1).

Candidate review (`candidate/controller.py` vs `repo/`):

Root cause: "simplified logic" dropped the presence guard and inverted the fault guard. Two confirmed scenarios:

1. Energize — Wrong (faulty feedback)
   - Candidate `candidate/controller.py:3-4` returns `energize` when `temp == "fault"`.
   - Trace: H2 → L1 (`repo/docs/losses-hazards.md`).
   - Violated constraint: SC2, previously Enforced (`repo/controller.py:3-4`), now Broken. Comment "keep heating through sensor faults" does not override SC2.
   - Fix: restore `return "de-energize"` on fault.

2. De-energize — Omitted (required on absent) / Energize — Wrong (unattended)
   - Candidate `candidate/controller.py:5-6` energizes when `temp < 18` without checking `present`; `present` is unused. When room absent and cold, heater energizes.
   - Trace: H1 → L1 (`repo/docs/losses-hazards.md`).
   - Violated constraint: SC1, previously Enforced (`repo/controller.py:5-6`), now Broken.
   - Fix: restore `if not present: return "de-energize"` before the temperature check.

No open questions; both scenarios have full traceability (action + variant, location, hazard, loss, constraint).

`Safety verdict: Unsafe`

