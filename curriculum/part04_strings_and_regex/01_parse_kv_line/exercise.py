"""Parse a key=value line.

Several agents report state as one line of "key=value" pairs separated by
semicolons, and the people who write those agents are not careful about spaces:

    serial=C02XG1234ABC; os = macOS 14.5 ;managed=true;

Write `parse_kv_line(line)` that turns such a line into a dict of strings.

Rules:
- fields are separated by ';'
- each field is split on its FIRST '=' only; the value may itself contain '='
- keys and values are stripped of surrounding whitespace
- fields that are empty after stripping (a trailing ';', double ';;') are skipped
- when the same key appears twice, the later value wins
- an empty or whitespace-only line gives {}
- a non-empty field without '=' raises ValueError
- a field whose key is empty after stripping ("=value") raises ValueError

Examples:
    >>> parse_kv_line("serial=C02XG1234ABC; os = macOS 14.5 ;managed=true;")
    {'serial': 'C02XG1234ABC', 'os': 'macOS 14.5', 'managed': 'true'}
    >>> parse_kv_line("token=abc=def")
    {'token': 'abc=def'}
    >>> parse_kv_line("   ")
    {}
"""
from typing import Dict


def parse_kv_line(line: str) -> Dict[str, str]:
    raise NotImplementedError("write parse_kv_line")
