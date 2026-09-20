USERS = frozenset({0, 1, 2})


def allowed(user_id):
    return bool(user_id) and user_id in USERS
