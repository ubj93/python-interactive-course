# Capstone: enrollment reconciler

--- teach
### The ticket
Three systems describe the fleet and disagree. MDM has `{serial, user}`, the directory has `{user, active}`, inventory has `{serial, owner, status}`. Produce a work list: for every serial in MDM or inventory, an action (`enroll`, `retire`, `reassign`, `investigate`) and a reason, sorted by action then serial. Serials compare uppercased and stripped; users, owners and statuses compare lowercased and stripped. Empty serials are skipped; a serial that appears twice in one source is flagged.

The docstring gives ten numbered rules and says "apply the FIRST matching rule". That sentence is the whole design: the code is the same ladder, in the same order. Write the rules down, then read the tests for `decide`; each test pins one rung.

--- teach
### Two normalisers, three helpers, one composer
```python
def _serial(value):
    return (value or "").strip().upper()

def _user(value):
    return (value or "").strip().lower()
```
- `index_by_serial(rows)` returns `({serial: first_row}, duplicates)`; the first row wins, later rows only add to the set.
- `active_users(directory)` is a set comprehension over rows whose `active` is truthy and whose user is non-empty.
- `decide(mdm_row, inv_row, active, duplicate_in)` is the rule ladder; it returns `(action, reason)` or `None`.
- `reconcile` indexes both sources, walks the union of serials, calls `decide`, and sorts.

Every read of a serial or user goes through a normaliser. `(value or "")` handles a missing key and a `None` in one move. That one habit removes half the messy-data bugs before they exist.

--- code
Write the two normalisers: `_serial(value)` returns the value stripped and uppercased, `_user(value)` stripped and lowercased, and both return `""` for `None`.
```python
# your code here
```
check: _serial(" c02abc ") == "C02ABC"
check: _serial(None) == ""
check: _user(" Alice@Example.com") == "alice@example.com"
solution: def _serial(value):
solution:     return (value or "").strip().upper()
solution: def _user(value):
solution:     return (value or "").strip().lower()
> `(value or "")` turns `None` into an empty string before any method is called, so a row with a missing key cannot crash the parse. Two four-line functions, called everywhere, and casing is never a bug again.

--- predict
What does this print?
```python
by_serial, dups = {}, set()
for raw in ["A", " a ", "B"]:
    serial = (raw or "").strip().upper()
    if serial in by_serial:
        dups.add(serial)
    else:
        by_serial[serial] = raw
print(sorted(by_serial), sorted(dups))
```
answer: ['A', 'B'] ['A'] | ['A','B'] ['A']
> `" a "` normalises to `"A"`, which is already a key, so it goes into the duplicate set and the first row stays. `B` is new. Membership on a dict is O(1), which is why a dict is the index.

--- teach
### The ladder: guard clauses in spec order
Each rule is an `if` that returns as soon as it applies; whatever is below can assume it did not. Rules 3 and 4 have a twist: a retired or in-stock device that is not in MDM needs nothing, so they return `None` instead of falling through.
```python
if duplicate_in:
    return "investigate", f"duplicate rows in {duplicate_in}"
if inv_row is None:
    return "investigate", "not in inventory"
status = (inv_row.get("status") or "").strip().lower()
if status == "retired":
    return ("retire", "retired in inventory") if mdm_row is not None else None
...
mdm_user = _user(mdm_row.get("user"))
if mdm_user != owner:
    return "reassign", f"mdm user {mdm_user or 'none'} != owner {owner}"
return None
```
Reasons use the normalised values, and an empty MDM user is written as `none`. Reordering any two rungs changes an answer somewhere in the tests.

--- code
Write the first two rungs of the ladder and nothing else: rule 1 (duplicate) and rule 2 (not in inventory), then `return None`.
```python
def decide(mdm_row, inv_row, active, duplicate_in=None):
```
check: decide(None, None, set(), "mdm") == ("investigate", "duplicate rows in mdm")
check: decide({"serial": "A"}, None, set()) == ("investigate", "not in inventory")
check: decide({"serial": "A"}, {"serial": "A"}, set()) is None
solution:     if duplicate_in:
solution:         return "investigate", f"duplicate rows in {duplicate_in}"
solution:     if inv_row is None:
solution:         return "investigate", "not in inventory"
solution:     return None
> Each rung is a guard that returns a tuple; `return "investigate", "..."` builds the tuple without brackets. The duplicate rung comes first, so a duplicated serial is investigated even when it is also missing from inventory. The remaining eight rungs slot in above the final `return None`.

--- quiz
A serial is in inventory (`in_use`, owner `zed@example.com`) but not in MDM, and `zed` is not an active directory user. What does `decide` return?
- [ ] `('enroll', 'not enrolled')`
- [x] `('investigate', 'owner zed@example.com not active in directory')`
- [ ] `None`
> Rule 7 (owner not active) sits above rule 8 (not in MDM), so the inactive owner is caught first. Enrolling a laptop for someone who has left is exactly the mistake the ladder order prevents.

--- fill
Complete the loop in `reconcile` so it visits every serial that appears in either source.
```python
for serial in set(mdm_by).___(set(inv_by)):
    verdict = decide(mdm_by.get(serial), inv_by.get(serial), active, duplicate_in)
```
answer: union
> `set.union` (or the `|` operator) gives serials in MDM, in inventory, or both. `.get` then returns `None` for the side that lacks the serial, which is exactly what `decide` expects. Work out `duplicate_in` from the two duplicate sets first, MDM taking precedence.

--- teach
### Budget: 45 minutes
- 0–6: read twice; copy the ten rules into comments inside `decide`, in order.
- 6–10: `_serial`, `_user`, signatures, `reconcile` skeleton.
- 10–18: `index_by_serial` and `active_users`; test with one duplicate, one blank, one `None`.
- 18–33: `decide`, one rung at a time, running the four `decide` tests as you go.
- 33–40: `reconcile`: union of serials, `duplicate_in`, sort by `(action, serial)`.
- 40–45: the messy-sources test; nearly every failure here is a missing normaliser.

If time runs short, ship `decide` complete and `reconcile` rough: the ladder is where the marks are.

--- exercise 13.4

--- recap
- `_serial` and `_user` normalise at the boundary; call them everywhere.
- Index with a dict; first row wins, repeats go into a duplicate set.
- `decide` is guard clauses in spec order; rules 3 and 4 return `None` when the device is not in MDM.
- `reconcile` walks the union of both serial sets and sorts by `(action, serial)`.
