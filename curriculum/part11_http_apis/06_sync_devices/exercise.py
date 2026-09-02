"""Sync a local device list to a remote API.

Our source of truth is a CSV of devices (serial, name, group). The MDM has its
own copy, addressed by a server-side id. Write `sync_devices(local, remote,
client, fields=("name", "group"), dry_run=False)` that works out the difference
and pushes it through `client`, returning a summary.

Inputs:
- `local`: list of dicts with "serial" plus the `fields`; extra keys are ignored
- `remote`: list of dicts with "id", "serial" plus the `fields`; extra keys
  (last_seen, os_version, ...) are ignored
- `client`: an object with `create(record)`, `update(remote_id, changes)` and
  `delete(remote_id)`. Tests pass a fake that records every call.

Matching:
- devices match on serial after normalising with .strip().upper()
- a record with a missing or blank serial raises ValueError; the same serial
  twice within local, or twice within remote, raises ValueError. Validate
  everything before the first client call.

Actions, in this order, each group sorted by normalised serial:
1. create: in local but not remote -> client.create({"serial": S, field: value, ...})
   containing only "serial" and the `fields` (missing fields are sent as None)
2. update: in both, and at least one field differs -> client.update(remote_id, changes)
   where changes holds only the fields that differ, with the local value. A field
   missing on either side counts as None.
3. delete: in remote but not local -> client.delete(remote_id)

Return {"created": [...], "updated": [...], "deleted": [...], "unchanged": [...]}
with sorted normalised serials. With dry_run=True return the same summary but
make no client calls at all.

Examples:
    >>> local = [{"serial": "c02x", "name": "mbp-jdoe", "group": "eng"}]
    >>> remote = [{"id": "17", "serial": "C02X", "name": "mbp-jdoe", "group": "sales"}]
    >>> sync_devices(local, remote, client)          # calls client.update("17", {"group": "eng"})
    {'created': [], 'updated': ['C02X'], 'deleted': [], 'unchanged': []}
"""
from typing import Any, Dict, Iterable, List


def sync_devices(
    local: List[Dict[str, Any]],
    remote: List[Dict[str, Any]],
    client: Any,
    fields: Iterable[str] = ("name", "group"),
    dry_run: bool = False,
) -> Dict[str, List[str]]:
    raise NotImplementedError("write sync_devices")
