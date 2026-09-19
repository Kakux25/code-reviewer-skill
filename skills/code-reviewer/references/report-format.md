# Review Report

Use the format required by the user or project, if one exists. Otherwise, include the following elements with an appropriate level of detail:

1. **Decision**: `Changes requested`, `No actionable findings`, or `Incomplete`, with the decisive reason. These are review conclusions, not authorization to merge or deploy. If findings exist and coverage is also incomplete, use `Changes requested` and explicitly mark the coverage as partial.
2. **Findings by priority**: title, file and verified lines, triggering condition, consequence, evidence, and the smallest proposed fix. Distinguish execution results from static deductions and indicate high or medium confidence. Weak hypotheses belong under open questions, not findings.
3. **Architecture**: change type, base revision, rubric version, axes with evidence, explicit gaps, architectural verdict, and rationale. Include complexity only if assessed. A brief rubric in the report is sufficient; a YAML file is not required.
4. **Soul**: essence source, statements with the verdict for each, soul verdict, and rationale.
5. **Verification and limitations**: checks actually run and their results, static review, files outside the scope, missing context, and outstanding checks.

## Brief Format

Default to the brief format for bounded reviews; use the full format above
when the user or project requires it, or when a finding needs extended
rationale (complex causality, disputed verdicts, or audit traceability).
The brief report keeps every decision-relevant element and moves the
detailed rubric to an annex only when useful:

1. **Decision**: verdict plus the single decisive reason.
2. **Findings**: one line each — priority, file:line, cause, and proof
   (execution result or cited evidence). Smallest fix inline where trivial.
3. **Verdicts**: architectural and soul verdicts, one line each with the
   decisive axis or statement.
4. **Checks and limits**: commands run with results; scope gaps in one line
   each. Never omit a failed or skipped check.

Brevity must not drop evidence: cause, line, proof, and decision are
mandatory in both formats.

## Finding Priorities

- `P0`: an immediate, critical consequence supported by evidence, such as data loss or active exposure.
- `P1`: a severe regression or violation of an essential contract that must be fixed before accepting the change.
- `P2`: a concrete defect with limited impact that requires correction.
- `P3`: a minor, actionable improvement, clearly distinguished from blocking issues.

Priority reflects impact and triggering conditions, not author type, diff size, or the architectural complexity label. An architectural finding also requires a concrete consequence; “violates SOLID” is not sufficient.

Calibration anchors (all verifiable in `tests/review-cases`): the case-A
discount divisor is P1 (every nonzero input corrupts totals); the case-D
filesystem write is P1 (breaks the documented memory-only contract); the
case-D write-only cache is P2 (real waste and unmet objective, contained
impact, no corruption); the case-C `None` hypothesis is an open question,
not a finding (no contract to judge it against). When the same defect
class could be P1 or P2, trigger breadth decides: broad, hard-to-avoid
triggers push toward P1; narrow, easily avoided ones stay P2.

## Final Consistency Check

Check that every reference points to the correct revision: base, candidate, or local working tree. Use diff lines where possible; if the evidence is in an unchanged caller, identify both locations. Do not invent line ranges or links.

`High` requires an empty gap list; `High with concerns` requires a nonempty gap list with no primary-axis violations. `Acceptable` and `Low` require evidence on a primary axis. A functional bug in a patch with a `High` architectural verdict remains a valid reason for `Changes requested`.

`Betrayed` requires a quoted essence statement plus candidate evidence; `Unverifiable` is not a pass.

`No actionable findings` means that no actionable defects were identified within the reviewed scope. If decisive context or checks are missing, use `Incomplete`. Omitting a nondecisive check does not automatically invalidate a review: explain its actual effect on confidence.

For tools that require structured data, you may represent the same elements in JSON or YAML: `scope`, `rubric`, `findings`, `architecture`, `soul`, `checks`, `limitations`, `decision`. Keep the structured output consistent with the written assessment.
