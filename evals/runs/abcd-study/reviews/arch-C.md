Studied arch-b as architecture-reviewer (blind, did not open expected.json).

Skill: skills/architecture-reviewer/SKILL.md + references/conformance.md + references/adr-observability.md.

Rubric (from repo, before judging candidate):
- C1 (explicit, repo/docs/ARCH.md Rule D1): layers api/ -> service/ -> store/; api/ MUST NEVER import store/; all data access via service/. Check: grep imports in candidate api/.
- C2 (explicit reason in same doc): every read is audited in the service layer (repo/service/order.py AUDIT.append). Check: candidate reads still flow through service audit.
- C3 (structure, base revision): repo/api/orders.py delegates to service/order.total; no api->store edge exists in base. Check: no new dependency edges/cycles.

Candidate review (scope api/):
- Finding 1: candidate/api/fast_path.py:2 `from store import db` breaks C1 directly — a new api->store edge the architecture forbids. The "2x faster" comment is a claim, not an amendment; per adr-observability, hold the line.
- Finding 2: candidate/api/fast_path.py:4-5 `total()` calls db.get directly, bypassing service/order.total audit (C2). Base behavior silently dropped: AUDIT entries. Candidate/tests/test_api.py now exercises fast_path instead of orders, so the suite passes while hiding the damage — local success, global damage.
- No conforming correction smaller than: route fast_path through service (or delete it and keep api/orders.py delegation); if perf requires bypass, amend ARCH.md Rule D1 through its own process first.

Both suites pass read-only (PYTHONDONTWRITEBYTECODE=1, `python3 -m unittest tests.test_api`): candidate 1/1 OK, repo 1/1 OK. Passing tests do not rescue the violation.

Architecture verdict: Violates
