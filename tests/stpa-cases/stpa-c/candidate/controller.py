"""Heater controller (candidate: refactored guards, same interlocks)."""
def _ok(present, temp, minutes_on):
    return present and temp != "fault" and minutes_on < 60

def step(present, temp, minutes_on):
    if not _ok(present, temp, minutes_on):
        return "de-energize"
    if temp < 18:
        return "energize"
    return "de-energize"
