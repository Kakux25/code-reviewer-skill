import shutil
import unittest

from store import Store


class StoreTest(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree("/tmp/store-cache", ignore_errors=True)

    def test_roundtrip(self):
        store = Store()
        store.put("a", 1)
        self.assertEqual(store.get("a"), 1)
