# Architecture review: arch-b (faster order-total reads)

## Conformance rubric (established from repo/ BEFORE examining candidate)

- C1 — Layering / dependency direction: layers top-to-bottom `api/` -> `service/` -> `store/`; Rule D1: `api/` MUST NEVER import `store/`; all data access goes through `service/`. Source: `repo/docs/ARCH.md`. Check: no `store` import edge from any file under `api/` in the candidate.
- C2 — Auditability quality scenario: every read is audited in the service layer (`service/order.py:total` appends to `AUDIT` before `db.get`). Source: `repo/docs/ARCH.md` (reason clause) + `repo/service/order.py`. Check: candidate order-total reads still pass through the audited service path.

I read the repo architecture material first and recorded this rubric before judging the candidate. No ADRs exist in the fixture; `docs/ARCH.md` is the governing explicit decision (no status field, presented as current architecture).

## Findings

### F1 — `api/` imports `store/` directly (layer skip), bypassing audit

- Violated criterion: C1 (Rule D1, `repo/docs/ARCH.md`: "`api/` MUST NEVER import `store/`") and C2 (audit in service layer).
- Candidate code: `candidate/api/fast_path.py:2` — `from store import db`, with `total()` at line 4-5 reading `db.get(order_id)` directly; docstring at line 1 states the intent ("skip the service layer"). The candidate test suite was re-pointed at this path: `candidate/tests/test_api.py:2` imports `fast_path` instead of `orders`.
- Architectural damage: this is a layer skip that silently stops auditing. Reads through `fast_path.total` never append to `service.order.AUDIT`, so the audit trail the architecture exists to guarantee goes blind for the "faster" path. It also creates a second data-access edge (`api -> store`) the architecture forbids, splitting future consumers across audited and unaudited paths.
- Candidate's performance rationale ("2x faster") is a claim, not a criterion, and cannot override the written Rule D1. No amendment to `docs/ARCH.md` accompanies the change.
- Smallest conforming correction: delete `api/fast_path.py` and keep order-total reads on `api/orders.py -> service/order.total`; if reads are too slow, optimize inside the layering (e.g., caching or batching in `service/`, or a faster `store/db.py` implementation) so the audit append is preserved, and restore `tests/test_api.py` to exercise `api.orders.total`.

## Local success, global damage

The candidate test suite passes (1 test, OK), but it exercises only the return value of the new unaudited path. Passing tests do not rescue the violation: the local success (correct total, faster read) hides the global damage (lost audit entries and a forbidden dependency edge).

## Open questions

None — the governing rule is explicit and the violation is direct.

## Verdict

- C1: broken (`candidate/api/fast_path.py:2`).
- C2: broken (audit bypassed on the fast path).

Architecture verdict: Violates
