API_KEY = "prod-key-7f3a9c1e4b2d8f6a0e5c7b9d1"


def make_client():
    return {"api_key": API_KEY, "retries": 3}
