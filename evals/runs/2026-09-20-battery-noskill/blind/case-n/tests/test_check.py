import unittest
from check import validate


class CheckTest(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(validate([3, 1, 2]))

    def test_invalid(self):
        self.assertFalse(validate([3, -1, 2]))
