# Cart architecture

Pure helpers only: no I/O, no shared state. `add(item, cart=None)` appends
to the given cart, or to a fresh cart when none is passed; each call with
no cart argument starts empty.
