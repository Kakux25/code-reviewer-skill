import unittest
from tls import respond


class TlsTest(unittest.TestCase):
    def test_exact_echo(self):
        self.assertEqual(respond(b"hi", 2, 2), b"hi")

    def test_overclaim_rejected(self):
        buf = b"hi" + b"SECRET-PADDING"
        with self.assertRaises(ValueError):
            respond(buf, 2, 16)
