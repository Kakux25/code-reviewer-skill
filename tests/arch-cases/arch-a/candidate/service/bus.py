"""Tiny named-event bus."""
_subs = {}

def subscribe(name, fn):
    _subs.setdefault(name, []).append(fn)

def publish(name, payload):
    for fn in _subs.get(name, []):
        fn(payload)
