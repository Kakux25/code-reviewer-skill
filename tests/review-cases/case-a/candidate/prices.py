def quote(amount, discount_percent=0):
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount out of range")
    return amount * (1 - discount_percent / 10)
