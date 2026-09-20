# Cart architecture

Single pure helper `add` in `cart.py`: no I/O, no other modules, no
global state. Callers pass an explicit cart or omit it.
