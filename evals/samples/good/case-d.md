# Sample review: case-d (GOOD — synthetic, for grader self-test)

**Decision**: Changes requested — the persistent cache betrays the documented memory-only essence.

**Findings**:
- P1, candidate/store.py:11-19 — filesystem writes via tempfile.mkdtemp plus open()/write() on every put; PHILOSOPHY.md states "Memory-only: this package never touches the filesystem. All state lives in process memory." Proof: cited lines plus the quoted essence statement. Fix: keep the cache in process memory or amend the essence deliberately.
- P2, candidate/store.py:21-22 — the cache is write-only: get() reads self._data and never consults _cache_dir, so every disk write is pure waste and reads are not sped up. Fix: read through the cache or remove it.

**Verdicts**: architectural `Low` (store module crosses into filesystem I/O, an improper boundary crossing); soul `Betrayed` (Memory-only statement contradicted with evidence).

**Checks and limits**: ran test_store.py with PYTHONPATH on candidate — suite passes, which covers function only and does not settle the essence question. Did not modify files.
