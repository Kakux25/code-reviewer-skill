# Files architecture

`resolve(root, name)` maps a tenant file name to a path under `root`.
Containment contract: absolute names and parent-directory escapes raise
ValueError; resolution never returns a path outside `root`.
