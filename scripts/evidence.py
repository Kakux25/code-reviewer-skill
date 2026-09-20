"""Gate 1: evidence store + collectors (stdlib only).

Receipts are content-addressed JSON: the filename is the sha256 of the
canonical bytes, so tampering is detected on read. Logical ids may gain
new revisions, but an id whose content changes is recorded as
failed-version; old bytes are never overwritten. Collectors never fail
silently: missing tools and dirty trees become explicit records.

Trust boundary: receipt FILES are self-authenticating (filename is the
hash); the index.json ledger is a convenience pointer and is NOT
authenticated. Callers needing tamper-evidence pin the digest returned
by put() and pass it as get()'s expected argument (trapped hash).
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


class IntegrityError(Exception):
    """Stored bytes fail verification, or a locator escapes root."""


def _utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def make_receipt(id, kind, locator, content, tool, tool_version,
                 collector, status="ok", reason="", root=None,
                 collected_at=None):
    """Build a receipt. root confines untrusted locators (adapters pass
    trusted absolute paths and leave root unset - caller-side validation).
    collected_at override exists for deterministic tests only."""
    if root is not None:
        full = (Path(root) / locator).resolve()
        if full != Path(root).resolve() and Path(root).resolve() not in full.parents:
            raise IntegrityError("locator escapes root: %s" % locator)
    return {
        "id": id,
        "kind": kind,
        "locator": locator,
        "content": content,
        "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "tool": tool,
        "tool_version": tool_version,
        "collector": collector,
        "collected_at": collected_at or _utcnow(),
        "status": status,
        "reason": reason,
    }


def _canonical(receipt):
    return (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")


class Store:
    """Append-only receipt store rooted at a directory."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "index.json"
        if not self.index_path.is_file():
            self.index_path.write_text("{}\n", encoding="utf-8")

    def _index(self):
        return json.loads(self.index_path.read_text(encoding="utf-8"))

    def _save_index(self, index):
        self.index_path.write_text(json.dumps(index, indent=2) + "\n",
                                   encoding="utf-8")

    def _path(self, digest):
        return self.root / ("%s.json" % digest)

    def _read_verified(self, digest):
        try:
            raw = self._path(digest).read_text(encoding="utf-8")
        except FileNotFoundError:
            raise IntegrityError("receipt file missing: %s" % digest)
        if hashlib.sha256(raw.encode("utf-8")).hexdigest() != digest:
            raise IntegrityError("stored bytes fail hash check: %s" % digest)
        return json.loads(raw)

    def put(self, receipt):
        index = self._index()
        prior = index.get(receipt["id"], [])
        if prior:
            # Drift compares content_hash only: volatile collected_at
            # must never turn an identical re-collection into drift.
            latest = self._read_verified(prior[-1])
            if latest["content_hash"] == receipt["content_hash"]:
                return prior[-1]  # idempotent reput
            receipt = dict(receipt, status="failed-version",
                           reason="content changed under id %s; prior %s "
                           "preserved" % (receipt["id"], prior[-1]))
        body = _canonical(receipt)
        digest = hashlib.sha256(body).hexdigest()
        target = self._path(digest)
        if not target.is_file():
            target.write_bytes(body)
        index[receipt["id"]] = prior + [digest]
        self._save_index(index)
        return digest

    def history(self, id):
        index = self._index()
        if id not in index:
            raise KeyError(id)
        return index[id]

    def get(self, id, expected=None):
        """Latest receipt. expected pins the digest (trapped hash): a
        history that no longer ends there raises instead of going stale."""
        latest = self.history(id)[-1]
        if expected is not None and latest != expected:
            raise IntegrityError(
                "history for %s ends at %s, pinned %s" % (id, latest, expected))
        receipt = self._read_verified(latest)
        if receipt["id"] != id:
            raise IntegrityError("index points %s at %s's bytes"
                                 % (id, receipt["id"]))
        return receipt


def _run(argv, path_env=None, timeout=300):
    import os
    env = dict(os.environ)
    if path_env is not None:
        env["PATH"] = path_env
    try:
        return subprocess.run(argv, capture_output=True, text=True,
                              timeout=timeout, env=env)
    except (OSError, subprocess.TimeoutExpired):
        return None


def _which(name, path_env):
    import os
    if path_env is None:
        paths = os.environ.get("PATH", "").split(os.pathsep)
    else:
        paths = path_env.split(os.pathsep)
    for directory in paths:
        candidate = Path(directory) / name
        if candidate.is_file():
            import os as _os
            if _os.access(candidate, _os.X_OK):
                return str(candidate)
    return None


def collect_git(repo, path_env=None):
    """HEAD SHA + dirty status. Dirty trees are tainted, never ok."""
    git = _which("git", path_env)
    if git is None:
        return make_receipt(
            id="git:HEAD", kind="vcs", locator=".", content="",
            tool="git", tool_version="missing", collector="git",
            status="failed", reason="git not found on PATH")
    version = _run([git, "--version"], path_env)
    tool_version = (version.stdout.strip() if version is not None
                    and version.returncode == 0 else "unknown")
    head = _run([git, "-C", repo, "rev-parse", "HEAD"], path_env)
    status = _run([git, "-C", repo, "status", "--porcelain"], path_env)
    if (head is None or status is None or head.returncode != 0
            or status.returncode != 0):
        return make_receipt(
            id="git:HEAD", kind="vcs", locator=".", content="",
            tool="git", tool_version=tool_version, collector="git",
            status="failed", reason="git command failed in %s" % repo)
    sha = head.stdout.strip()
    dirty = bool(status.stdout.strip())
    return make_receipt(
        id="git:HEAD", kind="vcs", locator=".", content="HEAD %s\n" % sha,
        tool="git", tool_version=tool_version, collector="git",
        status="tainted" if dirty else "ok",
        reason="dirty working tree" if dirty else "")


def collect_unittest(package_dir):
    """Run a unittest suite; the exit code is the observation. A missing
    target is mislocated collection (failed), not an observation."""
    if not Path(package_dir).is_dir():
        return make_receipt(
            id="test:unittest", kind="test", locator=str(package_dir),
            content="", tool="python", tool_version=sys.version.split()[0],
            collector="unittest", status="failed",
            reason="target directory missing: %s" % package_dir)
    package_dir = str(package_dir)
    proc = _run([sys.executable, "-m", "unittest", "discover",
                 "-s", package_dir])
    if proc is None:
        return make_receipt(
            id="test:unittest", kind="test", locator=package_dir,
            content="", tool="python", tool_version="missing",
            collector="unittest", status="failed",
            reason="python interpreter not executable")
    tail = (proc.stdout + proc.stderr)[-2000:]
    return make_receipt(
        id="test:unittest", kind="test", locator=package_dir,
        content="exit=%d\n%s" % (proc.returncode, tail),
        tool="python", tool_version=sys.version.split()[0],
        collector="unittest")


def collect_pycompile(files):
    """Compile-check files without touching them (compile() builtin, no
    __pycache__ writes). Empty input or missing files are failed
    collections: nothing checked must never read as success."""
    files = [Path(f) for f in files]
    if not files:
        return make_receipt(
            id="static:pycompile", kind="static", locator=".",
            content="", tool="py_compile",
            tool_version=sys.version.split()[0], collector="pycompile",
            status="failed", reason="no files collected")
    missing = [str(f) for f in files if not f.is_file()]
    if missing:
        return make_receipt(
            id="static:pycompile", kind="static", locator=".",
            content="", tool="py_compile",
            tool_version=sys.version.split()[0], collector="pycompile",
            status="failed", reason="input missing: %s" % ", ".join(missing))
    lines = []
    for path in files:
        try:
            compile(path.read_bytes(), str(path), "exec")
            lines.append("%s: ok" % path.name)
        except Exception as exc:  # noqa: BLE001 - observation, not control
            lines.append("%s: FAIL (%s)" % (path.name, exc))
    return make_receipt(
        id="static:pycompile", kind="static", locator=".",
        content="\n".join(lines) + "\n",
        tool="py_compile", tool_version=sys.version.split()[0],
        collector="pycompile")
