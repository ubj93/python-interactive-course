"""Format a byte count for humans.

Write `bytes_to_human(n)` that turns a non-negative integer byte count into a
string using binary units (1 KiB = 1024 B):

- units in order: B, KiB, MiB, GiB, TiB, PiB
- pick the largest unit where the value is at least 1
- show one decimal place for every unit except bytes, which are whole numbers
- exactly one space between number and unit
- negative input: raise ValueError

Examples:
    >>> bytes_to_human(0)
    '0 B'
    >>> bytes_to_human(1023)
    '1023 B'
    >>> bytes_to_human(1024)
    '1.0 KiB'
    >>> bytes_to_human(1536)
    '1.5 KiB'
    >>> bytes_to_human(5 * 1024 ** 3)
    '5.0 GiB'
"""


def bytes_to_human(n: int) -> str:
    raise NotImplementedError("write bytes_to_human")
