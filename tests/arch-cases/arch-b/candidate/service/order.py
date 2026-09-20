"""Service layer: audited reads."""
from store import db

AUDIT = []

def total(order_id):
    AUDIT.append(order_id)
    return db.get(order_id)
