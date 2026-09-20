def names(db, ids):
    return [db.fetch_one(i) for i in ids]
