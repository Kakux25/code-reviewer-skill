"""Candidate acceptance: bus delivery + layering intact."""
import ast
import os
import unittest
from service import bus
from service import order

class T(unittest.TestCase):
    def test_bus_delivers(self):
        seen = []
        bus.subscribe("order.placed", seen.append)
        order.place("o1", 100)
        self.assertTrue(any(p["id"] == "o1" for p in seen))

    def test_service_imports_no_store(self):
        here = os.path.dirname(os.path.abspath(__file__))
        target = os.path.join(here, "..", "service", "order.py")
        tree = ast.parse(open(target).read())
        mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                mods.add(node.module.split(".")[0])
            elif isinstance(node, ast.Import):
                mods.update(a.name.split(".")[0] for a in node.names)
        self.assertNotIn("store", mods)

if __name__ == "__main__":
    unittest.main()
