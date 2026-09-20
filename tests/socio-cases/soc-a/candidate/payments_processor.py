"""Stand-in: payments/processor.py rounds fees half-up (CHG-101)."""
def fee(cents):
    return (cents + 50) // 100
