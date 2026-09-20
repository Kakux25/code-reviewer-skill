import unittest
from stats import total


class StatsTest(unittest.TestCase):
    def test_values(self):
        self.assertEqual(total([1, 2, 3]), 6)
        self.assertEqual(total([-1, 1]), 0)

    def test_empty(self):
        self.assertEqual(total([]), 0)
