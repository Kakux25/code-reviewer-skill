from store import Store


def fetch(key, default=None):
    return Store().get(key, default)
