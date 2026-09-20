import unittest
from pager import page


class PagerTest(unittest.TestCase):
    def test_full_pages(self):
        items = list(range(10))
        self.assertEqual(page(items, 0, 3), [0, 1, 2])
        self.assertEqual(page(items, 1, 3), [3, 4, 5])

    def test_bad_request(self):
        with self.assertRaises(ValueError):
            page([1, 2], -1, 3)
        with self.assertRaises(ValueError):
            page([1, 2], 0, 0)
