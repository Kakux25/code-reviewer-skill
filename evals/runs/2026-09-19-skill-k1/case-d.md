# Review: persistent read cache for Store (case-d)

Scope: `base/store.py` vs `candidate/store.py`; essence `base/PHILOSOPHY.md`; suite `tests/test_store.py`. Objective: speed up reads with a persistent cache.

## 1. Decision

**Changes requested** — every `put` writes to the filesystem, breaking the documented memory-only contract (P1), while reads never consult the cache, so the stated objective is unmet by construction.

## 2. Findings

- **P1, candidate/store.py:11,18-19 — `put` writes to the filesystem on every call** (`tempfile.mkdtemp` + `open(..., "w")`), breaking the base memory-only contract. Proof (execution): after `put("a", 1)`, `_cache_dir` contains file `a`; a fresh `mkdtemp` dir per `Store` is also never cleaned up. Fix: remove the disk writes and `_cache_dir` entirely.
- **P1, candidate/store.py:16-17 — `put` rejects keys the base accepted** (`ValueError` unless the key matches `[A-Za-z0-9_-]+`); base `put` (base/store.py:7-8) stored any key. Proof (execution): `put("key with space", 1)`, `put("a.b", 1)`, and `put(("t","uple"), 1)` all raise. Fix: accept all keys as before (hash the key for any filename if disk use is retained).
- **P2, candidate/store.py:21-22 — the cache is write-only: `get` never reads it**, so reads are not sped up and every `put` pays wasted I/O. Proof (execution + static): `get("a")` still returns `1` after all cache files are deleted, and `get` touches only `_data`. Fix: have `get` consult the cache (or drop the cache if it stays unused).

## 3. Verdicts

- **Architecture: `Low`** — fundamental pattern bypass on primary axis A1 (reads must use the persistent cache; `get` never does) plus a significant primary-axis violation on A2 (`put` must accept arbitrary keys; it now rejects them). Gaps: (A1) write-only cache, objective unmet; (A2) `ValueError` regression for previously valid keys; (S1, secondary) leaked `mkdtemp` dir per `Store`. Change type: feature addition; rubric v1, checked against base (diff seen before freezing — no blind assessment claimed). Complexity: `Low` (one file, shallow call graph, invariant documented in PHILOSOPHY.md).
- **Soul: `Betrayed`** — statement 1 ("Memory-only: this package never touches the filesystem") is contradicted by the per-`put` disk writes (see P1 above); statement 2 ("Honest API: ... no hidden side effects") is `Tense`, since `put` gains disk I/O invisible from its name/signature — grouped under the same fix.

## 4. Checks and limits

- Ran `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=candidate python3 -m unittest tests.test_store` → 1 test OK (covers only single-key roundtrip; the test itself depends on candidate-internal `_cache_dir`, so it cannot run against base).
- Ran `/tmp/case-d-repro.py` (throwaway, outside the repo) → confirmed all three findings; temp dirs cleaned up.
- Static: full diff of base vs candidate; traced `get` (no cache read anywhere) and `put` (write + validation); no existing guard or in-scope caller invalidates any finding; all three are regressions introduced by the change, not pre-existing.
- Limits: no concurrency, performance, or multi-key coverage exists; scope restricted to the case-d files listed above.
