"""API layer: delegates to service."""
from service import order

def create(order_id, total_cents):
    return order.place(order_id, total_cents)
