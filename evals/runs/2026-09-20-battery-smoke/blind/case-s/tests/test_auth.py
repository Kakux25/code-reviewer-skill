import unittest
from auth import allowed


class AuthTest(unittest.TestCase):
    def test_operator_zero(self):
        self.assertTrue(allowed(0))

    def test_regular_and_unknown(self):
        self.assertTrue(allowed(1))
        self.assertFalse(allowed(99))
        self.assertFalse(allowed(None))
