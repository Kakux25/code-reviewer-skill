# Code Reviewer

A reusable skill for reviewing code changes against repository evidence, regardless of author. It evaluates functional correctness and architectural conformance separately, producing prioritized findings with verifiable code locations.

## What it reviews

- Bugs, regressions, and broken contracts introduced or worsened by a change.
- Architectural boundaries, repository conventions, and effects beyond the diff.
- Essence preservation: whether the change keeps the project's documented spirit (soul verification).
- Test evidence, review coverage, and unresolved questions.

Each review includes an overall decision, actionable findings, an architectural rubric and verdict, a soul verdict, verification results, and limitations. A `High` architectural verdict does not establish functional correctness or authorize a merge.

## Installation

Copy `skills/code-reviewer` into your coding assistant's user-level skills directory. Review any existing installation before replacing it, then start a new task to load the skill.

The skill consists of Markdown instructions only and works in any harness that loads `SKILL.md`. It uses Git and project test runners when relevant and available. No additional services or API credentials are required.

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

Automatic selection is enabled by default. Explicit invocation through `$code-reviewer` is also supported. Reviews follow the user's language. Code changes and publication of review comments must be part of the user's request.

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
