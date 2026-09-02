"""Enrollment reconciler: three sources, one action list.

Three systems disagree about the fleet and someone has to produce the work
list. Each source is a list of dicts:

    mdm:       {"serial": "C02ABC", "user": "alice@example.com"}      # user may be "" or None
    directory: {"user": "alice@example.com", "active": True}
    inventory: {"serial": "C02ABC", "owner": "alice@example.com", "status": "in_use"}

Inventory status is one of "in_use", "in_stock", "retired" (anything else is
unknown). Serials arrive in mixed case with stray whitespace; compare them
uppercased and stripped. Users and owners compare lowercased and stripped.
Rows with an empty or missing serial are skipped. The same serial may appear
twice in one source.

index_by_serial(rows) -> (dict, set)
- {normalised_serial: first_row_seen}, and the set of serials seen more than once

active_users(directory) -> set
- normalised users whose "active" is truthy

decide(mdm_row, inv_row, active, duplicate_in=None) -> (action, reason) or None
- `mdm_row` / `inv_row` are the matching rows or None when the serial is absent
  from that source; `duplicate_in` is None, "mdm" or "inventory"
- apply the FIRST matching rule:
   1. duplicate_in is set          -> investigate, "duplicate rows in <source>"
   2. in mdm, not in inventory     -> investigate, "not in inventory"
   3. status retired               -> retire, "retired in inventory" if in mdm; else None
   4. status in_stock              -> investigate, "in stock but enrolled" if in mdm; else None
   5. status not in_use            -> investigate, "unknown inventory status '<status>'"
   6. no owner                     -> investigate, "no owner"
   7. owner not active             -> investigate, "owner <owner> not active in directory"
   8. not in mdm                   -> enroll, "not enrolled"
   9. mdm user != owner            -> reassign, "mdm user <user> != owner <owner>"
                                      (write "none" for an empty mdm user)
  10. otherwise                    -> None (nothing to do)
- statuses compare lowercased and stripped; reasons use normalised values

reconcile(mdm, directory, inventory) -> list of dicts
- {"serial": ..., "action": ..., "reason": ...} for every serial in either
  mdm or inventory that gets an action, sorted by (action, serial)

Examples:
    >>> decide({"serial": "A", "user": "Bob@example.com"}, {"serial": "A", "owner": "alice@example.com", "status": "in_use"}, {"alice@example.com"})
    ('reassign', 'mdm user bob@example.com != owner alice@example.com')
    >>> decide(None, {"serial": "A", "owner": "alice@example.com", "status": "in_use"}, {"alice@example.com"})
    ('enroll', 'not enrolled')
    >>> decide({"serial": "A", "user": ""}, None, set())
    ('investigate', 'not in inventory')
"""
from typing import Dict, List, Optional, Set, Tuple


def index_by_serial(rows: List[dict]) -> Tuple[Dict[str, dict], Set[str]]:
    raise NotImplementedError("write index_by_serial")


def active_users(directory: List[dict]) -> Set[str]:
    raise NotImplementedError("write active_users")


def decide(mdm_row: Optional[dict], inv_row: Optional[dict], active: Set[str], duplicate_in: Optional[str] = None) -> Optional[Tuple[str, str]]:
    raise NotImplementedError("write decide")


def reconcile(mdm: List[dict], directory: List[dict], inventory: List[dict]) -> List[Dict[str, str]]:
    raise NotImplementedError("write reconcile")
