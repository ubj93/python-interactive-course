"""Reference solutions for bytes_to_human."""

UNITS = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]


# Best practice: divide down through the unit list; stop when the value is small enough
# or when we run out of units.
def bytes_to_human(n: int) -> str:
    if n < 0:
        raise ValueError("byte count must be non-negative")
    value = float(n)
    unit = UNITS[0]
    for unit in UNITS:
        if value < 1024 or unit == UNITS[-1]:
            break
        value /= 1024
    if unit == "B":
        return f"{n} B"
    return f"{value:.1f} {unit}"


# Clever: compute the exponent directly with a while loop on the index.
def bytes_to_human_index(n: int) -> str:
    if n < 0:
        raise ValueError("byte count must be non-negative")
    i = 0
    while n >= 1024 ** (i + 1) and i < len(UNITS) - 1:
        i += 1
    if i == 0:
        return f"{n} B"
    return f"{n / 1024 ** i:.1f} {UNITS[i]}"
