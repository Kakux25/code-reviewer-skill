## Review: heater controller change (stpa-a) — Generic review, no skill

**Baseline established from repo safety docs (before judging candidate):**

From `tests/stpa-cases/stpa-a/repo/docs/losses-hazards.md`:
- L1: heater fire
- H1: heater energized while room unattended
- H2: heater energized while temp sensor faulty
- SC1: must de-energize when presence lost
- SC2: must never energize on faulty sensor reading

From `tests/stpa-cases/stpa-a/repo/docs/control-structure.md`:
- Control actions: Controller → Heater {energize, de-energize}
- Feedback: Presence {present, absent}, Temp {celsius} or {fault}
- Controller must track occupancy + sensor health

Base `tests/stpa-cases/stpa-a/repo/controller.py` complies: `fault → de-energize`, `not present → de-energize`, `temp<18 → energize`.

**Candidate findings (`tests/stpa-cases/stpa-a/candidate/controller.py`):**

1. **Energizes on faulty sensor — violates SC2 / causes H2 → L1.**
   - Candidate line 3-4: `if temp == "fault": return "energize" # keep heating through sensor faults`
   - Base returned `de-energize` here. This is a direct inversion of the safe action.
   - Scenario: temp sensor reports `fault` → controller issues `energize`. Per `losses-hazards.md` SC2/H2, this is forbidden; uncontrolled heating risks L1 fire.

2. **Ignores presence — violates SC1 / causes H1 → L1.**
   - Candidate deleted the `if not present: return "de-energize"` check. `present` parameter is now unused.
   - Scenario: `present=False, temp=10` → candidate returns `energize`; base returned `de-energize`. Per `losses-hazards.md` SC1/H1 and `control-structure.md` occupancy model, the controller has dropped required occupancy feedback.

3. **Docs unchanged, so no new justification.**
   - `candidate/docs/losses-hazards.md` and `candidate/docs/control-structure.md` are identical to repo versions. SC1/SC2 still apply; candidate violates both.

No mitigating factors found. Two independent unsafe control actions, each sufficient for a fire hazard.

**Verdict: Unsafe**

