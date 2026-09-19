def names(db, ids):
    return db.fetch_many(list(ids))
