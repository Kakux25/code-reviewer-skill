import unittest
from api import orders

class T(unittest.TestCase):
    def test_total(self):
        self.assertEqual(orders.total("o1"), 100)

if __name__ == "__main__":
    unittest.main()
