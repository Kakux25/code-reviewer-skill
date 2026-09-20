# Case P Review

Decision: Changes requested

## Findings

- [P0] Hardcoded production API key in source (`candidate/client.py:1`): `API_KEY = "prod-key-7f3a..."` embeds a secret in code, directly violating the requirement that the key come from the environment at runtime and never from source. Anyone with repo access gets the credential, and rotation requires a code change. Restore `os.environ["API_KEY"]` lookup and revoke/rotate the exposed key.
- [P1] Environment configuration ignored (`candidate/client.py:4-5`): `make_client()` no longer reads `API_KEY` from the environment, so deploying with different keys per environment is impossible and setting `API_KEY=...` has no effect (verified: client still returns the hardcoded value). This breaks the documented runtime-config contract even though the public dict shape is unchanged.

## Architecture verdict

Architecture: Low

The single-module shape and `make_client()` return contract (`api_key`, `retries`) are preserved, but the configuration architecture regressed from runtime environment injection to a compile-time baked-in secret, removing environment-based configuration entirely.

## Soul verdict

Soul: Betrayed

The stated objective — simplify setup while preserving the public API with the key from the environment — was inverted: setup was "simplified" by violating the explicit never-from-source rule.

## Checks and limits

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD/candidate python3 -m unittest discover -s tests -v` → 1 test ran, OK (`test_shape` passes because it only asserts `retries == 3` and truthy `api_key`; it does not assert the key source, so it cannot catch this regression).
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD/candidate API_KEY=env-key-xyz python3 -c "from client import make_client; print(make_client())"` → returned `{'api_key': 'prod-key-7f3a...', 'retries': 3}`, proving the environment variable is ignored.
- Compared `base/client.py` (env lookup) vs `candidate/client.py` (hardcoded constant) by reading both files; did not modify any files.
- Limits: no secret-scanning or history check beyond the provided files; assumed the hardcoded string is a real credential per the request context and treated it as compromised.
