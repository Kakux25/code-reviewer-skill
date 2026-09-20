# Security Policy

This is experimental research software (evidence-grounded review skills
plus an eval harness). It is published for inspection and reuse, not as
a production assurance product.

- Supported versions: `main` only. No LTS, no backports, no SLA.
- Dependencies: one direct Python pin (`requirements-dev.txt`); the
  transitive graph resolves at install time and has no SBOM or scanner
  yet — do not assume it is vulnerability-free.
- If you find a vulnerability: open a public issue describing it. There
  is no private disclosure channel and no guaranteed response time.
- Scope notes: review outputs never authorize merges, deploys, or
  compliance claims (see `SKILL.md` and `docs/assurance/`). A skill that
  reads untrusted patches inherits prompt-injection exposure from its
  host harness — run reviews with least-privilege tool permissions.
