def groupby(iterable, key):
    grouped = {}
    for item in iterable:
        grouped.setdefault(key(item), []).append(item)
    return grouped.items()
