"""Summarize a configuration profile.

macOS configuration profiles (.mobileconfig) are property lists. The top level
is a dict with PayloadType "Configuration" and a PayloadContent list of payload
dicts, one per setting group. Write `parse_profile_plist(data)` that takes the
raw bytes of a profile and returns a summary dict with exactly these keys:

    identifier          top-level PayloadIdentifier (str)
    display_name        top-level PayloadDisplayName, "" if missing
    organization        top-level PayloadOrganization, "" if missing
    removal_disallowed  top-level PayloadRemovalDisallowed as a bool, False if missing
    payload_count       number of entries in PayloadContent
    payload_types       sorted list of the distinct PayloadType values in the payloads
    payloads            list of {"type", "identifier", "display_name"} dicts, one per
                        payload, in the order they appear

Rules:
- use plistlib; the data may be XML or binary plist, plistlib.loads handles both
- if the bytes are not a valid plist at all, raise ValueError (plistlib raises
  plistlib.InvalidFileException or xml.parsers.expat.ExpatError; turn both into a
  ValueError and chain the original with `raise ... from`)
- if the top level is not a dict, or its PayloadType is not "Configuration",
  raise ValueError
- a missing PayloadContent means zero payloads
- in each payload, a missing PayloadDisplayName falls back to that payload's
  PayloadType; a missing PayloadIdentifier becomes ""
- payload_types has no duplicates

A real-looking profile is in fixtures/profile.mobileconfig; open it and predict
the summary before running the tests.

Examples:
    >>> data = plistlib.dumps({"PayloadType": "Configuration",
    ...     "PayloadIdentifier": "com.corp.wifi", "PayloadDisplayName": "Wi-Fi",
    ...     "PayloadContent": [{"PayloadType": "com.apple.wifi.managed",
    ...                         "PayloadIdentifier": "com.corp.wifi.1"}]})
    >>> parse_profile_plist(data)
    {'identifier': 'com.corp.wifi', 'display_name': 'Wi-Fi', 'organization': '',
     'removal_disallowed': False, 'payload_count': 1,
     'payload_types': ['com.apple.wifi.managed'],
     'payloads': [{'type': 'com.apple.wifi.managed', 'identifier': 'com.corp.wifi.1',
                   'display_name': 'com.apple.wifi.managed'}]}
"""
import plistlib
from typing import Any, Dict
from xml.parsers.expat import ExpatError


def parse_profile_plist(data: bytes) -> Dict[str, Any]:
    raise NotImplementedError("write parse_profile_plist")
