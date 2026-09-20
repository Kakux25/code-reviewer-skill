"""Pressure controller (no safety documents in repo)."""
GAIN = 1.0

def step(kpa):
    return GAIN * (500 - kpa)
