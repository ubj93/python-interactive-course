"""Reference solutions for invert_index."""
from typing import Dict, List


# Best practice: a nested loop with an explicit conflict check before each insert.
# A dict comprehension would silently keep the last user; here duplicates are an error.
def invert_index(user_to_devices: Dict[str, List[str]]) -> Dict[str, str]:
    device_to_user: Dict[str, str] = {}
    for user, serials in user_to_devices.items():
        for serial in serials:
            owner = device_to_user.get(serial)
            if owner is not None and owner != user:
                raise ValueError(f"serial {serial} is assigned to both {owner} and {user}")
            device_to_user[serial] = user
    return device_to_user


# Clever: setdefault returns the existing value, so "insert if new, else check" is one call.
# Compact, but the conflict test hides inside an assignment; say so if you write it in an interview.
def invert_index_setdefault(user_to_devices: Dict[str, List[str]]) -> Dict[str, str]:
    device_to_user: Dict[str, str] = {}
    for user, serials in user_to_devices.items():
        for serial in serials:
            owner = device_to_user.setdefault(serial, user)
            if owner != user:
                raise ValueError(f"serial {serial} is assigned to both {owner} and {user}")
    return device_to_user
