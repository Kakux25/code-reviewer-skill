import unittest
from expr import calc


class ExprTest(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual(calc("1.5"), 1.5)
        self.assertEqual(calc("2+3"), 5)
