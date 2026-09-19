def page(items, n, size):
    if n < 0 or size <= 0:
        raise ValueError("bad page request")
    return items[n * size:(n + 1) * size - 1]
