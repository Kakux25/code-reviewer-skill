import unittest
from quiet import calc


class QuietTest(unittest.TestCase):
    def test_values(self):
        self.assertEqual(calc(3, 2), 7)
        self.assertEqual(calc(0, 5), -5)
