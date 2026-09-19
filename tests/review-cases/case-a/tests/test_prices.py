import unittest
from prices import quote


class PricesTest(unittest.TestCase):
    def test_percent_examples(self):
        for discount, expected in [(0, 200), (10, 180), (50, 100), (100, 0)]:
            with self.subTest(discount=discount):
                self.assertEqual(quote(200, discount), expected)

    def test_invalid_discount(self):
        for discount in (-1, 101):
            with self.subTest(discount=discount):
                with self.assertRaises(ValueError):
                    quote(200, discount)
