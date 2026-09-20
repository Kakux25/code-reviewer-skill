# Case P — code review (brief)

Scope: base `client.py` vs candidate `client.py`; objective "simplify client setup while preserving the public API"; acceptance examples in `tests/test_client.py`. Correctness and architecture assessed separately. Rubric v1 frozen from the base before examining the candidate.

## Decision

`Changes requested` — the candidate hardcodes a production API key in source, violating the base's documented never-from-source contract and exposing the credential.

## Findings

- `P0` (high confidence) — candidate/client.py:1: `API_KEY = "prod-key-..."` hardcodes a secret in source; base/client.py:4 reads `os.environ["API_KEY"]` at runtime per base/ARCHITECTURE.md:3-5 ("must come from the environment at runtime, never from source code"). Execution proof: with `API_KEY=env-override-123`, candidate/client.py:5 returns the hardcoded prod key while the base returns `env-override-123`; environment configuration is silently ignored. Fix: delete the module constant, restore the `os.environ["API_KEY"]` lookup, and rotate the exposed key. (Single root cause; no other callers per trace.)

## Verdicts

- Architecture: `Low` — change type: refactoring; primary axis A1 (secret from environment at runtime, never source; base/ARCHITECTURE.md:3-5, base/client.py:4) violated with gap at candidate/client.py:1; secondary axis A2 (public `make_client()` shape `{api_key, retries: 3}`) preserved.
- Soul: `Unverifiable` — no manifesto, canon, or principles essence is documented (ARCHITECTURE.md states an architectural contract, not project essence); nothing to assess against.

## Checks and limits

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=blind/case-p/candidate python3 -m unittest discover -s blind/case-p/tests -v` → 1 test OK; covers return shape only, not secret sourcing.
- Env-override probes (execution): candidate returns the hardcoded prod key despite `API_KEY=env-override-123`; base returns the env value.
- `trace_callers.py make_client` / `API_KEY` over blind/case-p → sole caller is tests/test_client.py:7; the key is referenced only in candidate/client.py:5.
- Limits: reviewed only the skill, request.md, base, candidate, and case tests; no git history or external consumers; key-rotation status unknown.
