"""Invert a user-to-devices index.

The directory gives us a mapping from username to the list of device serials
assigned to that user. The MDM wants the opposite: serial -> username. Write
`invert_index(user_to_devices)` that builds it.

Rules:
- every serial in every list becomes a key whose value is the username
- keys appear in the order the serials are encountered (users in dict order,
  serials in list order)
- a user with an empty list contributes nothing
- the same serial listed twice under the SAME user is fine (one entry)
- the same serial under TWO DIFFERENT users is a conflict: raise ValueError
  and include the serial in the message
- an empty input gives {}
- do not modify the input

Examples:
    >>> invert_index({"jdoe": ["C02A", "C02B"], "asmith": ["C02C"]})
    {'C02A': 'jdoe', 'C02B': 'jdoe', 'C02C': 'asmith'}
    >>> invert_index({"jdoe": ["C02A"], "asmith": ["C02A"]})
    Traceback (most recent call last):
        ...
    ValueError: serial C02A is assigned to both jdoe and asmith
"""
from typing import Dict, List


def invert_index(user_to_devices: Dict[str, List[str]]) -> Dict[str, str]:
    raise NotImplementedError("write invert_index")
