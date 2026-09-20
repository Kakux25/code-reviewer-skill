# Repo architecture

`repo.py` owns batch fetching; the database object offers `fetch_many(ids)`
for batches and `fetch_one(id)` for single rows.
