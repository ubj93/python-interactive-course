# Walking nested dicts

--- teach
### Build the dotted path as you descend
Each nested key extends a path. Keep the path so far as a `prefix` and join with the separator, except at the top level where there is nothing to join to. A conditional expression, `a if cond else b`, picks between the two cases.
```python
path = f"{prefix}{sep}{key}" if prefix else key
```
With `prefix = "payload.wifi"` and `key = "ssid"` that is `"payload.wifi.ssid"`; with an empty prefix it is just `"ssid"`.

--- code
Write `join_path(prefix, key)` that returns the key joined onto the prefix with `sep`, or just the key when the prefix is empty.
```python
sep = "."
def join_path(prefix, key):
```
check: join_path("", "name") == "name"
check: join_path("payload.wifi", "ssid") == "payload.wifi.ssid"
solution:     return f"{prefix}{sep}{key}" if prefix else key
> An empty prefix is falsy, so the `else` branch returns the bare key. Without that branch the top-level keys would come out as `.name`.

--- teach
### Decide what is a leaf
Recurse only into a *non-empty* dict. Everything else is a leaf and is stored as is: numbers, strings, `None`, lists (even lists containing dicts), and an empty dict. `isinstance(value, dict) and value` is the test: an empty dict is falsy, so it falls to the leaf branch.
```python
if isinstance(value, dict) and value:
    ...  # go deeper
else:
    flat[path] = value
```

--- quiz
Which of these is NOT a leaf for `flatten_dict`?
- [ ] `{}`
- [ ] `[1, {"x": 2}]`
- [x] `{"b": 1}`
> Only a non-empty dict is descended into. An empty dict stays a leaf by the spec, and a list is never expanded, whatever it contains.

--- teach
### Recursion with an inner function
Recursion means a function calls itself on a smaller piece. Write an inner function `walk(node, prefix)` that loops over `node.items()`, recurses on nested dicts and otherwise stores the leaf into `flat`, a dict from the outer function. Start it with `walk(d, "")`.
```python
def flatten_dict(d, sep="."):
    flat = {}

    def walk(node, prefix):
        for key, value in node.items():
            path = f"{prefix}{sep}{key}" if prefix else key
            if isinstance(value, dict) and value:
                walk(value, path)
            else:
                flat[path] = value

    walk(d, "")
    return flat
```
Leaves land in `flat` in visiting order: depth-first, following the input order.

--- predict
Using the `flatten_dict` above, what does this print?
```python
print(list(flatten_dict({"a": {"b": 1, "c": {}}, "d": 2})))
```
answer: ['a.b', 'a.c', 'd']
> `a` is a non-empty dict, so the walk goes inside: `b` is a leaf, and `c` is an empty dict, also a leaf. Then `d`. Depth-first, in input order.

--- teach
### Unflatten: split the key and walk down
Going back, split each key on the separator. `*parents, last = parts` puts everything but the final piece into `parents`. Walk down from the result, using `setdefault(part, {})` to create each intermediate dict on first sight, then assign the value under `last`.
```python
for key, value in flat.items():
    *parents, last = key.split(sep)
    node = result
    for part in parents:
        node = node.setdefault(part, {})
    node[last] = value
```

--- code
Split `key` on `.`, walk down `result` creating dicts as needed, and store `value` under the last part.
```python
result = {}
key, value = "a.b.c", 1
```
check: result == {"a": {"b": {"c": 1}}}
solution: *parents, last = key.split(".")
solution: node = result
solution: for part in parents:
solution:     node = node.setdefault(part, {})
solution: node[last] = value
> `parents` is `['a', 'b']` and `last` is `'c'`. Each `setdefault` creates the next level and moves `node` into it; the final assignment lands at the bottom.

--- teach
### Detect conflicts in both orders
A key that is both a leaf and a prefix of another key cannot be rebuilt. Two checks catch it whichever comes first: while walking down, if `setdefault` hands back something that is not a dict, a leaf is in the way; before the final assignment, if `node.get(last)` is a non-empty dict, nested keys are already there. Raise `ValueError` in either case.
```python
child = node.setdefault(part, {})
if not isinstance(child, dict):
    raise ValueError(f"key {key!r} conflicts with leaf {part!r}")
```

--- fill
Complete the call so an intermediate dict is created when it is missing.
```python
child = node.setdefault(part, ___)
```
answer: {}
> `setdefault(part, {})` inserts an empty dict on first sight and returns the existing value afterwards. Check that value with `isinstance` before descending into it.

--- exercise 5.7

--- recap
- `f"{prefix}{sep}{key}" if prefix else key` builds the path.
- Recurse only into non-empty dicts; everything else, including `{}` and lists, is a leaf.
- An inner `walk(node, prefix)` that calls itself fills the outer `flat` dict.
- Unflatten with `*parents, last = key.split(sep)` and a chain of `setdefault(part, {})`; raise on a leaf-versus-prefix conflict.
