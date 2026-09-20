import unittest
from greeter import greet


class GreeterTest(unittest.TestCase):
    def test_single_name(self):
        self.assertEqual(greet("Ada"), "Hello, Ada!")

    def test_custom_punct(self):
        self.assertEqual(greet("Ada", "?"), "Hello, Ada?")
