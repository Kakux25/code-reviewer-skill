verdict_correct: true
substance: 1.0
false_claim: false
notes: Verdict "Violates" matches key "violates". All 3 required concepts present (3/3=1.0): ARCH.md cited with Rule D1, api->store edge via `from store import db` in candidate/api/fast_path.py, and bypass of service-layer audit stated twice. No must_not_claim violation: "acceptable" and "no violation" absent, and "conforming" appears only in "No conforming correction smaller than" (negated/fix-scope, not a conformance claim for the candidate) and in the "conformance.md" filename reference, which per instructions do not count as false claims.

