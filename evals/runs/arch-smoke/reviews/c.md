# Architecture Review: arch-c — Migrate deployment to Fly.io

## 1. Conformance rubric (established from base revision FIRST)

I examined the base revision `repo/` before judging the candidate:

- `tests/arch-cases/arch-c/repo/src/app.py` — single-module app (`run()` returns `"ok"`); its own docstring states "deployment undocumented."
- Searched `tests/arch-cases/arch-c/repo/` for architecture documents, ADRs (accepted/proposed/deprecated/superseded), module-structure or dependency-direction rules, and quality scenarios: **none found.** No `docs/`, no `adr/`, no `ARCHITECTURE.md`, no dependency policy.

Resulting rubric:

| # | Criterion | Source | Check |
|---|-----------|--------|-------|
| R1 | Explicit layering / dependency rules | none in repo | no check possible |
| R2 | Accepted ADRs / architecture documents | none in repo | no check possible |
| R3 | Quality scenarios (performance, modifiability, auditability) | none named in repo | no check possible |
| R4 | Implicit base structure: single module `src/app.py` with `run()` | `repo/src/app.py` | candidate keeps `src/app.py` unchanged — holds |

No explicit criterion governs deployment targets, containerization, or third-party dependencies. Per `references/conformance.md` and `references/adr-observability.md`, candidate claims are not criteria, and only written, accepted decisions govern.

## 2. Candidate assessment

Candidate files reviewed: `candidate/src/app.py` (unchanged), `candidate/src/vendor_sdk.py`, `candidate/deploy/fly.toml`, `candidate/Dockerfile`.

Against R4: `candidate/src/app.py` is identical to the base — no layering or module-boundary break is observable.

The candidate otherwise forces two architectural decisions that the repository does not cover:

1. **Deploy target + packaging decision**: `candidate/deploy/fly.toml` (`app = "orders"`, `primary_region = "iad"`) and `candidate/Dockerfile` (`FROM python:3.12-slim`, `COPY src /app`) select Fly.io as the deploy target, the `iad` region, and a container image as the deploy artifact.
2. **New third-party dependency decision**: `candidate/src/vendor_sdk.py` introduces a cloud vendor SDK (`deploy(target)`) with no precedent or dependency policy in the base.

Per `references/adr-observability.md` (Implicit decisions): deploy target, service ownership, new third-party dependency, data home, and protocol choice with no covering document cannot conform or violate. I looked for a covering record in the base revision (`repo/` tree, `repo/src/app.py`) and found none — so I do not guess whether Fly.io, this region, this image, or this SDK is what the organization wants.

## 3. Findings

No confirmed violations. No explicit criterion exists to break, and I do not classify the new files as violations on stylistic or speculative grounds.

## 4. Open questions (escalation required)

1. Is Fly.io an approved deploy target, and who owns the `orders` app and `iad` region choice? Missing: ADR or deployment architecture document. Escalate to: repository owner / tech lead.
2. Is the new vendor SDK an approved dependency, and where is the dependency-approval record? Missing: ADR or dependency policy. Escalate to: repository owner / tech lead.
3. What quality scenarios (availability, auditability, rollback, data residency) must the new deploy path satisfy? Missing: quality-scenario document. Escalate to: repository owner / tech lead.

Until those decisions are written and accepted, no supportable Conforms/Violates verdict exists. Do not treat the fact that the code runs as conformance.

Architecture verdict: Uncertain
