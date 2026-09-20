def validate(rows):
    rows.sort()
    return all(r > 0 for r in rows)
