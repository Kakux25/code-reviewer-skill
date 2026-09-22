# ADR-0004: Follow-up Audit Response — Critique Rebuttal + Tooling Fixes

Status: accepted; fixes merged on top of audited `e5b8450`.

## Decision

Accept the independent follow-up counter-replica (white-box, same
auditor as ADR-0003, disclosed non-blind) and an internal multi-agent
validation as joint evidence. Merge the fix groups below, record the
overstatements found in the September HTML critique ("El método es
mejor que la evidencia"), and keep frozen artifacts untouched.

## Unified rebuttal (mine + auditor's; overlaps merged)

Accepted from the HTML critique: no demonstrated detection lift over
the LLM baseline; P0–P3 anchors are four synthetic micro-cases; no
High/Low↔outcome or soul↔outcome validity data; no precision/recall
on real defects; the A/B mixes retries and arms; the grader is a
lexical proxy. The repo's own RUN.md already states the lift "is not
finding bugs" (verbatim, `battery-noskill/RUN.md:83-86`).

Refuted or corrected, with evidence:

1. "13 plants diagnosed": recalculated as 13/13 correct decisions on
   positive cases in BOTH arms; rubric passes 2/16 vs 16/16;
   adjudicated-substance means tied at 0.77125. "Undemonstrated lift"
   is defensible; "proven format-only lift" exceeds the comparison.
2. "9.2% vs 60–90%": denominator error. Sun et al. RQ3 uses 3,879
   valid comments (2,990 for the 9.2% model); RQ2 Table IX over 5,652
   comments shows 4.2/0.9/19.2/6.5% per AI tool vs 60% human. Mixed
   subsets presented as one comparison.
3. "14% refutes bugs-as-value": Bacchelli & Bird's 78/570 measures
   feedback composition, not value, severity avoided, or detection
   share. Tufano et al. (n=29, GPT-4) limits expectations (no more
   severe findings, anchoring) but is not an experiment on this repo.
4. "not diff size" refuted: the adjacent sentence ("Do not skip
   simple changes…", SKILL.md) concedes small-diff risk, and the
   cited literature is correlational. Real tension, wrong verdict
   word. The sentence was still too categorical: reworded to count
   diff size among the risk factors (this ADR, fix group 5).
5. Soul "unfalsifiable / severity without anchor": false on both.
   `soul.md` admits falsifiable requirements (memory-only operation);
   priority was already by impact ("typically P1"). Corrected to
   never-P1-by-default (fix group 5); full "principios documentados"
   operationalization stays future work.
6. "Re-adjusted after failing" (p-hacking insinuation): against a
   pre-registered triage ("never weaken the key", smoke/RUN.md:18-23),
   frozen thresholds, and keys explicitly NOT widened to the baseline
   (noskill/RUN.md:64-66). Fixture-validation is not score-hacking.
7. "1 script" inventory: true of the isolated skill only; the full
   repo holds 17 tooling scripts. Scope corrected, efficacy unclaimed.
8. "Model unstated": runner+provider were stated (judge-k1/RUN.md:18);
   the exact pinned model id is what is missing.
9. Crossed citation (merge disclaimer paired with the accuracy quote)
   and "13 plants" paraphrase: minor audit sloppiness, both now fixed
   in this record.

## Fix groups (all verified; battery 179/179, hard 14/14)

1. `scripts/evidence.py` F1: store annotations (`store_note`) are
   excluded from observation identity. Repeating a tainted
   observation keeps two versions and a stable digest; real material
   change still appends; timestamp-only still idempotent. Regression:
   `test_repeated_drift_is_idempotent`.
2. `evals/check_integrity.py` + new `evals/structured_unittest.py`
   F2: designed-fail suites must fail by executed call-phase tests
   under TWO agreeing oracles (structured per-test identity/phase +
   traceback-text classifier). setUp/tearDown/import-only failures
   never certify. Self-test step 11 extended; case-i (candidate
   TypeError) stays green as the control.
3. `scripts/evidence.py` G1: split guarantees into two APIs.
   `get()` keeps latest-observation + rollback-trap semantics;
   new `get_exact()` binds digest to bytes. The follow-up probe as
   written tests the previous guarantee via `get()` and still fails
   BY DESIGN; the adapted expectation (exact reads via `get_exact`)
   passes and is pinned by
   `test_exact_pin_binds_bytes_despite_append`.
4. `evals/grader.py`: same-clause negation guard (B1), plant credit
   scoped to finding sections (open questions are not diagnoses),
   forbid_phrase exempts base-attributed statements (F-C1/I-C1).
   New gate step 6b pins all three rules.
5. Wording: SKILL.md counts diff size as a risk factor; "static
   reading" replaces "static analysis"; soul forbids default P1;
   `evals/README.md` count fixed (20→22) and limits updated.
6. Deferred honestly, not fixed: D/code-C1 traceability trip stays a
   documented lexical-proxy limit (weakening the control would be
   post-hoc); arch-letter dead weight in 9 single-function keys
   stays frozen (structural/behavioral split deferred to a
   pre-registered battery v3); all future protocols anchor
   pre-registration in commits (K-3 pattern), recorded in
   `docs/assurance/validation-plan.md`.

## Residuals and next step

Endorsed: the auditor's preregistered pilot (20 held-out changes, 5+
repos, 10 defects + 10 controls, same-model ±skill arms plus a
deterministic baseline, blind dual adjudication) — NOT run here.
Precision/recall/addressing on real defects, cross-family
replication, and judge validation on E–T remain unmeasured.
External literature below was accepted from the auditor's hashed
manifest, not re-verified here.
