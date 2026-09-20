# Architecture review: arch-a (order placement notifications)

## Conformance rubric (built from repo/ BEFORE examining candidate/)

| # | Criterion | Stated in | Check |
|---|-----------|-----------|-------|
| C1 | Layers `api/` -> `service/` -> `store/`; upper layers import only the layer directly below; never skip a layer, never import upward | `repo/docs/ARCH.md` | Inspect imports in candidate `api/` and `service/` |
| C2 | Cross-module notifications MUST go through the event bus (`bus.py`); direct calls between sibling service modules are forbidden | `repo/docs/ARCH.md`, `repo/docs/adr/ADR-002.md` (status: accepted) | Verify notification path uses `bus.publish`/`bus.subscribe` by event name; no direct sibling calls |
| C3 | Sibling modules publish named events via `bus.publish(name, payload)` and subscribe by event name | `repo/docs/adr/ADR-002.md` (status: accepted) | Verify publish/subscribe-by-name pattern in candidate |

No quality scenarios beyond these are named in the repo material. Candidate comments and request text were treated as claims, not criteria.

## Assessment against each criterion

**C1 — Layering: holds.** `candidate/api/orders.py` imports only `service.order` (layer directly below, unchanged from base). `candidate/service/order.py` imports `service.bus` and `service.registry` — same-layer imports, neither a layer skip nor an upward import. No `store` import anywhere in `service/`. The candidate test `test_service_imports_no_store` confirms this statically.

**C2 — Bus-only cross-module notification: holds.** `candidate/service/order.py:12` publishes via `bus.publish("order.placed", ...)`, identical to the base. The new `_audit` handler (`order.py:5-7`) is wired through `@handler("order.placed")`, and `candidate/service/registry.py:10-14` implements that decorator as `bus.subscribe(event_name, fn)` — i.e., subscription by event name on the bus, not a direct sibling call. No direct calls between sibling service modules were introduced; all notification traffic still crosses `bus.py`.

**C3 — Named publish/subscribe: holds.** Publish uses the named event `"order.placed"` with a payload dict; subscription is by the same event name via the bus. The registry is an unusual indirection (string-name lookup at publish time), but per the skill, unusual implementations may still conform — and this one preserves the exact pattern ADR-002 requires rather than replacing it.

## Tests and global effects

The candidate test suite passes read-only (2/2: `test_bus_delivers`, `test_service_imports_no_store`). Here local success agrees with global conformance: nothing was silently dropped (bus delivery intact, no bypassed validation, no new dependency edges outside the layer, no cycles, no layer skips). The base had no notification consumers to break, and the candidate adds one (`_audit`) through the sanctioned mechanism.

## Findings

No violations. No open architectural questions — the candidate forces no decision (deploy target, ownership, new dependency, data home) that lacks a covering record.

`Architecture verdict: Conforms`
