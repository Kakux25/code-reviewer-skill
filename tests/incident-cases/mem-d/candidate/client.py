"""Payments client (candidate: bounded retries)."""
import random
import time

def charge(card, cents, breaker):
    delay = 0.1
    for _ in range(5):
        if breaker.is_open():
            raise breaker.OpenError
        try:
            return gateway.charge(card, cents)
        except gateway.TransientError:
            time.sleep(delay * (0.5 + random.random()))
            delay *= 2
    raise gateway.GiveUp
