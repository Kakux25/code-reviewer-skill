"""Heater controller (base)."""
def step(present, temp):
    if temp == "fault":
        return "de-energize"
    if not present:
        return "de-energize"
    if temp < 18:
        return "energize"
    return "de-energize"
