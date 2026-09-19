import os
import re
import tempfile


class Store:
    """In-memory key-value store with a persistent read cache."""

    def __init__(self):
        self._data = {}
        self._cache_dir = tempfile.mkdtemp(prefix="store-cache-")

    def put(self, key, value):
        self._data[key] = value
        name = str(key)
        if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
            raise ValueError("cache keys must be alphanumeric")
        with open(os.path.join(self._cache_dir, name), "w") as fh:
            fh.write(repr(value))

    def get(self, key, default=None):
        return self._data.get(key, default)
