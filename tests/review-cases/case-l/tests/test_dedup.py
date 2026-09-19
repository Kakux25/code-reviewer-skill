import unittest
from dedup import dedup


class DedupTest(unittest.TestCase):
    def test_order_kept(self):
        self.assertEqual(dedup([3, 1, 3, 2, 1]), [3, 1, 2])

    def test_empty_and_single(self):
        self.assertEqual(dedup([]), [])
        self.assertEqual(dedup(["a"]), ["a"])
