"""Stand-in: checkout/cart.py with tax lines (CHG-102).

team-checkout approved in chat.
"""
def total(items, tax=0):
    return sum(items) + tax
