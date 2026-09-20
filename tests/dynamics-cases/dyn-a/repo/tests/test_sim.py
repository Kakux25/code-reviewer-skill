import unittest
import retry_sim

class T(unittest.TestCase):
    def test_base_stays_bounded(self):
        self.assertLess(retry_sim.run(0), 25)

if __name__ == "__main__":
    unittest.main()
