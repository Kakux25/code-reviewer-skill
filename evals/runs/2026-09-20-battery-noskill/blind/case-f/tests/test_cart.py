import unittest
from cart import add


class CartTest(unittest.TestCase):
    def test_fresh_cart_each_call(self):
        self.assertEqual(add("a"), ["a"])
        self.assertEqual(add("b"), ["b"])

    def test_explicit_cart(self):
        mine = ["x"]
        self.assertEqual(add("y", mine), ["x", "y"])
