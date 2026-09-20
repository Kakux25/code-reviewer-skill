import os
import tempfile
import unittest
from loader import load


class LoaderTest(unittest.TestCase):
    def test_missing_file_raises(self):
        missing = os.path.join(tempfile.gettempdir(), "no-such-case-g.txt")
        if os.path.exists(missing):
            os.unlink(missing)
        with self.assertRaises(FileNotFoundError):
            load(missing)

    def test_reads_records(self):
        fd, path = tempfile.mkstemp(prefix="case-g-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write("a\nb\n")
            self.assertEqual(load(path), {"records": ["a", "b"]})
        finally:
            os.unlink(path)
