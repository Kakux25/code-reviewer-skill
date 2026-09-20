"""Order placement (base: no notification yet)."""
from service import bus

def place(order_id, total_cents):
    bus.publish("order.placed", {"id": order_id, "total": total_cents})
    return {"id": order_id, "total": total_cents}
