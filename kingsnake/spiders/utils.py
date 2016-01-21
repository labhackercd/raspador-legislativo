
def ensure_list(i):
    if not isinstance(i, (list, tuple)):
        i = [i]
    return i
