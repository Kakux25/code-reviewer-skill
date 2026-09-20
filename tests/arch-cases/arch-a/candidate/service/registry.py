"""String-name handler registry (new indirection).

Handlers are looked up by event name at publish time instead of
being wired directly. Unusual, but all traffic still crosses the bus.
"""
from service import bus

REGISTRY = {}

def handler(event_name):
    def wrap(fn):
        REGISTRY[event_name] = fn
        bus.subscribe(event_name, fn)
        return fn
    return wrap
