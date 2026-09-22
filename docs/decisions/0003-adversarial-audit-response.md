# ADR-0003: Adversarial Audit Response — Tooling Contract Fixes

Status: accepted; fixes merged in `3f2d535` on top of audited `5ccb039`.

## Decision

Accept and merge the six fix groups below, closing all 11
adversarial findings of the September 2026 white-box audit, plus 14
regression tests and a new integrity-gate step pinning the
failure-classification rule:

1. `scripts/evidence.py`: drift compares all material fields
   (everything but `collected_at`); metadata drift is retained as a
   new revision preserving the incoming status; pinned reads return
   the latest observation and raise only on rollback past the pin.
2. `scripts/assemble.py`: a shared digest with conflicting
   integrity/kind refuses the merge; identifier-collision checks
   extend to `causal_links`, `incident_cases`, `safety_constraints`.
3. `scripts/envelope.py`: `dir_hash` uses length-prefixed framing
   per name and per content.
4. `scripts/validate_assurance.py`: claim-cycle detection is an
   iterative DFS with a shared done set (linear time).
5. `evals/check_integrity.py`: a designed-fail suite must fail by
   executed tests (`Ran N`, no ImportError); new step 11 self-tests
   the classifier.
6. `evals/judge.py`: exact score allowlist, true-int type checks, no
   exceptions on malformed verdicts, nonzero provider exit is an
   execution failure.

## Context

An external white-box audit targeted this repository at
`5ccb039`, with a rubric fixed before the implementation was read
(R1 conservative acceptance, R2 observation identity and immutable
provenance, R3 measurement validity). It delivered 14 executable
tests: 3 positive controls plus 11 adversarial probes. Pre-fix,
all 11 probes failed and the 3 controls passed; the repo's own
163-test battery was green throughout, which is what made the
probes valuable — they covered contracts the battery did not.

Each finding was then validated against independent external
sources (official docs, standards, and one benchmark paper;
bodies inspected, not snippets) before any fix was written. No
finding was refuted; the failure taxonomy ("11 failures in 8
causes") is partly interpretive (see Confidence).

## Evidence

Per finding: defect, fix, sources, executable proof.

- Store drops dirty state and metadata (`Store.put` compared
  `content_hash` only; clean→dirty at one HEAD aliased to one
  digest, 7 metadata fields silently lost). Fix: `_material`
  comparison excluding only `collected_at`; metadata drift keeps
  incoming status with an annotated reason; `get(expected=)` uses
  contains-semantics. Sources: S20 (identity covers the full
  record; dirty≠clean), S21 (builder/materials required), S22
  (agent identity inseparable). Proof: hard-tests
  `test_store_retains_real_git_dirty_state`,
  `test_store_retains_material_metadata_changes`; repo tests
  `test_metadata_drift_is_retained_not_aliased`,
  `test_pinned_read_returns_latest_observation`,
  `test_pin_still_detects_rollback`.
- Assembly order decides survival (shared digest, conflicting
  integrity: forward ACCEPT vs reverse INSUFFICIENT; conflicting
  `L-*` causal ids silently dropped). Fix: digest conflict
  refuses; collision rule covers all record groups. Sources: S25
  (fail securely), S26 (no silent drops in assurance records).
  Proof: hard-tests `test_assembly_order_cannot_hide_unverified_`
  `evidence`, `test_assembly_conflicting_causal_ids_refuse`; repo
  tests `test_shared_digest_conflict_refuses_both_orders`,
  `test_causal_collision_refuses`.
- Directory-hash framing collision (one file `a:(x NUL b NUL y)`
  vs two files `a:x,b:y` shared digest `938fbc10...`). Fix:
  8-byte big-endian length prefix per name and content. Sources:
  S23 (concatenation ambiguity; length-prefix required), S24
  (framing defect, not a SHA-256 break). Proof: hard-test
  `test_directory_hash_distinguishes_different_trees`; repo test
  `test_dir_hash_distinguishes_framing`.
- Validator recursion and blowup (1100-chain → RecursionError;
  shared 32-node DAG → timeout via exponential re-walks). Fix:
  iterative DFS with global done set. No registry source: standard
  algorithmics; consulted
  <https://cp-algorithms.com/graph/depth-first-search.html> plus
  [RecursionError](https://docs.python.org/3/library/exceptions.html#RecursionError)
  and [getrecursionlimit](https://docs.python.org/3/library/sys.html#sys.getrecursionlimit)
  docs. Proof: hard-tests
  `test_validator_accepts_deep_acyclic_graph_without_recursion_`
  `error`, `test_validator_shared_dag_finishes_within_bound`; repo
  tests `test_accepts_deep_acyclic_chain`,
  `test_accepts_shared_dag_without_blowup`,
  `test_reject_cycle_in_large_graph`.
- Gate certifies ImportError (fixture with injected
  `raise ImportError` still passed the whole integrity gate,
  exit 0). Fix: `suite_failure_is_bug_proof` requires executed
  tests and no import failure. Sources: S27 (exit conflates
  errors/failures), S28 (import failures excluded from
  fail-to-pass). Proof: hard-test
  `test_integrity_does_not_count_import_error_as_bug_proof`;
  gate step 11 `check_failure_classification`.
- Judge accepts lax verdicts, crashes on malformed ones, and
  promotes exit-7 output (extra ids and `True` scores passed;
  `plants=[2]` raised AttributeError; fake CLI exit 7 with valid
  JSON exited 0). Fix: exact allowlist, `type(x) is int`,
  type-checked traversal returning error lists, nonzero exit
  recorded as execution failure. Sources: S29 (`True == 1`),
  S30 (closed objects; bool≠int), S31 (allowlist validation),
  S32 (CWE-20 classification). Proof: hard-tests
  `test_judge_nonzero_exit_cannot_be_success`,
  `test_judge_rejects_extra_ids_and_boolean_scores`,
  `test_judge_malformed_scores_return_errors_not_crash`; repo
  class `JudgeRunnerContract` (5 tests).

Verification record (observed, Python 3.14.7; audit manifest
pins 3.12): hard-tests 14/14 (was 3/14); full baseline battery
177/177 across 16 commands (was 163, +14 regressions);
integrity gate green; study metrics recomputed bit-identical to
the delivered `recomputed-metrics.json`.

## Alternatives

- Reject-on-drift (raise IntegrityError on metadata change)
  instead of retain-as-revision: rejected. The dirty-state probe
  requires `put` to succeed and the new state to be readable;
  explicit records beat rejection, and content drift already had
  the failed-version precedent.
- Keep ends-semantics for `get(expected=)` (raise whenever
  history advanced): rejected. It contradicts the pinned read
  surfacing the latest observation; contains-semantics still
  detects truncation and rollback, which is what the pin is for.
- Carry digest conflicts as defeaters instead of refusing:
  rejected. A shared digest with contradictory integrity is a
  structural merge failure like an id collision, and the
  fail-closed precedent (S25) plus the collision path already
  existed.
- Reject any suite output containing `errors=`: rejected.
  Case-i's TypeError is raised by the candidate under test and is
  genuine bug proof; only loader failures (ImportError, zero
  executed tests) are excluded.

## Tradeoffs

- All `dir_hash` values change. Frozen runs under `evals/runs/`
  keep their old hashes as historical records; no test compares
  fresh hashes against frozen ones, so nothing was migrated. Any
  future consumer that pins a `dir_hash` must re-pin once.
- The gate is stricter by design: suites that used to "fail
  correctly" via import breakage now fail the gate. That red is
  the intended signal.
- The integrator refuses more merges (digest conflicts).
  Refusals are fail-closed and carry named defeaters; fragment
  producers sharing digests across different integrity states
  must fix their digests.
- Pinned reads no longer alert on history advance. Callers that
  need advance notice must compare digests themselves; the pin
  now guards rollback/truncation only. This is documented in
  `evidence.py`.

## Source IDs

S20–S32 per `references/source-registry.yaml`, traced to
tooling rules `evidence-store-001`, `assurance-integrator-001`,
`shared-envelope-001`, `assurance-checker-001`,
`eval-harness-001`, `judge-runner-001` in
`references/traceability.yaml`. New enum values introduced:
rule `status` = `implemented`, `test_status` =
`implemented_contract_tests` (these rules ship with passing
contract tests, unlike the `design_requirement` rules they sit
beside). `assurance-checker-001` intentionally has an empty
basis: iterative DFS is standard practice, consulted but not
normatively sourced.

Consulted but not normative (mechanism transfer or scope notes,
exact pages read 2026-09-22): NIST AI RMF
(<https://www.nist.gov/itl/ai-risk-management-framework>),
OWASP AISVS model-validation-testing
(<https://github.com/owasp/aisvs/blob/HEAD/1.0/research/chapters/C03-Model-Lifecycle-Management/C03-02-Model-Validation-Testing.md>),
pytest exit codes
(<https://docs.pytest.org/en/stable/reference/exit-codes.html>),
NIST fail_safe glossary
(<https://csrc.nist.gov/glossary/term/fail_safe>), rule of three
and binomial CI
(<https://en.wikipedia.org/wiki/Rule_of_three_(statistics)>,
<https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval>),
NIST Dataplot propconf
(<https://itl.nist.gov/div898/software/dataplot/refman1/auxillar/propconf.htm>),
NIST/SEMATECH handbook PRC 6.2.2
(<https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm>),
ISTQB STE syllabus
(<https://istqb.org/wp-content/uploads/2025/02/ISTQB_STE_Syllabus_v1.0.pdf>).

## Confidence and uncertainty

High confidence in the six contract fixes: each is executable
from both sides (a probe that failed before and passes now, plus
permanent repo regressions). Medium confidence in the "8 causes"
taxonomy: causes 4/5 share one file and function, so 7 causes is
an equally defensible count; the fix set is unaffected either
way.

Not verified in this pass: full re-execution under the
manifest's Python 3.12 (local runs used 3.14.7); callers of
`Store.put` beyond the test suites and historical-receipt
migration; impact review of frozen runs beyond hash-shape
compatibility; the n32 DAG timeout itself (extrapolated from
n12/22/25/27 measurements); fixture-clustering audit behind the
study metrics; one prior-report claim left unvalidated after a
stalled validation child (judge ignoring nonzero exit — covered
instead by the hard-test, now passing).

## Reversal conditions

Revisit if: a pinned-hash consumer needs ends-semantics back
(restore it as an opt-in strict mode, keeping contains as the
default); a legitimate same-digest/different-kind pair appears
in production fragments (narrow the conflict rule to integrity
only, with a recorded defeater for kind drift); the
length-prefix migration cost materializes for a downstream
pinner (ship a migration map old→new for affected fixtures).
Record revisions with migration rules; never silently
reinterpret existing records.
