import unittest
from repo import names


class FakeDB:
    def __init__(self):
        self.calls = 0
        self.rows = {1: "a", 2: "b", 3: "c"}

    def fetch_many(self, ids):
        self.calls += 1
        return [self.rows[i] for i in ids]

    def fetch_one(self, i):
        self.calls += 1
        return self.rows[i]


class RepoTest(unittest.TestCase):
    def test_batch_values(self):
        db = FakeDB()
        self.assertEqual(names(db, [1, 2, 3]), ["a", "b", "c"])

    def test_single_round_trip(self):
        db = FakeDB()
        names(db, [1, 2, 3])
        self.assertEqual(db.calls, 1)
