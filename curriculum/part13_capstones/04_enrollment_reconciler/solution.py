"""Reference solution for enrollment_reconciler."""
from typing import Dict, List, Optional, Set, Tuple


def _serial(value) -> str:
    return (value or "").strip().upper()


def _user(value) -> str:
    return (value or "").strip().lower()


# Best practice: normalise at the boundary, once. After index_by_serial every
# lookup is by the canonical serial and nobody downstream thinks about casing.
def index_by_serial(rows: List[dict]) -> Tuple[Dict[str, dict], Set[str]]:
    by_serial: Dict[str, dict] = {}
    duplicates: Set[str] = set()
    for row in rows:
        serial = _serial(row.get("serial"))
        if not serial:
            continue
        if serial in by_serial:
            duplicates.add(serial)
        else:
            by_serial[serial] = row
    return by_serial, duplicates


def active_users(directory: List[dict]) -> Set[str]:
    return {_user(row.get("user")) for row in directory if row.get("active") and _user(row.get("user"))}


# The rules are a numbered ladder in the spec, so the code is the same ladder:
# guard clauses in spec order, each returning as soon as it applies. Reordering
# any two of them changes the answer, which is exactly why the spec numbers them.
def decide(mdm_row: Optional[dict], inv_row: Optional[dict], active: Set[str], duplicate_in: Optional[str] = None) -> Optional[Tuple[str, str]]:
    if duplicate_in:
        return "investigate", f"duplicate rows in {duplicate_in}"
    if inv_row is None:
        return "investigate", "not in inventory"
    status = (inv_row.get("status") or "").strip().lower()
    if status == "retired":
        return ("retire", "retired in inventory") if mdm_row is not None else None
    if status == "in_stock":
        return ("investigate", "in stock but enrolled") if mdm_row is not None else None
    if status != "in_use":
        return "investigate", f"unknown inventory status '{status}'"
    owner = _user(inv_row.get("owner"))
    if not owner:
        return "investigate", "no owner"
    if owner not in active:
        return "investigate", f"owner {owner} not active in directory"
    if mdm_row is None:
        return "enroll", "not enrolled"
    mdm_user = _user(mdm_row.get("user"))
    if mdm_user != owner:
        return "reassign", f"mdm user {mdm_user or 'none'} != owner {owner}"
    return None


def reconcile(mdm: List[dict], directory: List[dict], inventory: List[dict]) -> List[Dict[str, str]]:
    mdm_by, mdm_dup = index_by_serial(mdm)
    inv_by, inv_dup = index_by_serial(inventory)
    active = active_users(directory)
    actions: List[Dict[str, str]] = []
    for serial in set(mdm_by) | set(inv_by):
        duplicate_in = "mdm" if serial in mdm_dup else "inventory" if serial in inv_dup else None
        verdict = decide(mdm_by.get(serial), inv_by.get(serial), active, duplicate_in)
        if verdict is not None:
            actions.append({"serial": serial, "action": verdict[0], "reason": verdict[1]})
    return sorted(actions, key=lambda a: (a["action"], a["serial"]))
