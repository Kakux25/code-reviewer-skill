# Heartbeat architecture

`respond(buf, claimed_len)` echoes at most the bytes actually received.
Bounds contract: a claimed length beyond the received bytes raises
ValueError; the response never includes bytes past the payload.
