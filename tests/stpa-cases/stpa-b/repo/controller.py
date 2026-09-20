"""Relief controller (base)."""
LIMIT = 500

def step(kpa, valve_open, seconds_open):
    if kpa > LIMIT and not valve_open:
        return "open"
    if valve_open and kpa <= LIMIT:
        return "close"
    return "hold"
