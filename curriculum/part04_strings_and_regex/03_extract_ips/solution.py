"""Reference solutions for extract_ips."""
import re
from typing import List

# Lookarounds forbid a digit or dot on either side without consuming it, so a candidate
# glued to a longer dotted number is rejected while punctuation such as ':' or ')' is fine.
CANDIDATE = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")


def _valid_octet(octet: str) -> bool:
    if len(octet) > 1 and octet[0] == "0":
        return False
    return 0 <= int(octet) <= 255


# Best practice: regex for shape, Python for range. The pattern stays readable and the
# numeric rules live where they are easy to test and explain.
def extract_ips(text: str) -> List[str]:
    return [
        candidate
        for candidate in CANDIDATE.findall(text)
        if all(_valid_octet(o) for o in candidate.split("."))
    ]


# Clever: let ipaddress do the validation. It rejects out-of-range and leading-zero octets
# (3.9.5+ / 3.10), so the check collapses to "does it parse". Slower, but obviously correct.
def extract_ips_ipaddress(text: str) -> List[str]:
    import ipaddress

    found = []
    for candidate in CANDIDATE.findall(text):
        try:
            ipaddress.IPv4Address(candidate)
        except ValueError:
            continue
        if any(len(o) > 1 and o[0] == "0" for o in candidate.split(".")):
            continue  # older 3.9 releases accept leading zeros; keep the rule explicit
        found.append(candidate)
    return found
