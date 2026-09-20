def load(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return {"records": fh.read().splitlines()}
    except OSError:
        return {}
