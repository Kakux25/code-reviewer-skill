_entries = {}


def snapshot():
    return dict(_entries)


def _replace(new_entries):
    global _entries
    _entries = new_entries


def register_many(pairs):
    if not isinstance(pairs, list):
        raise TypeError("list required")
    updated = dict(_entries)
    for key, value in pairs:
        updated[key] = value
    _replace(updated)
