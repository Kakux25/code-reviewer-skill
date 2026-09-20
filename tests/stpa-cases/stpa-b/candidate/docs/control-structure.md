# Control structure

Controller -> Relief valve: control actions {open, close}.
Pressure sensor -> Controller: feedback {kpa}.

Timing is part of every control action: too late and too short
are unsafe even when the action itself is correct.

Timing note: step() runs at least every 0.5 s, so an open on
the first over-limit step meets the SC1 2 s bound.
