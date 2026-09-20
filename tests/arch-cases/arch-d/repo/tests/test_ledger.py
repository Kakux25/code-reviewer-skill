import unittest
import ledger

class T(unittest.TestCase):
    def test_add(self):
        self.assertEqual(ledger.add(100, 25), 125)

if __name__ == "__main__":
    unittest.main()
