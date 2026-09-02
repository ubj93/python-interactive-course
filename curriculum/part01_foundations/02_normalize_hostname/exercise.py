"""Normalize a hostname.

Help-desk staff type hostnames into a form by hand. Before we look a machine up
in the MDM we need to clean the input. Write `normalize_hostname(raw)` that:

1. removes leading and trailing whitespace (spaces, tabs, newlines),
2. converts to lowercase,
3. drops any domain suffix: keep only the part before the first '.',
4. replaces every underscore with a hyphen.

Return the cleaned name. If nothing is left after cleaning, return an empty string.

Examples:
    >>> normalize_hostname("  MBP-J-DOE \\n")
    'mbp-j-doe'
    >>> normalize_hostname("win_lab_01.corp.example.com")
    'win-lab-01'
    >>> normalize_hostname("   ")
    ''
"""


def normalize_hostname(raw: str) -> str:
    raise NotImplementedError("write normalize_hostname")
