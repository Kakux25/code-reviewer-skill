"""Stand-in: payments/processor.py rounds fees down."""
def fee(cents):
    return cents // 100
