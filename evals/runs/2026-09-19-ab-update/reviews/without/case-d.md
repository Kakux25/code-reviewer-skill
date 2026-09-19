# Review: case-d — persistent read cache for in-memory store

Scope: candidate vs base (objective: speed up reads with a persistent cache). Rubric disclosure: the diff was seen before the rubric was frozen; every criterion below was checked against the base revision, not derived from the patch.

## Decision

**Changes requested** — the candidate writes every `put` to the filesystem, breaking the documented memory-only contract.

## Findings

- P1, candidate/store.py:11,18-19 — `put` creates a temp dir (`mkdtemp`) and writes each value to a file, breaking the memory-only contract (base/PHILOSOPHY.md:3); proof: static (`open(..., "w")` + `fh.write`) corroborated by tests/test_store.py:10 cleaning up `store._cache_dir`. Fix: remove the filesystem cache; keep state in `self._data` only.
- P1, candidate/store.py:16-17 — `put` raises `ValueError` for any key outside `[A-Za-z0-9_-]+`, rejecting keys the base accepted (e.g. `"a.b"`, keys with spaces); proof: static vs base/store.py:7-8, which stores any key unconditionally. Fix: drop the regex gate.
- P2, candidate/store.py:21-22 — `get` never reads the cache, so the stated objective (faster reads) is unmet and all cache writes are pure waste plus leaked temp dirs; proof: static (`get` touches only `self._data`). Fix: same as above — remove the write-only cache.

## Verdicts

- Architecture: `Low` — primary-axis violation: state escapes process memory to the filesystem (boundary crossing against base store.py:1-11 + PHILOSOPHY.md:3); second primary gap: `put` narrows the arbitrary-key contract. Change type: feature addition; rubric v1.
- Soul: `Betrayed` — S1 "Memory-only: this package never touches the filesystem" betrayed by candidate/store.py:11,18-19; S2 "Honest API: ... no hidden side effects" betrayed by the hidden file write and unexpected `ValueError` in `put` (source: base/PHILOSOPHY.md:1-4).

## Checks and limits

- Ran `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=candidate python3 -m unittest discover -s tests -v` → OK (1 test); it exercises only an alphanumeric roundtrip, so it cannot confirm the broken cases above.
- Static review of base/store.py, candidate/store.py, base/PHILOSOPHY.md, tests/test_store.py; no execution beyond the suite.
- Limits: single-file package, no other callers or docs to trace; no performance measurement (moot — the cache is never read).
