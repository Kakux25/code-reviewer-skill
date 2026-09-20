# Cache architecture

`get(key)` serves cached rows. Isolation contract: callers receive an
independent copy; mutating a served value must never corrupt the cache.
