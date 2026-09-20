import unittest
import retry_sim

class T(unittest.TestCase):
    def test_documents_amplification(self):
        base = retry_sim.run(0)
        cand = retry_sim.run(2)
        self.assertLess(base, 25)
        self.assertGreater(cand, 1000)

if __name__ == "__main__":
    unittest.main()
