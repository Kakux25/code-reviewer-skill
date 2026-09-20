def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return {"records": fh.read().splitlines()}
