import os


def resolve(root, name):
    if os.path.isabs(name):
        raise ValueError("absolute name")
    full = os.path.normpath(os.path.join(root, name))
    if full != root and not full.startswith(root + os.sep):
        raise ValueError("escape from root")
    return full
