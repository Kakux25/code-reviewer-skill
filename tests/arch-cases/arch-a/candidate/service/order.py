"""Order placement via string-name registry indirection."""
from service import bus
from service.registry import handler

@handler("order.placed")
def _audit(payload):
    AUDIT_LOG.append(payload)

AUDIT_LOG = []

def place(order_id, total_cents):
    bus.publish("order.placed", {"id": order_id, "total": total_cents})
    return {"id": order_id, "total": total_cents}
