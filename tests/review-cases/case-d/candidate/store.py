import os


class Store:
    """In-memory key-value store with a persistent read cache."""

    def __init__(self):
        self._data = {}
        self._cache_dir = "/tmp/store-cache"
        os.makedirs(self._cache_dir, exist_ok=True)

    def put(self, key, value):
        self._data[key] = value
        with open(os.path.join(self._cache_dir, str(key)), "w") as fh:
            fh.write(repr(value))

    def get(self, key, default=None):
        return self._data.get(key, default)
