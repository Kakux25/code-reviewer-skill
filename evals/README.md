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
│                        thresholds, grader self-test, hand-score schema,
│                        agreement self-test (stdlib only)
├── rubric.md            Phase 2 semantic scoring rubric (plant levels 0/1/2)
├── judge_prompt.md      frozen LLM-judge prompt (template)
├── judge.py             LLM-judge runner: prompt per review, JSON verdicts
│                        (manual/scheduled; NEVER in the merge gate)
├── agreement.py         judge-vs-hand agreement scorer (stdlib only)
├── hand_scores.json     hand-scored gold for the 16-review validation set
├── samples/
│   ├── good/case-*.md   synthetic reviews that MUST pass (cases a-d)
│   └── bad/case-*.md    synthetic reviews that MUST fail their case
└── runs/<date>-*/       frozen run artifacts (manifests, outputs, RUN.md)
```

Cases e-t ship their own `sample_good.md` / `sample_bad.md` next to the
fixture; cases a-d keep the Phase 1 `samples/` location.

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

Case pass = all of the above. Suite gate = N/N over the discovered
battery (`thresholds.json`; battery v2 = 20 cases, a-t).

## Phase 2: calibrated LLM judge (validated 2026-09-20)

The mechanical proxy cannot tell a correct diagnosis from a token near
a citation. `rubric.md` re-scores each review semantically (same items
as the keys; plants on a 0 missed / 1 mentioned / 2 diagnosed scale),
`hand_scores.json` is the single-scorer gold over 16 reviews (12 live
+ 4 bad), and `judge.py` runs the frozen prompt once per review:

```sh
# Score the validation set (needs an LLM CLI; costs money and minutes):
python3 evals/judge.py --manifest evals/runs/2026-09-20-judge-k1/manifest.json --out /tmp/judge-out
python3 evals/agreement.py --gold evals/hand_scores.json --judge /tmp/judge-out
```

Gate: item-level exact agreement >= 0.75 (plant levels exact).
First scored run: 95/96 = 0.990, gate MET
(`runs/2026-09-20-judge-k1/RUN.md`). Independent replication (K=2):
96/96 = 1.000, gate MET; K1-vs-K2 stability 95/96, single diff on
the known 1-vs-2 boundary item (`runs/judge-k2-stability/RUN.md`).
The judge stays out of the merge gate; CI only checks the gold
schema and the agreement self-test.

## Phase 3: 20-case battery + shadow subset (2026-09-20)

Sixteen fixtures (e-t) extend the battery to 20: defect battery e-j,
negatives k-l, soul cases m-n, Incomplete case o, security p-q, and
shadow subset r/s/t (patterns modeled on real bugs: Heartbleed-style
bounds leak, falsy-ID auth denial, cache aliasing — simplified
one-file fixtures, not the real code). Each new case ships its suite,
answer key with a declared suite outcome (pass/fail/absent), and
co-located good/bad sample reviews that the integrity gate grades.

## Known limits (honest)

- Lexical matching is coarse: a citation next to a token does not prove
  the diagnosis is correct, and negation ("no partial publication")
  contains the token it denies. The B1 plant is the known weak spot.
- Priority tokens are checked document-wide, not attached to a finding.
- Lexical grading stays coarse by design; semantic disputes go to the
  Phase 2 judge (agreement 0.990 on cases A–D; unvalidated on E–T).
- 20 single-author fixtures still cannot prove general accuracy; the
  shadow subset (R/S/T) is modeled on real-bug patterns, not sampled
  from real failures. Live-review calibration on the full battery and
  cross-family judge replication are future work.

## Method sources

rltree/agentic-engineering `agent-evals-observability` (executable oracles
first, tested instruments), folkol `make-eval` (plants + controls,
pre-declared thresholds, frozen artifacts), espalier-engineering `eval/grill`
(answer key in fixture, judge validation, shadow subset), weareikko
`code-review` (trajectory + LLM-judge evals outside the merge gate),
kbichave `skill-reviewer` (skill-quality rubric incl. negative triggers).
