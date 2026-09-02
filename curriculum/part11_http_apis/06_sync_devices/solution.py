"""Reference solutions for sync_devices."""
from typing import Any, Dict, Iterable, List, Tuple


def _norm_serial(record: Dict[str, Any]) -> str:
    serial = str(record.get("serial") or "").strip().upper()
    if not serial:
        raise ValueError(f"record without a serial: {record!r}")
    return serial


def _index(records: List[Dict[str, Any]], label: str) -> Dict[str, Dict[str, Any]]:
    by_serial: Dict[str, Dict[str, Any]] = {}
    for record in records:
        serial = _norm_serial(record)
        if serial in by_serial:
            raise ValueError(f"duplicate serial {serial} in {label}")
        by_serial[serial] = record
    return by_serial


# Plan first, act second. The plan is pure data (no side effects), which is what makes
# dry_run free and the diff testable without any client at all.
def plan_sync(
    local: List[Dict[str, Any]],
    remote: List[Dict[str, Any]],
    fields: Iterable[str] = ("name", "group"),
) -> Dict[str, List[Tuple[Any, ...]]]:
    fields = tuple(fields)
    local_by = _index(local, "local")
    remote_by = _index(remote, "remote")
    plan: Dict[str, List[Tuple[Any, ...]]] = {"create": [], "update": [], "delete": [], "unchanged": []}
    for serial in sorted(set(local_by) | set(remote_by)):
        mine, theirs = local_by.get(serial), remote_by.get(serial)
        if theirs is None:
            record = {"serial": serial}
            record.update({f: mine.get(f) for f in fields})
            plan["create"].append((serial, record))
        elif mine is None:
            plan["delete"].append((serial, theirs["id"]))
        else:
            changes = {f: mine.get(f) for f in fields if mine.get(f) != theirs.get(f)}
            if changes:
                plan["update"].append((serial, theirs["id"], changes))
            else:
                plan["unchanged"].append((serial,))
    return plan


# Best practice: the sync function is now a thin driver: validate (inside plan_sync),
# then creates, updates, deletes in that order. Sorting happened once in plan_sync.
def sync_devices(
    local: List[Dict[str, Any]],
    remote: List[Dict[str, Any]],
    client: Any,
    fields: Iterable[str] = ("name", "group"),
    dry_run: bool = False,
) -> Dict[str, List[str]]:
    plan = plan_sync(local, remote, fields)
    if not dry_run:
        for _serial, record in plan["create"]:
            client.create(record)
        for _serial, remote_id, changes in plan["update"]:
            client.update(remote_id, changes)
        for _serial, remote_id in plan["delete"]:
            client.delete(remote_id)
    return {
        "created": [s for s, *_ in plan["create"]],
        "updated": [s for s, *_ in plan["update"]],
        "deleted": [s for s, *_ in plan["delete"]],
        "unchanged": [s for s, *_ in plan["unchanged"]],
    }


# Clever: set arithmetic names the three groups directly, which reads like the spec.
# Same result; the version above is preferred because it walks every serial once.
def sync_devices_sets(
    local: List[Dict[str, Any]],
    remote: List[Dict[str, Any]],
    client: Any,
    fields: Iterable[str] = ("name", "group"),
    dry_run: bool = False,
) -> Dict[str, List[str]]:
    fields = tuple(fields)
    local_by, remote_by = _index(local, "local"), _index(remote, "remote")
    to_create = sorted(set(local_by) - set(remote_by))
    to_delete = sorted(set(remote_by) - set(local_by))
    both = sorted(set(local_by) & set(remote_by))
    updates = {
        s: {f: local_by[s].get(f) for f in fields if local_by[s].get(f) != remote_by[s].get(f)}
        for s in both
    }
    to_update = [s for s in both if updates[s]]
    if not dry_run:
        for s in to_create:
            client.create({"serial": s, **{f: local_by[s].get(f) for f in fields}})
        for s in to_update:
            client.update(remote_by[s]["id"], updates[s])
        for s in to_delete:
            client.delete(remote_by[s]["id"])
    return {
        "created": to_create,
        "updated": to_update,
        "deleted": to_delete,
        "unchanged": [s for s in both if not updates[s]],
    }
