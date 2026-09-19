# Loader architecture

`load(path)` reads records from a file. The error contract: a missing file
raises FileNotFoundError so callers can distinguish "missing" from "empty".
