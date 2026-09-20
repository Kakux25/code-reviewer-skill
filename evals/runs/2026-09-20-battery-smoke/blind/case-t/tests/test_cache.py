import unittest
import cache
from cache import get


class CacheTest(unittest.TestCase):
    def setUp(self):
        cache._CACHE = {"a": [1, 2]}

    def test_values(self):
        self.assertEqual(get("a"), [1, 2])

    def test_caller_mutation_isolated(self):
        get("a").append(99)
        self.assertEqual(get("a"), [1, 2])
