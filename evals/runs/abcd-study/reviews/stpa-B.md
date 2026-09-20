Study arm B (code-reviewer skill only) — STPA-A heater controller review.

**Scope:** `candidate/controller.py` vs base `repo/` (code + docs). Base: `tests/stpa-cases/stpa-a/repo/controller.py`, `repo/docs/losses-hazards.md`, `repo/docs/control-structure.md`. Candidate: `tests/stpa-cases/stpa-a/candidate/controller.py` (docs unchanged). Did not open `expected.json`.

**Independent criteria (from base, before detailed candidate judgment):**
Base docs establish: L1 heater fire; H1 energized while unattended; H2 energized on faulty sensor; SC1 de-energize when presence lost (`repo/docs/losses-hazards.md:8`); SC2 never energize on faulty reading (`losses-hazards.md:9`). Base code implements SC2 first (`repo/controller.py:3-4`), then SC1 (`repo/controller.py:5-6`), energizing only when present and temp < 18. (Disclosure: candidate diff seen during rubric recording; every criterion checked against the base, not the patch.)
- Rubric v1, axis R1 (primary): fault-safe interlock — faulty reading must yield de-energize. Preserve anchor: early de-energize on `"fault"`. Violate anchor: any energize path on `"fault"`.
- Rubric v1, axis R2 (primary): occupancy gating — absent presence must yield de-energize. Preserve anchor: presence check gates every energize path. Violate anchor: energize while `present` is false.

**Review (brief format):**

1. **Decision:** `Changes requested` — candidate commands the hazardous action under both documented hazard conditions.
2. **Findings:**
   - P0, `candidate/controller.py:3-4`: `step()` returns `"energize"` on `temp == "fault"` (comment: "keep heating through sensor faults"), violating SC2/H2. Proof: executed — cand `fault+present → energize`, `fault+absent → energize`; base returns `de-energize` for both. Consequence: H2 → L1 heater fire on uncontrolled heating with no valid feedback. Fix: return `"de-energize"` on fault (restore base lines 3–4).
   - P1, `candidate/controller.py:2-7`: `present` parameter accepted but never read — occupancy gate deleted, violating SC1/H1. Proof: executed — cand `absent+cold → energize`; base returns `de-energize`. Consequence: H1 → L1, heater energized in unattended room on every cold reading. Fix: restore `if not present: return "de-energize"` before the energize path.
   - No counterexample or compensating guard: candidate docs are identical to base (SC1/SC2 still stated), and `step()` has no callers in scope that could re-impose the gates (single-function module; no other repo code). Both defects are regressions introduced by the change, not pre-existing.
3. **Verdicts:**
   - Architectural verdict: `Low` — significant primary-axis violations on R1 (fault path inverted to energize) and R2 (occupancy gate removed); gaps: [R1: energize-on-fault at candidate/controller.py:4], [R2: presence input ignored, candidate/controller.py:2-7]. Change type: feature/simplification attempt that breaks essential safety contracts. Complexity: Low (single function, but safety-critical invariant).
   - Soul verdict: `Unverifiable` — repo documents safety constraints, not identity/manifesto essence; no essence statements to assess against.
4. **Checks and limits:** `python3` import-and-call comparison of base vs candidate `step()` over 5 input combos (fault×presence, absent+cold, present+cold, present+warm) — passed, confirms both findings (execution evidence). Static: full read of base + candidate code and docs. No existing test suite in scope; no callers beyond `step()` in the provided material.

**Requested safety verdict: Unsafe** (candidate energizes on faulty sensor feedback and while unattended, realizing H1 and H2 → L1).
