# Evaluation Cases

These fixtures exercise reviewer behavior across proposals of different quality. They are not a test suite in which every candidate is expected to pass.

To evaluate the skill, start an independent task, invoke `$code-reviewer`, and ask it to complete each `review-cases/case-*/request.md`. The reviewer should read the base and establish criteria before opening the candidate. Expected outcomes live in [EXPECTED.md](EXPECTED.md) — open it only after the review is complete.

Machine-readable answer keys (`review-cases/case-*/answer-key.json`), the mechanical grader, pre-declared thresholds, and the deterministic CI gate live in [../evals/](../evals/). The same blindness rule applies: an agent under evaluation must never read the keys.

Cases A, B, and D include Python tests with no external dependencies. Run them from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests/review-cases/case-a/candidate python3 -m unittest discover -s tests/review-cases/case-a/tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests/review-cases/case-b/candidate python3 -m unittest discover -s tests/review-cases/case-b/tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests/review-cases/case-d/candidate python3 -m unittest discover -s tests/review-cases/case-d/tests -v
```

| Case | Materials (no outcomes — see EXPECTED.md after review) |
| --- | --- |
| A | Proposal + acceptance suite |
| B | Proposal + acceptance suite |
| C | Isolated snippet, no repository |
| D | Proposal + passing suite + essence doc |
