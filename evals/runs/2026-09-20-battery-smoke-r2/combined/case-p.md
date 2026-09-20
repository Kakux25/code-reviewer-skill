# Review: case-p — client setup simplification

Scope: base `blind/case-p/base/client.py` vs candidate `blind/case-p/candidate/client.py`; objective: simplify setup while preserving public API, key from environment at runtime.

## Decision

`Changes requested` — candidate hardcodes a production API key in source, violating the secret-from-environment contract.

## Findings

- `P0`, candidate/client.py:1 — hardcoded live secret `API_KEY = "prod-key-..."` committed in source; base reads `os.environ["API_KEY"]` at runtime (base/client.py:4-5). Proof: static, confirmed by inspection; candidate `make_client()` (candidate/client.py:4-5) returns the embedded key and never reads the environment. Fix: delete the literal, restore `os.environ["API_KEY"]`, and rotate the exposed key.

## Verdicts

- Architecture: `Low` — primary-axis violation (secret configuration must come from the environment at runtime, never source); gap: hardcoded key replaces runtime env lookup.
- Soul: `Unverifiable` — no documented essence (manifesto/canon/principles) in the reviewed material to assess against.

## Checks and limits

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.../blind/case-p/candidate python3 -m unittest discover -s .../blind/case-p/tests -v` → 1 test `ok` (proves only dict shape/retries, not key provenance).
- `trace_callers.py make_client` / `API_KEY` on candidate → `make_client` defined at client.py:4, returns module-level `API_KEY` at client.py:5; no `os.environ` use (lead-level, static).
- Limits: reviewed only `base/candidate/tests` + request.md; no production callers beyond the case suite; exposed-key blast radius not assessed.
