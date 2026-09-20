Study A (generic reviewer, no skill) — arch-b

Scope: `api/` in candidate vs repo per `tests/arch-cases/arch-b/request.md`. Objective stated: faster order-total reads.

Conformance criteria (established from repo BEFORE judging candidate):
- `tests/arch-cases/arch-b/repo/docs/ARCH.md`: Layers `api/ -> service/ -> store/`; Rule D1: `api/` MUST NEVER import `store/`; all data access via `service/`. Reason: every read is audited in service layer.
- `tests/arch-cases/arch-b/repo/service/order.py`: `total()` appends to `AUDIT` then calls `db.get()` — audit is the enforced side effect.
- `tests/arch-cases/arch-b/repo/api/orders.py`: delegates to `service.order.total()` — compliant baseline.

Candidate changes (diff repo vs candidate):
1. NEW `candidate/api/fast_path.py`: `from store import db` and `db.get(order_id)` directly. Docstring admits intent: "skip the service layer, read the store directly (2x faster)".
2. `candidate/tests/test_api.py` switched from `api.orders` to `api.fast_path` — test now exercises the bypass path.
3. `candidate/api/orders.py`, `candidate/service/order.py`, `candidate/store/db.py`, `candidate/docs/ARCH.md` unchanged.

Findings:
- F1 (Rule D1 violation): `candidate/api/fast_path.py:2` imports `store` from `api/`, directly forbidden by `repo/docs/ARCH.md` Rule D1.
- F2 (Audit bypass): `fast_path.total()` skips `service/order.py:7` `AUDIT.append`, defeating the stated reason for D1.
- Tests: ran `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=candidate python3 -m unittest discover` — 1 test passes, but it only asserts the return value (100), not layering or audit. Functional pass does not cure the architectural violation.

Decision: The performance gain is achieved by the exact mechanism the architecture forbids. Reject / rework to keep reads through `service/` (e.g., optimize inside service/store, add caching with audit preserved).

Verdict: Violates
