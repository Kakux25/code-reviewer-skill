"""Deterministic overload simulator (pure computation, no I/O).

Each step: new arrivals = base (+ spike inside the window); the
server clears up to capacity from arrivals + backlog; unserved
units backlog, and each one spawns RETRIES extra units next step
(immediate client retry). Returns peak backlog.
"""
def run(retries, steps=50, capacity=10, base_load=8,
        spike_at=10, spike_len=5, spike_extra=6):
    backlog = 0
    peak = 0
    for t in range(steps):
        in_spike = spike_at <= t < spike_at + spike_len
        new = base_load + (spike_extra if in_spike else 0)
        unserved = max(0, new + backlog - capacity)
        backlog = unserved * (1 + retries)
        peak = max(peak, backlog)
    return peak
