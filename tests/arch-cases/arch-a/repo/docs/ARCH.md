# Architecture

Layers, top to bottom: `api/` -> `service/` -> `store/`.
Upper layers import the layer directly below; never skip a layer,
never import upward.

Cross-module notifications MUST go through the event bus (`bus.py`).
Direct calls between sibling service modules are forbidden.
See ADR-002.
