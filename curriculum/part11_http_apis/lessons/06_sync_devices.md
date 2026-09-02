# Sync: plan, then apply

--- teach
### Index both sides by a normalised key
Local and remote both identify a device by serial, but one side says `" c02x "` and the other `"C02X"`. Normalise with `.strip().upper()` and build a dict from serial to record for each side. While indexing, validate: a blank or missing serial, or the same serial twice on one side, raises `ValueError`. Everything is checked **before** the first API call, so a bad file fails the run instead of half of it.
```python
def _index(records, label):
    by_serial = {}
    for record in records:
        serial = str(record.get("serial") or "").strip().upper()
        if not serial:
            raise ValueError(f"record without a serial: {record!r}")
        if serial in by_serial:
            raise ValueError(f"duplicate serial {serial} in {label}")
        by_serial[serial] = record
    return by_serial
```

--- code
Build `by_serial`, a dict from normalised serial (`strip().upper()`) to record, raising `ValueError` on a duplicate. Then print `sorted(by_serial)`.
```python
records = [{"serial": " c02x ", "name": "mbp"}, {"serial": "A1", "name": "air"}]
```
expect: ['A1', 'C02X']
check: by_serial["C02X"]["name"] == "mbp"
solution: by_serial = {}
solution: for record in records:
solution:     serial = record["serial"].strip().upper()
solution:     if serial in by_serial:
solution:         raise ValueError(f"duplicate serial {serial}")
solution:     by_serial[serial] = record
solution: print(sorted(by_serial))
> The key is the cleaned serial, the value is the original record. Checking `serial in by_serial` before storing catches a duplicate on the spot.

--- predict
What does this print?
```python
print(" c02x ".strip().upper())
```
answer: C02X
> `strip` removes the padding and `upper` folds the case, so both sides produce the same key.

--- teach
### Three groups from two sets of keys
With both dicts keyed the same way, set arithmetic names the groups: in local only means create, in remote only means delete, in both means compare. Walking `sorted(set(local_by) | set(remote_by))` visits every serial once in a deterministic order, and `.get(serial)` on each dict tells you which side has it.
```python
for serial in sorted(set(local_by) | set(remote_by)):
    mine, theirs = local_by.get(serial), remote_by.get(serial)
    if theirs is None:      # create
    elif mine is None:      # delete, by theirs["id"]
    else:                   # compare fields
```
Sorted order makes logs diffable and tests simple.

--- predict
What does this print?
```python
local = {"A1", "B2", "C3"}
remote = {"A1", "Z9"}
print(sorted(local - remote), sorted(remote - local))
```
answer: ['B2', 'C3'] ['Z9']
> `local - remote` is what only local has (to create); `remote - local` is what only remote has (to delete). `A1` is in both.

--- teach
### Send only what changed
For a device on both sides, compare each field in `fields`. A field missing on either side counts as `None`, so use `.get(f)`. The update carries only the differing fields, with the local value: smaller requests, readable logs, and nothing you do not own gets clobbered. An empty `changes` dict means unchanged. A create record holds `serial` plus every field, missing ones as `None`.
```python
changes = {f: mine.get(f) for f in fields if mine.get(f) != theirs.get(f)}
record = {"serial": serial, **{f: mine.get(f) for f in fields}}
```

--- code
Set `changes` to the fields from `fields` whose local value differs from the remote one, holding the local value. A missing field counts as `None`.
```python
fields = ("name", "group")
mine = {"serial": "A1", "name": "mbp-a"}
theirs = {"id": "17", "serial": "A1", "name": "mbp-a", "group": "eng"}
```
check: changes == {"group": None}
solution: changes = {f: mine.get(f) for f in fields if mine.get(f) != theirs.get(f)}
> `name` matches, so it is left out. `group` is missing locally, so `mine.get("group")` is `None`, which differs from `"eng"` and becomes the update.

--- fill
Complete the comprehension so `changes` holds only fields whose local value differs.
```python
changes = {f: mine.get(f) for f in fields if mine.get(f) ___ theirs.get(f)}
```
answer: !=
> The condition keeps a field only when the two sides disagree. `.get` makes a missing field `None` on either side.

--- teach
### Plan first, apply second
Compute the actions as plain data (a dict of lists), then loop over them calling `client.create`, `client.update(remote_id, changes)` and `client.delete(remote_id)`, in that order. The planner is a pure function you can test with no client, and `dry_run` simply skips the apply step. The tests pass a fake client that records every call, the same injection idea as `runner` and `get`.
```python
plan = plan_sync(local, remote, fields)
if not dry_run:
    for _serial, record in plan["create"]:
        client.create(record)
    for _serial, remote_id, changes in plan["update"]:
        client.update(remote_id, changes)
    for _serial, remote_id in plan["delete"]:
        client.delete(remote_id)
```
The summary lists the normalised serials of each group, sorted.

--- quiz
`sync_devices(local, remote, client, dry_run=True)` finds one device to update. What happens?
- [ ] `client.update` is called and the summary is returned
- [x] The summary lists it under `"updated"` and the client is never called
- [ ] It returns `None`
> Dry run means "show me the plan". The planning half runs in full; the applying half is skipped.

--- exercise 11.6

--- recap
- Index each side by `serial.strip().upper()`; blanks and duplicates raise before any call.
- `local - remote` creates, `remote - local` deletes, the intersection compares.
- Updates carry only the fields that differ; missing fields count as `None`.
- Plan as data, then apply in order: create, update, delete. `dry_run` skips the apply.
