import unittest
import bounded_sim

class T(unittest.TestCase):
    def test_candidate_stays_bounded(self):
        self.assertEqual(bounded_sim.run(), 14)

if __name__ == "__main__":
    unittest.main()
