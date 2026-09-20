def add(item, cart=None):
    if cart is None:
        cart = []
    cart.append(item)
    return cart
