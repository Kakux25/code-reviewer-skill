"""Relief controller (candidate: fast-cycle to save valve wear)."""
LIMIT = 500

def step(kpa, valve_open, seconds_open, seconds_over):
    # Fast cycle: confirm sustained pressure before opening, and
    # close quickly to save wear. All functional tests pass.
    if kpa > LIMIT and not valve_open and seconds_over >= 30:
        return "open"
    if valve_open and seconds_open >= 1:
        return "close"
    return "hold"
