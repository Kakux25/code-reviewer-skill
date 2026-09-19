# Review: case-d — persistent read cache (base vs candidate)

1. **Decision**: `Changes requested` — P1 filesystem write breaks the documented memory-only contract and betrays the essence.

2. **Findings**:
   - `P1`, candidate/store.py:11,16-19 — `put()` creates a temp dir (`mkdtemp`) and writes `repr(value)` to a file per key, and rejects previously valid non-alphanumeric keys with `ValueError`; breaks the memory-only contract. Proof (execution): probe with candidate on `PYTHONPATH` showed `put("a",1)` created file `_cache_dir/a`, and `put("a/b")` / `put("a.b")` / `put("key with space")` raised `ValueError`, while base `put()` is plain `self._data[key] = value` with no validation. Fix: delete `_cache_dir`, the key regex, and the file write; keep `put()` as memory-only dict assignment.
   - `P2`, candidate/store.py:11,21-22 — cache is write-only and the read-speedup objective is unmet: `get()` reads only `_data`, never `_cache_dir`, and each `Store()` leaks a `mkdtemp` dir. Proof (execution + static): probe showed deleting `_cache_dir/a` left `get("a") == 1`; no read of `_cache_dir` exists in the candidate. Fix: remove the filesystem cache entirely (a read-through cache would still violate memory-only).

3. **Verdicts**:
   - Architecture: `Low` — primary-axis A1 (memory-only, no filesystem I/O) violated by `mkdtemp` + per-`put` file writes; improper boundary crossing to the filesystem.
   - Soul: `Betrayed` — S1 "Memory-only: this package never touches the filesystem" contradicted by candidate/store.py:11,18-19 (probe-confirmed file creation).

4. **Checks and limits**:
   - `PYTHONPATH=case-d/candidate PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s case-d/tests -v` → 1 test ran, OK (`test_roundtrip`).
   - `python3 -m pytest case-d/tests/test_store.py` → not run: `No module named pytest` (no pytest installed).
   - `/tmp/probe_case_d.py` (same env) → confirmed: cache file created on `put`, `get` unaffected by cache-file deletion, `ValueError` on non-alphanumeric keys; temp dir cleaned up.
   - Static: base/store.py (11 lines), candidate/store.py (22 lines), base/PHILOSOPHY.md, tests/test_store.py; no caller tracing beyond the case (isolated fixture, no production consumers).
   - Limits: no VCS revisions (scope is case-d/base vs case-d/candidate paths); suite covers only one alphanumeric roundtrip; base not executed (static only); answer key not read per instructions.

## Annex — rubric (v1, recorded after diff exposure; all criteria checked against base)

- Change type: feature addition (persistent cache), assessed against the memory-only property it was not authorized to replace; complexity `Low` (single class, no cross-component coordination).
- A1 (primary) Memory-only persistence: all state in process memory, no filesystem I/O. Base evidence: base/store.py has no imports, only `dict` ops; docstring "In-memory". Preserve anchor: `put`/`get` touch only `_data`. Violate anchor: `mkdtemp`/`open`/file writes.
- A2 (secondary) Arbitrary-key contract: `put` accepts any hashable key. Base evidence: base/store.py:7-8 plain assignment, no validation. Preserve: no key restriction. Violate: raise on previously valid keys.
- A3 (minor) Effective, cleaned-up resources: acquired resources are used and released. Base evidence: no external resources. Preserve: no temp dirs, or read + cleanup. Violate: write-only temp dir leak.
- Gaps: G1 (A1) `mkdtemp` + per-`put` file write — primary violation; G2 (A2) `ValueError` on non-alphanumeric keys — secondary deviation / functional regression; G3 (A3) write-only cache + leaked temp dir, objective unmet — minor deviation.
- Soul statements (source: base/PHILOSOPHY.md): S1 "Memory-only: this package never touches the filesystem. All state lives in process memory." → `Betrayed` (candidate/store.py:11,18-19 + probe); S2 "Honest API: function names say what they do; no hidden side effects." → `Betrayed` (`put` hides filesystem writes and an undocumented `ValueError`).
