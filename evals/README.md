# Eval Harness (Phase 1: deterministic)

Mechanical grading for the review cases in `tests/review-cases/`.
No LLM calls anywhere in this directory: everything here runs offline in CI.

## Layout

```
evals/
├── README.md            this file
├── thresholds.json      pre-declared pass bars (frozen before scored runs)
├── grader.py            scores review outputs against answer keys (stdlib only)
├── check_integrity.py   the CI gate: schema, anchors, suites, skill lint,
│                        thresholds, grader self-test (stdlib only)
└── samples/
    ├── good/case-*.md   synthetic reviews that MUST pass 4/4
    └── bad/case-*.md    synthetic reviews that MUST fail their case
```

Answer keys live with their cases: `tests/review-cases/case-*/answer-key.json`.
Each key declares the expected `decision`, allowed `architecture`/`soul`
verdicts, `plants` (must-catch) and `controls` (must-not-flag).

## Blindness rule

`answer-key.json` and `tests/EXPECTED.md` are the answer sheet. An agent
under evaluation must never read them; only the harness (and CI) may.
A review run that had key access is void.

## Run

```sh
# Full deterministic gate (what CI runs):
python3 evals/check_integrity.py

# Score a directory of review outputs (case-a.md ... case-d.md):
python3 evals/grader.py --reviews <dir> --out grading.json
```

To produce review outputs, run each `tests/review-cases/case-*/request.md`
blind (with and without the skill for a comparison), save each review as
`case-*.md`, then grade. LLM runs are manual/scheduled and never part of
the per-push gate: they cost money and minutes, and no reference harness
gates merges on them.

## What the grader checks (mechanical proxy)

- Decision: the first decision token in the decision section
  (`Changes requested`, `No actionable findings`, `Incomplete`) is the
  expected one. Sections are markdown `##` sections, else the triggering
  line plus continuations, else the whole document.
- Verdicts: the first architectural-verdict token on architecture lines
  (else verdict-section lines) is within the allowed set, and likewise
  for soul. Reviews should use the skill's verdict vocabulary literally
  (`High`, `Betrayed`, ...); later rationale mentions are ignored.
- Every plant: file cited + one evidence token (+ priority token when
  the plant declares one, e.g. P1).
- Every control: `not_flagged` (no P0-P3 on that file) or `forbid_phrase`
  (e.g. claiming the case-a suite passes when it fails by design).

Case pass = all of the above. Suite gate = 4/4 (`thresholds.json`).

## Known limits (honest)

- Lexical matching is coarse: a citation next to a token does not prove
  the diagnosis is correct, and negation ("no partial publication")
  contains the token it denies. The B1 plant is the known weak spot.
- Priority tokens are checked document-wide, not attached to a finding.
- Real-review calibration (judge-vs-human agreement) is Phase 2, not here.
- 4 synthetic single-author fixtures cannot prove general accuracy; the
  Phase 3 battery (20+ cases, shadow subset from real bugs) addresses that.

## Method sources

rltree/agentic-engineering `agent-evals-observability` (executable oracles
first, tested instruments), folkol `make-eval` (plants + controls,
pre-declared thresholds, frozen artifacts), espalier-engineering `eval/grill`
(answer key in fixture, judge validation, shadow subset), weareikko
`code-review` (trajectory + LLM-judge evals outside the merge gate),
kbichave `skill-reviewer` (skill-quality rubric incl. negative triggers).
