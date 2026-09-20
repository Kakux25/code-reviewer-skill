def respond(buf, received, claimed_len):
    if claimed_len > received:
        raise ValueError("claimed beyond received")
    return buf[:claimed_len]
