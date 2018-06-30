def parse_size(s: str):
    last = s[-1]
    value = float(s[:-1])
    if last == 'K':
        value *= 1024
    elif last == 'M':
        value *= 1024 * 1024
    elif last == 'G':
        value *= 1024 * 1024 * 1024
    elif last == 'T':
        value *= 1024 * 1024 * 1024 * 1024
    return value
