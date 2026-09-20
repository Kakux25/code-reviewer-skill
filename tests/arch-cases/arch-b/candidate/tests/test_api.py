import unittest
from api import fast_path

class T(unittest.TestCase):
    def test_total(self):
        self.assertEqual(fast_path.total("o1"), 100)

if __name__ == "__main__":
    unittest.main()
