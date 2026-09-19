import shutil
import unittest

from store import Store


class StoreTest(unittest.TestCase):
    def test_roundtrip(self):
        store = Store()
        self.addCleanup(shutil.rmtree, store._cache_dir, True)
        store.put("a", 1)
        self.assertEqual(store.get("a"), 1)
