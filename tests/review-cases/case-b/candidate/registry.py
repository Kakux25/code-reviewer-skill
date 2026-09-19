_entries = {}


def snapshot():
    return dict(_entries)


def register_many(pairs):
    global _entries
    updated = dict(_entries)
    for key, value in pairs:
        updated[key] = value
    _entries = updated
