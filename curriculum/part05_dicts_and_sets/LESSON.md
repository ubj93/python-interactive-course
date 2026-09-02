# Part 5 · Dictionaries and sets

> **What you will be able to do:** count, group, look up, invert, diff and merge
> fleet data with the two data structures that do most of the work in real CPE
> scripts, and explain why they are fast. About ninety minutes plus the exercises.

## Why this part matters

Almost every fleet question is a dictionary question in disguise. "How many devices
per OS?" is counting. "Which devices belong to Finance?" is grouping. "Which serials
are in the MDM but not in the inventory?" is a set difference. "Apply this override
to the base config" is a recursive merge. Interviewers love these because they are
small, have edge cases, and reveal whether you reach for the right structure or
write nested loops.

## 1. Creating dictionaries

```python
>>> device = {"hostname": "mbp-j-doe", "os": "macOS", "ram_gb": 16}
>>> dict(hostname="mbp-j-doe", os="macOS")        # keyword form, keys must be identifiers
>>> dict([("a", 1), ("b", 2)])                     # from pairs
{'a': 1, 'b': 2}
>>> dict(zip(["serial", "os"], ["C02X", "macOS"]))
{'serial': 'C02X', 'os': 'macOS'}
>>> dict.fromkeys(["a", "b"], 0)
{'a': 0, 'b': 0}
>>> {}                                             # empty dict; set() is the empty set
{}
```

**Gotcha:** `dict.fromkeys(keys, [])` shares *one* list between every key. Appending
to `d["a"]` changes `d["b"]`. Use a comprehension, `{k: [] for k in keys}`, when the
value is mutable.

Keys can be any hashable value (section 9). Values can be anything.

## 2. Reading and writing

```python
>>> device["os"]                     # 'macOS'
>>> device["serial"]                 # KeyError: 'serial'
>>> device.get("serial")             # None
>>> device.get("serial", "unknown")  # 'unknown'
>>> "serial" in device               # False   (tests keys, not values)
>>> device["serial"] = "C02X"        # insert or overwrite
>>> device.pop("ram_gb")             # 16, and the key is gone
>>> device.pop("missing", None)      # None instead of KeyError
>>> del device["serial"]
>>> device.setdefault("tags", []).append("laptop")   # create-if-missing, then use
>>> device.update({"os": "macOS 14"}, ram_gb=32)     # merge in place
>>> len(device), list(device)                        # size, keys
```

| Need | Idiom | Not |
|---|---|---|
| value, error if absent | `d[k]` | |
| value or default | `d.get(k, default)` | `d[k] if k in d else default` |
| value, inserting default | `d.setdefault(k, default)` | `if k not in d: d[k] = default` then `d[k]` |
| remove and return | `d.pop(k)` / `d.pop(k, None)` | `v = d[k]; del d[k]` |
| does key exist | `k in d` | `k in d.keys()` (works, redundant) |
| does value exist | `v in d.values()` | a loop |

`get` never inserts; `setdefault` does. `get(k, [])` builds the default list even
when it is not used, which is fine for small defaults and wasteful for big ones.

### Views

```python
>>> for key in device: ...                 # keys
>>> for key, value in device.items(): ...  # pairs, the usual loop
>>> device.keys() & {"os", "serial"}       # keys() behaves like a set
{'os'}
```

`keys()`, `values()` and `items()` are live views: they change when the dict does
and cost nothing to create. Wrap in `list(...)` when you need a snapshot.

## 3. Counting and grouping

The two idioms you must be able to write without thinking.

```python
counts = {}
for d in devices:
    os_name = d.get("os") or "unknown"
    counts[os_name] = counts.get(os_name, 0) + 1
```

```python
groups = {}
for d in devices:
    groups.setdefault(d["department"], []).append(d["hostname"])
```

The standard library has both wrapped up: `collections.Counter` for counting and
`collections.defaultdict(list)` for grouping. You meet them properly in Part 10;
here we practise the plain-dict versions because they are what interviewers ask
you to write by hand, and because you should be able to explain what the helpers
save you.

```python
>>> from collections import Counter
>>> Counter(d["os"] for d in devices).most_common(2)
[('macOS', 812), ('Windows', 143)]
```

**Gotcha:** `Counter.most_common` breaks ties by insertion order, not
alphabetically. When a spec says "ties alphabetical", sort explicitly:
`sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))`. The negated count sorts
descending while the name sorts ascending, in one key.

## 4. Nested dictionaries

Config files and API responses nest. Reading deep paths safely:

```python
>>> profile = {"payload": {"wifi": {"ssid": "corp", "hidden": False}}}
>>> profile["payload"]["wifi"]["ssid"]
'corp'
>>> profile.get("payload", {}).get("vpn", {}).get("server")   # None, no KeyError
```

A chain of `.get(..., {})` is fine for two or three levels. Deeper than that, write a
small function that walks a list of keys, or flatten the structure (exercise 5.7).

Writing deep paths means creating the intermediate dicts:

```python
>>> cfg = {}
>>> cfg.setdefault("payload", {}).setdefault("wifi", {})["ssid"] = "corp"
>>> cfg
{'payload': {'wifi': {'ssid': 'corp'}}}
```

## 5. Ordering guarantees

Since Python 3.7 a `dict` remembers insertion order. This is a language guarantee,
not an implementation detail, and it shapes idioms:

```python
>>> d = {"b": 1, "a": 2}
>>> list(d)                  # ['b', 'a']  insertion order, not sorted
>>> d["b"] = 99              # updating a value keeps its position
>>> list(d)                  # ['b', 'a']
>>> d.pop("b"); d["b"] = 1   # removing and re-adding moves it to the end
>>> list(d)                  # ['a', 'b']
>>> d.popitem()              # ('b', 1)   last in, first out
>>> list(reversed(d))        # 3.8+
```

Consequences:

- "Group by key, keys in first-seen order" needs no extra bookkeeping.
- `dict.fromkeys(items)` deduplicates *and* keeps order; `set(items)` does not.
- Two dicts with the same pairs in different order are still `==`.
- `sorted(d)` gives sorted keys; `dict(sorted(d.items()))` gives a sorted copy.

## 6. Changing a dict while iterating

```python
>>> for k in d:
...     if d[k] is None:
...         del d[k]            # RuntimeError: dictionary changed size during iteration
```

Iterate over a copy of the keys (`for k in list(d)`), or build a new dict with a
comprehension: `{k: v for k, v in d.items() if v is not None}`. Prefer the second;
it says what you want rather than how.

## 7. Dict and set comprehensions (a preview)

Part 9 covers comprehensions properly. The two you need now:

```python
>>> {d["serial"]: d for d in devices}              # index a list by a field
>>> {k: v for k, v in device.items() if v}         # drop falsy values
>>> {d["os"] for d in devices}                     # the distinct values, as a set
>>> {v: k for k, v in user_to_device.items()}      # invert (last one wins on duplicates)
```

Inverting a dict with a comprehension silently drops duplicates. When duplicates
are an error, and in inventory work they usually are, write the loop and raise
(exercise 5.3).

## 8. Sets

A set is an unordered collection of distinct hashable values. Membership and
add/remove are O(1) on average; that is the whole point.

```python
>>> mdm = {"C02A", "C02B", "C02C"}
>>> inventory = {"C02B", "C02C", "C02D"}
>>> mdm | inventory          # union         {'C02A', 'C02B', 'C02C', 'C02D'}
>>> mdm & inventory          # intersection  {'C02B', 'C02C'}
>>> mdm - inventory          # difference    {'C02A'}     in mdm only
>>> inventory - mdm          #               {'C02D'}     in inventory only
>>> mdm ^ inventory          # symmetric difference {'C02A', 'C02D'}
>>> {"C02B"} <= mdm          # subset        True
>>> mdm >= {"C02B"}          # superset      True
>>> mdm.isdisjoint({"X"})    # True
```

| Operator | Method | In-place |
|---|---|---|
| `a \| b` | `a.union(b)` | `a \|= b`, `a.update(b)` |
| `a & b` | `a.intersection(b)` | `a &= b` |
| `a - b` | `a.difference(b)` | `a -= b` |
| `a ^ b` | `a.symmetric_difference(b)` | `a ^= b` |
| `a <= b` | `a.issubset(b)` | |

The methods accept any iterable (`mdm.union(some_list)`); the operators need sets
on both sides. `set()` is the empty set; `{}` is an empty dict.

```python
>>> s = set()
>>> s.add("C02A"); s.add("C02A")        # still one element
>>> s.discard("nope")                   # no error
>>> s.remove("nope")                    # KeyError
>>> sorted(mdm - inventory)             # a set has no order; sort for output
['C02A']
```

**Gotcha:** always `sorted(...)` a set before printing, returning, or comparing
in a test. The iteration order of a set of strings changes between runs (hash
randomisation), so code that relies on it is flaky by design.

`frozenset` is an immutable set, which makes it hashable, which makes it usable as
a dict key or as a member of another set: `{frozenset({"a", "b"})}`.

### The `in` test

```python
>>> allowed = {"macOS", "Windows"}
>>> "Linux" in allowed             # O(1)
>>> "Linux" in ["macOS", "Windows"]   # O(n): fine for 2, wrong for 20 000
```

Turn a list into a set *once* before a loop that tests membership. Doing
`if x in some_list` inside a loop over another list is the quadratic pattern
interviewers wait for.

## 9. Hashability

Dict keys and set members must be hashable: immutable, with a `__hash__` that
agrees with `__eq__`.

```python
>>> {["a", "b"]: 1}            # TypeError: unhashable type: 'list'
>>> {("a", "b"): 1}            # tuples are fine ...
>>> {("a", ["b"]): 1}          # ... unless they contain something unhashable
>>> {{"a": 1}}                 # TypeError: unhashable type: 'dict'
>>> hash(1) == hash(1.0) == hash(True)
True
>>> {1: "int", 1.0: "float", True: "bool"}
{1: 'bool'}
```

That last one is a real trap: `1`, `1.0` and `True` are equal, so they are the
*same key*; the first key object stays and the value is overwritten.

Immutable built-ins (`str`, `int`, `float`, `bool`, `bytes`, `tuple`, `frozenset`,
`None`) are hashable. Mutable ones (`list`, `dict`, `set`) are not. Instances of
your own classes are hashable by identity unless you define `__eq__`, and
`@dataclass(frozen=True)` gives you a value-based hash for free.

## 10. Recursion over nested dicts

Nested configs call for recursive functions. The shape is always the same: handle
the leaf, recurse on the dict.

```python
def walk(d, prefix=""):
    for key, value in d.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            yield from walk(value, path)
        else:
            yield path, value
```

```python
>>> list(walk({"payload": {"wifi": {"ssid": "corp"}}, "name": "Base"}))
[('payload.wifi.ssid', 'corp'), ('name', 'Base')]
```

Rules that keep recursive dict code correct:

- `isinstance(value, dict)` decides whether to recurse. Lists are leaves unless the
  spec says otherwise.
- Do not mutate the input. Build a new dict, and copy nested values you keep
  (`copy.deepcopy` or recursion) so the result does not share structure with
  the arguments.
- Decide the tie rule out loud: "later wins", "lists are replaced, not merged",
  "a dict never merges with a scalar".
- An empty dict is a valid leaf; make sure your base case handles it.

The non-idiomatic version is a loop with a hard-coded depth ("for k1 in d, for k2
in d[k1], ...") that breaks on the fourth level. Interviewers will ask "what if it
nests deeper?" the moment they see it.

## 11. Gotchas in one place

- `d[k]` raises; `d.get(k)` returns `None`. Pick deliberately.
- `dict.fromkeys(keys, [])` shares one list.
- `set(items)` deduplicates but loses order; `dict.fromkeys(items)` keeps it.
- Sets have no stable iteration order; sort before output.
- `{}` is a dict, `set()` is a set.
- `1`, `1.0` and `True` are the same key.
- Never modify a dict while iterating over it.
- Inverting with a comprehension drops duplicates silently.
- `Counter.most_common` does not sort ties alphabetically.

## Interview notes for this part

- **Say the structure before you code it.** "I will build a dict from serial to
  record so lookups are O(1), then one pass over the other list." That sentence is
  most of the marks.
- **Ask about duplicates and missing keys.** "Can a serial appear twice? What
  should happen if a device has no department?" Then write the branch.
- **Name the tie rule for anything ranked.** Counts descending, then name ascending.
- **State the complexity.** Set difference is O(n + m); the nested-loop version is
  O(n × m). Say it even if nobody asks.
- **The trap:** returning a set or the raw dict order where the spec (or a test)
  wants a sorted list. Return `sorted(...)`.

## Exercises

Run `course list 5`, then `course show 5.1`.

1. `count_by_os` · counting with `get`, the "unknown" bucket
2. `group_by_department` · `setdefault` and insertion order
3. `invert_index` · inverting a one-to-many mapping and refusing duplicates
4. `fleet_diff` · set difference, intersection, and sorted output
5. `most_common_apps` · per-device deduplication, then a two-part sort key
6. `merge_configs` · recursive deep merge that never mutates its inputs
7. `flatten_dict` · recursion both ways: nested to dotted keys and back
