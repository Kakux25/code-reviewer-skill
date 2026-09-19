import unittest
from client import make_client


class ClientTest(unittest.TestCase):
    def test_shape(self):
        c = make_client()
        self.assertEqual(c["retries"], 3)
        self.assertTrue(c["api_key"])
