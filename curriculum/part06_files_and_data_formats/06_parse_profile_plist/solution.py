"""Reference solutions for parse_profile_plist."""
import plistlib
from typing import Any, Dict
from xml.parsers.expat import ExpatError


# Best practice: parse, validate the shape, then build the summary with .get() defaults.
# Chaining the parser's exception with `from` keeps the real cause in the traceback.
def parse_profile_plist(data: bytes) -> Dict[str, Any]:
    try:
        root = plistlib.loads(data)
    except (plistlib.InvalidFileException, ExpatError) as e:
        raise ValueError(f"not a valid plist: {e}") from e
    if not isinstance(root, dict) or root.get("PayloadType") != "Configuration":
        raise ValueError("not a configuration profile")

    payloads = []
    for payload in root.get("PayloadContent", []):
        ptype = payload.get("PayloadType", "")
        payloads.append(
            {
                "type": ptype,
                "identifier": payload.get("PayloadIdentifier", ""),
                "display_name": payload.get("PayloadDisplayName", ptype),
            }
        )
    return {
        "identifier": root.get("PayloadIdentifier", ""),
        "display_name": root.get("PayloadDisplayName", ""),
        "organization": root.get("PayloadOrganization", ""),
        "removal_disallowed": bool(root.get("PayloadRemovalDisallowed", False)),
        "payload_count": len(payloads),
        "payload_types": sorted({p["type"] for p in payloads}),
        "payloads": payloads,
    }


# Clever: a tiny helper that loads-or-raises makes the main function read top to bottom,
# and is reusable by every other plist function in the same script.
def _load_plist(data: bytes) -> Any:
    try:
        return plistlib.loads(data)
    except (plistlib.InvalidFileException, ExpatError) as e:
        raise ValueError(f"not a valid plist: {e}") from e


def parse_profile_plist_helper(data: bytes) -> Dict[str, Any]:
    root = _load_plist(data)
    if not isinstance(root, dict) or root.get("PayloadType") != "Configuration":
        raise ValueError("not a configuration profile")
    payloads = [
        {
            "type": p.get("PayloadType", ""),
            "identifier": p.get("PayloadIdentifier", ""),
            "display_name": p.get("PayloadDisplayName", p.get("PayloadType", "")),
        }
        for p in root.get("PayloadContent", [])
    ]
    return {
        "identifier": root.get("PayloadIdentifier", ""),
        "display_name": root.get("PayloadDisplayName", ""),
        "organization": root.get("PayloadOrganization", ""),
        "removal_disallowed": bool(root.get("PayloadRemovalDisallowed", False)),
        "payload_count": len(payloads),
        "payload_types": sorted({p["type"] for p in payloads}),
        "payloads": payloads,
    }
