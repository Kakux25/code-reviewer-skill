# Architecture

Layers, top to bottom: `api/` -> `service/` -> `store/`.
Rule D1: `api/` MUST NEVER import `store/`; all data access goes
through `service/`. Reason: every read is audited in the service layer.
