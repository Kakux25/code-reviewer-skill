# Evaluation Cases

These fixtures exercise reviewer behavior across proposals of different quality. They are not a test suite in which every candidate is expected to pass.

To evaluate the skill, start an independent task, invoke `$code-reviewer`, and ask it to complete each `review-cases/case-*/request.md`. The reviewer should read the base and establish criteria before opening the candidate. Do not provide expected outcomes until the review is complete.

Cases A, B, and D include Python tests with no external dependencies. Run them from the package root:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests/review-cases/case-a/candidate python3 -m unittest discover -s tests/review-cases/case-a/tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests/review-cases/case-b/candidate python3 -m unittest discover -s tests/review-cases/case-b/tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests/review-cases/case-d/candidate python3 -m unittest discover -s tests/review-cases/case-d/tests -v
```

| Case | Review behavior |
| --- | --- |
| A | Identify a functional defect while assessing architecture separately. The candidate is intentionally defective, so its failing tests do not indicate a broken skill package. |
| B | Accept an alternative implementation that preserves the required architectural property. |
| C | Report insufficient architectural evidence when only an isolated snippet is available. |
| D | Flag a soul betrayal in a candidate whose tests pass, keeping function and essence separate. |
