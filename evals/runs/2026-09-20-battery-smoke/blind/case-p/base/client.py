import os


def make_client():
    return {"api_key": os.environ["API_KEY"], "retries": 3}
