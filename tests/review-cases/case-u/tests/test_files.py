import unittest
from files import resolve


class FilesTest(unittest.TestCase):
    def test_plain_name(self):
        self.assertEqual(resolve("/srv/t1", "a.txt"), "/srv/t1/a.txt")

    def test_absolute_name_rejected(self):
        with self.assertRaises(ValueError):
            resolve("/srv/t1", "/etc/passwd")

    def test_escape_rejected(self):
        with self.assertRaises(ValueError):
            resolve("/srv/t1", "../x")
