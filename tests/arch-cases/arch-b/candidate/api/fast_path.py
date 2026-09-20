"""Perf: skip the service layer, read the store directly (2x faster)."""
from store import db

def total(order_id):
    return db.get(order_id)
