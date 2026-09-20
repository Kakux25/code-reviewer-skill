import unittest
import scale_sim

class T(unittest.TestCase):
    def test_documents_delay_damage(self):
        base = scale_sim.run(1)
        cand = scale_sim.run(300)
        self.assertLess(base, 30)
        self.assertGreater(cand, 50)

if __name__ == "__main__":
    unittest.main()
