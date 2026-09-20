# Losses and hazards

- L1: heater fire (property damage, harm).
- H1: heater energized while the room is unattended.
- H2: heater energized while the temperature sensor is faulty.

Safety constraints:
- SC1: the controller must de-energize the heater when presence is lost.
- SC2: the controller must never energize the heater on a faulty sensor reading.
