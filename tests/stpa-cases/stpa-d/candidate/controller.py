"""Pressure controller (retuned gain)."""
GAIN = 4.0

def step(kpa):
    return GAIN * (500 - kpa)
