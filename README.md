# Code Reviewer

A reusable skill for reviewing code changes against repository evidence, regardless of author. It evaluates functional correctness and architectural conformance separately, producing prioritized findings with verifiable code locations.

## What it reviews

- Bugs, regressions, and broken contracts introduced or worsened by a change.
- Architectural boundaries, repository conventions, and effects beyond the diff.
- Essence preservation: whether the change keeps the project's documented spirit (soul verification).
- Test evidence, review coverage, and unresolved questions.

Each review includes an overall decision, actionable findings, an architectural rubric and verdict, a soul verdict, verification results, and limitations. A `High` architectural verdict does not establish functional correctness or authorize a merge.

## Installation

Copy any `skills/<name>` directory into your coding assistant's user-level skills directory. Review any existing installation before replacing it, then start a new task to load the skill.

Each skill consists of Markdown instructions only and works in any harness that loads `SKILL.md`. Skills use Git and project test runners when relevant and available. No additional services or API credentials are required.

| Skill | Reviews |
| --- | --- |
| [code-reviewer](skills/code-reviewer/SKILL.md) | Defects, regressions, architecture conformance, documented essence |
| [architecture-reviewer](skills/architecture-reviewer/SKILL.md) | Fit to the repo's own documented architecture (layers, ADRs, quality scenarios) |
| [safety-stpa-reviewer](skills/safety-stpa-reviewer/SKILL.md) | Safety via systems thinking (losses, hazards, control structure, UCAs) |
| [incident-memory](skills/incident-memory/SKILL.md) | Structured incident precedents, transfer by mechanism |
| [system-dynamics-reviewer](skills/system-dynamics-reviewer/SKILL.md) | Feedback loops, stocks/flows, delays, stability under load |
| [sociotechnical-reviewer](skills/sociotechnical-reviewer/SKILL.md) | Coordination coverage (handoffs, ownership freshness, escalation) |

## Usage

In a task with access to the target repository:

```text
Use $code-reviewer to review the local changes.
The goal is to fix discount calculations. Do not modify the code.
```

You can also specify a pull request, commit range, or individual files. To focus a review:

```text
Use $code-reviewer on this pull request. Prioritize public contracts
and error handling. If context is missing, report partial coverage explicitly.
```

Harnesses with automatic skill selection may pick it up on matching review requests. Explicit invocation through `$code-reviewer` is also supported. Reviews follow the user's language. Code changes and publication of review comments must be part of the user's request.

A helper script ships with the skill: `skills/code-reviewer/scripts/trace_callers.py SYMBOL ROOT` lists definitions and call sites for a Python symbol (standard library only, read-only). Treat its output as review leads, not proof.

## Documentation

| Resource | Purpose |
| --- | --- |
| [Skill instructions](skills/code-reviewer/SKILL.md) | Review workflow and scope |
| [Architectural assessment](skills/code-reviewer/references/architecture.md) | Rubric construction and verdict rules |
| [Soul verification](skills/code-reviewer/references/soul.md) | Essence statements and soul verdicts |
| [Report format](skills/code-reviewer/references/report-format.md) | Findings, priorities, and reporting |
| [Evaluation cases](tests/README.md) | Reproducible examples for checking reviewer behavior |

## License

MIT — see [LICENSE](LICENSE).

## Engineering Assurance Foundation

The [design foundation](docs/assurance/README.md) specifies the six reviewer skills above plus a shared evidence envelope and an assurance integrator. All six skills are implemented with fixtures: the five specialists with live smoke runs (4/4 each), code-reviewer with a 22-case battery (a–v) plus a with/without-skill comparison. The shared envelope, assurance integrator, judge protocol, and a controlled A/B/C/D comparative study with independent re-grading (K-2/K-3) are recorded as frozen runs under [evals/runs/](evals/runs/). The code-reviewer keeps its standalone contract; in composed mode, architectural judgment routes to the architecture specialist. Nothing here grants integration or deployment permission.

Validate the synthetic assurance record and run the contract tests:

```sh
uv run --with-requirements requirements-dev.txt python scripts/validate_assurance.py examples/assurance/insufficient-evidence.json
uv run --with-requirements requirements-dev.txt python -m unittest discover -s tests/contracts -v
```

Contract validation checks data structure and selected consistency constraints. It does not prove engineering claims or grant integration or deployment permission.
