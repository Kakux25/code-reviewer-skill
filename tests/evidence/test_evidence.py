"""Gate 1: evidence store + adapters (stdlib only).

Falsification contract (roadmap gate 1): dirty-tree state never
resembles success; spoofed, mislocated, drifted, or missing-tool
collections always surface as failed/failed-version records, never
as silence or as success.
"""
import hashlib
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import evidence


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = evidence.Store(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_round_trip_verifies_hash(self):
        rec = evidence.make_receipt(
            id="git:HEAD", kind="vcs", locator=".", content="abc123\n",
            tool="git", tool_version="stub-1", collector="git")
        digest = self.store.put(rec)
        back = self.store.get("git:HEAD")
        self.assertEqual(back["content"], "abc123\n")
        # File digest (address) covers all bytes; content_hash covers content.
        self.assertTrue((Path(self.tmp.name) / ("%s.json" % digest)).is_file())
        self.assertEqual(self.store.history("git:HEAD"), [digest])
        self.assertEqual(back["status"], "ok")

    def test_tampered_bytes_raise_on_read(self):
        rec = evidence.make_receipt(
            id="t1", kind="test", locator="x", content="pass",
            tool="t", tool_version="1", collector="c")
        digest = self.store.put(rec)
        target = Path(self.tmp.name) / ("%s.json" % digest)
        target.write_text(target.read_text().replace("pass", "FAIL"))
        with self.assertRaises(evidence.IntegrityError):
            self.store.get("t1")

    def test_drift_is_recorded_never_overwritten(self):
        first = evidence.make_receipt(
            id="d1", kind="test", locator="x", content="v1",
            tool="t", tool_version="1", collector="c")
        h1 = self.store.put(first)
        second = evidence.make_receipt(
            id="d1", kind="test", locator="x", content="v2",
            tool="t", tool_version="1", collector="c")
        h2 = self.store.put(second)
        self.assertNotEqual(h1, h2)
        latest = self.store.get("d1")
        self.assertEqual(latest["status"], "failed-version")
        self.assertEqual(latest["content"], "v2")
        history = self.store.history("d1")
        self.assertEqual(history, [h1, h2])
        # Old bytes still on disk, untouched.
        old = json.loads((Path(self.tmp.name) / ("%s.json" % h1)).read_text())
        self.assertEqual(old["content"], "v1")

    def test_locator_escape_rejected(self):
        with self.assertRaises(evidence.IntegrityError):
            evidence.make_receipt(
                id="e1", kind="file", locator="../../etc/passwd",
                content="x", tool="t", tool_version="1", collector="c",
                root="/repo")

    def test_missing_id_raises(self):
        with self.assertRaises(KeyError):
            self.store.get("nope")

    def test_identical_reput_is_idempotent(self):
        first = evidence.make_receipt(
            id="r1", kind="test", locator="x", content="same",
            tool="t", tool_version="1", collector="c",
            collected_at="2026-01-01T00:00:00+00:00")
        second = evidence.make_receipt(
            id="r1", kind="test", locator="x", content="same",
            tool="t", tool_version="1", collector="c",
            collected_at="2026-06-01T00:00:00+00:00")
        h1 = self.store.put(first)
        self.assertEqual(self.store.put(second), h1)
        self.assertEqual(self.store.history("r1"), [h1])

    def test_truncated_index_detected_by_pin(self):
        h1 = self.store.put(evidence.make_receipt(
            id="p1", kind="test", locator="x", content="v1",
            tool="t", tool_version="1", collector="c"))
        h2 = self.store.put(evidence.make_receipt(
            id="p1", kind="test", locator="x", content="v2",
            tool="t", tool_version="1", collector="c"))
        index_path = Path(self.tmp.name) / "index.json"
        index = json.loads(index_path.read_text())
        index["p1"] = [h1]  # adversary truncates history
        index_path.write_text(json.dumps(index))
        # Unpinned read trusts the ledger (documented); pinned read refuses.
        self.assertEqual(self.store.get("p1")["content"], "v1")
        with self.assertRaises(evidence.IntegrityError):
            self.store.get("p1", expected=h2)

    def test_index_pointing_at_foreign_bytes_raises(self):
        self.store.put(evidence.make_receipt(
            id="a1", kind="test", locator="x", content="aaa",
            tool="t", tool_version="1", collector="c"))
        other = self.store.put(evidence.make_receipt(
            id="b2", kind="test", locator="x", content="bbb",
            tool="t", tool_version="1", collector="c"))
        index_path = Path(self.tmp.name) / "index.json"
        index = json.loads(index_path.read_text())
        index["a1"] = [other]  # adversary swaps the pointer
        index_path.write_text(json.dumps(index))
        with self.assertRaises(evidence.IntegrityError):
            self.store.get("a1")

    def test_deleted_receipt_raises_integrity_error(self):
        digest = self.store.put(evidence.make_receipt(
            id="gone", kind="test", locator="x", content="x",
            tool="t", tool_version="1", collector="c"))
        (Path(self.tmp.name) / ("%s.json" % digest)).unlink()
        with self.assertRaises(evidence.IntegrityError):
            self.store.get("gone")


def write_stub_git(bindir, head="abc123", dirty=False, status_fails=False):
    """Deterministic stub git: no real repository needed."""
    path = Path(bindir) / "git"
    if status_fails:
        status_cmd = "exit 1"
    else:
        status_cmd = 'echo " M x.py"' if dirty else "true"
    path.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "--version" ]; then echo "git version stub-9"; exit 0; fi\n'
        'if [ "$1" = "-C" ]; then shift 2; fi\n'
        'if [ "$1" = "rev-parse" ]; then echo "%s"; exit 0; fi\n'
        'if [ "$1" = "status" ]; then %s; exit 0; fi\n'
        "exit 3\n" % (head, status_cmd))
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return str(path)


class GitAdapterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.bin = Path(self.tmp.name) / "bin"
        self.bin.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_tree_status_ok(self):
        write_stub_git(self.bin, head="deadbeef", dirty=False)
        rec = evidence.collect_git("/repo", path_env=str(self.bin))
        self.assertEqual(rec["status"], "ok")
        self.assertIn("deadbeef", rec["content"])

    def test_dirty_tree_never_ok(self):
        write_stub_git(self.bin, head="deadbeef", dirty=True)
        rec = evidence.collect_git("/repo", path_env=str(self.bin))
        self.assertEqual(rec["status"], "tainted")
        self.assertIn("dirty", rec["reason"].lower())

    def test_missing_git_is_failed_collector(self):
        rec = evidence.collect_git("/repo", path_env=str(self.bin))
        self.assertEqual(rec["status"], "failed")
        self.assertIn("reason", rec)

    def test_failing_status_is_failed_not_ok(self):
        write_stub_git(self.bin, head="deadbeef", status_fails=True)
        rec = evidence.collect_git("/repo", path_env=str(self.bin))
        self.assertEqual(rec["status"], "failed")

    def test_git_version_recorded(self):
        write_stub_git(self.bin, head="deadbeef", dirty=False)
        rec = evidence.collect_git("/repo", path_env=str(self.bin))
        self.assertIn("stub-9", rec["tool_version"])

    def test_hung_tool_yields_no_record_not_silence(self):
        sleeper = Path(self.tmp.name) / "sleeper.sh"
        sleeper.write_text("#!/bin/sh\nsleep 5\n")
        sleeper.chmod(sleeper.stat().st_mode | stat.S_IEXEC)
        self.assertIsNone(evidence._run([str(sleeper)], timeout=0.01))


class ToolAdapterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _pkg(self, name, body):
        d = self.root / name
        (d / "tests").mkdir(parents=True)
        (d / "tests" / "__init__.py").write_text("")
        (d / "mod.py").write_text("VALUE = 1\n")
        (d / "tests" / "test_mod.py").write_text(body)
        return d

    def test_unittest_pass_recorded(self):
        d = self._pkg("okpkg", "import unittest\nfrom mod import VALUE\n"
                      "class T(unittest.TestCase):\n"
                      "    def test_v(self):\n"
                      "        self.assertEqual(VALUE, 1)\n")
        rec = evidence.collect_unittest(d)
        self.assertEqual(rec["status"], "ok")
        self.assertIn("exit=0", rec["content"])

    def test_unittest_failure_is_observation_not_collector_failure(self):
        d = self._pkg("badpkg", "import unittest\n"
                      "class T(unittest.TestCase):\n"
                      "    def test_v(self):\n"
                      "        self.assertEqual(1, 2)\n")
        rec = evidence.collect_unittest(d)
        self.assertEqual(rec["status"], "ok")
        self.assertRegex(rec["content"], r"exit=[1-9]")

    def test_pycompile_clean_and_broken(self):
        good = self.root / "good.py"
        good.write_text("x = 1\n")
        bad = self.root / "bad.py"
        bad.write_text("def broken(:\n")
        rec = evidence.collect_pycompile([good, bad])
        self.assertEqual(rec["status"], "ok")
        self.assertIn("good.py: ok", rec["content"])
        self.assertIn("bad.py: FAIL", rec["content"])

    def test_split_layout_needs_pythonpath(self):
        src = self.root / "src"
        (src / "tests").mkdir(parents=True)
        (self.root / "lib").mkdir()
        (self.root / "lib" / "thing.py").write_text("V = 7\n")
        (src / "tests" / "__init__.py").write_text("")
        (src / "tests" / "test_thing.py").write_text(
            "import unittest\nfrom thing import V\n"
            "class T(unittest.TestCase):\n"
            "    def test_v(self):\n"
            "        self.assertEqual(V, 7)\n")
        bare = evidence.collect_unittest(src / "tests")
        self.assertNotIn("exit=0", bare["content"])
        fixed = evidence.collect_unittest(
            src / "tests",
            extra_env={"PYTHONPATH": str(self.root / "lib")})
        self.assertIn("exit=0", fixed["content"])

    def test_missing_suite_dir_is_failed_collector(self):
        rec = evidence.collect_unittest(self.root / "no-such-dir")
        self.assertEqual(rec["status"], "failed")
        self.assertIn("missing", rec["reason"])

    def test_empty_pycompile_is_failed_not_ok(self):
        rec = evidence.collect_pycompile([])
        self.assertEqual(rec["status"], "failed")
        self.assertIn("no files", rec["reason"])

    def test_missing_pycompile_input_is_failed(self):
        rec = evidence.collect_pycompile([self.root / "ghost.py"])
        self.assertEqual(rec["status"], "failed")
        self.assertIn("missing", rec["reason"])

    def test_pycompile_writes_no_pycache(self):
        target = self.root / "clean.py"
        target.write_text("x = 1\n")
        evidence.collect_pycompile([target])
        self.assertFalse((self.root / "__pycache__").exists())

    def test_content_hash_matches_bytes(self):
        d = self._pkg("h", "import unittest\nclass T(unittest.TestCase):\n"
                      "    def test_v(self):\n        pass\n")
        rec = evidence.collect_unittest(d)
        expect = hashlib.sha256(rec["content"].encode("utf-8")).hexdigest()
        self.assertEqual(rec["content_hash"], expect)


if __name__ == "__main__":
    unittest.main()
