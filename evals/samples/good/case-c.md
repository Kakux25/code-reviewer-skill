# Sample review: case-c (GOOD — synthetic, for grader self-test)

**Decision**: No actionable findings — only an isolated snippet is available, with no repository, no base revision, and no contract to judge it against; the architecture gap is recorded below and cannot change the findings.

**Findings**: none. snippet.py defines normalize_name over strip/lower; locally consistent.

**Open questions**: passing None would raise AttributeError — but with no contract specifying the accepted input domain, this stays a question, not a finding.

**Verdicts**: architectural `Insufficient evidence` (no repo, no base, no rubric possible); soul `Unverifiable` (no essence document in scope).

**Checks and limits**: static read of the single file only. No tests exist to run.
