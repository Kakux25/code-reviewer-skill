"""Deterministic bounded-retry simulator (pure computation, no I/O).

Backoff drains 2 backlogged units per step; a breaker opens for 5
steps when unserved load exceeds 15, shedding new load. Returns
peak backlog.
"""
def run(steps=60, capacity=10, base=8, spike_extra=6, spike_len=5):
    backlog = 0
    breaker_open_until = -1
    peak = 0
    for t in range(steps):
        in_spike = 10 <= t < 10 + spike_len
        load = base + (spike_extra if in_spike else 0)
        sent = 0 if t < breaker_open_until else load + backlog
        unserved = max(0, sent - capacity)
        if unserved > 15:
            breaker_open_until = t + 5
            backlog = 0
        else:
            backlog = max(0, backlog + unserved - 2)
        peak = max(peak, backlog)
    return peak
