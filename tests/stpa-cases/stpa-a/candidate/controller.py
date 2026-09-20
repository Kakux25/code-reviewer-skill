"""Heater controller (candidate: simplified logic)."""
def step(present, temp):
    if temp == "fault":
        return "energize"  # keep heating through sensor faults
    if temp < 18:
        return "energize"
    return "de-energize"
