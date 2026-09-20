"""Deterministic autoscale simulator (pure computation, no I/O).

A load spike hits for spike_len steps. Overload schedules extra
capacity that arrives scale_delay steps later. Returns total
unserved requests.
"""
def run(scale_delay, steps=40, capacity0=10, spike_at=5, spike_len=3,
        spike_load=30, base=8, scale_amount=30):
    capacity = capacity0
    pending = []
    unserved_total = 0
    for t in range(steps):
        in_spike = spike_at <= t < spike_at + spike_len
        load = spike_load if in_spike else base
        arrived = [p for p in pending if p[0] <= t]
        for _, amt in arrived:
            capacity += amt
        pending = [p for p in pending if p[0] > t]
        unserved = max(0, load - capacity)
        unserved_total += unserved
        if unserved > 0 and not pending:
            pending.append((t + scale_delay, scale_amount))
    return unserved_total
