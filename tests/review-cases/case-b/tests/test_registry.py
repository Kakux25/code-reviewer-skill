import importlib
import unittest
import registry


class RegistryTest(unittest.TestCase):
    def setUp(self):
        importlib.reload(registry)

    def test_generator_batch(self):
        registry.register_many((pair for pair in [("a", 1), ("b", 2)]))
        self.assertEqual(registry.snapshot(), {"a": 1, "b": 2})

    def test_failed_generator_keeps_previous_state(self):
        registry.register_many([("old", 7)])

        def failing():
            yield "partial", 8
            raise ValueError("interrupted")

        with self.assertRaises(ValueError):
            registry.register_many(failing())
        self.assertEqual(registry.snapshot(), {"old": 7})

    def test_snapshot_is_a_copy(self):
        registry.register_many([("old", 7)])
        view = registry.snapshot()
        view["old"] = 9
        self.assertEqual(registry.snapshot(), {"old": 7})
