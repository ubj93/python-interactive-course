"""Greet a device.

Write `greet_device(hostname, os_name, ram_gb)` that returns a one-line
status string exactly in this shape:

    Hello, MBP-J-DOE! You are running macOS with 16 GB of RAM.

Rules:
- `ram_gb` is an int; keep it as a plain number (no decimals, no thousands separators).
- Do not add a trailing newline.

Examples:
    >>> greet_device("MBP-J-DOE", "macOS", 16)
    'Hello, MBP-J-DOE! You are running macOS with 16 GB of RAM.'
    >>> greet_device("win-lab-01", "Windows", 8)
    'Hello, win-lab-01! You are running Windows with 8 GB of RAM.'
"""


def greet_device(hostname: str, os_name: str, ram_gb: int) -> str:
    raise NotImplementedError("write greet_device")
