"""API layer: delegates to service."""
from service import order

def total(order_id):
    return order.total(order_id)
