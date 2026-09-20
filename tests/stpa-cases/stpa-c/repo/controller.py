"""Heater controller (base)."""
def step(present, temp, minutes_on):
    if temp == "fault":
        return "de-energize"
    if not present:
        return "de-energize"
    if minutes_on >= 60:
        return "de-energize"
    if temp < 18:
        return "energize"
    return "de-energize"
