# Pager architecture

Pure helpers only: no I/O, no shared state. `page(items, n, size)` returns
the n-th 0-based page of `size` elements; `labels.py` formats page headers
and is independent of paging arithmetic.
