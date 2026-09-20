"""Payments client (candidate: tight retry loop)."""
def charge(card, cents):
    while True:
        try:
            return gateway.charge(card, cents)
        except gateway.TransientError:
            continue
