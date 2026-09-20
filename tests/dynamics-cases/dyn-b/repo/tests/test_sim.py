import unittest
import scale_sim

class T(unittest.TestCase):
    def test_base_absorbs_spike(self):
        self.assertLess(scale_sim.run(1), 30)

if __name__ == "__main__":
    unittest.main()
