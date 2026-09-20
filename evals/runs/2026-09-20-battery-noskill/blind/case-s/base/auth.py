USERS = frozenset({0, 1, 2})


def allowed(user_id):
    return user_id is not None and user_id in USERS
