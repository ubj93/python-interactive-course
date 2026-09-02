# Capstone: manifest resolver

--- teach
### The ticket
Munki-style manifests are a dict of `name -> manifest`. A manifest may list `included_manifests`, `managed_installs` and `managed_uninstalls`; every key is optional. Starting from one manifest, work out which manifests a client would read and in what order, what it would install and remove, and where the manifests contradict each other (the same item installed by one and removed by another). An unknown name raises `KeyError`; an include cycle raises `ValueError` naming the cycle, such as `a -> b -> a`. An optional catalog flags items nobody has packaged.

Rules in your own words:
```
- order: depth-first, pre-order, each manifest once (a diamond is fine)
- cycle: a name already on the current path -> ValueError "a -> b -> a"
- items: strip, drop empties, first-seen order, no duplicates
- conflicts: sorted(installs & uninstalls); remove from both lists
- missing: only with a catalog; sorted; items stay in their lists
```

--- teach
### Four functions
```python
def resolve_manifest(manifests, name, catalog=None):
    order = expand_includes(manifests, name)
    installs, uninstalls = collect_items(manifests, order)
    conflicts = find_conflicts(installs, uninstalls)
    conflict_set = set(conflicts)
    installs = [i for i in installs if i not in conflict_set]
    uninstalls = [u for u in uninstalls if u not in conflict_set]
    missing = []
    if catalog is not None:
        known = set(catalog)
        missing = sorted({i for i in installs + uninstalls if i not in known})
    return {"manifests": order, "installs": installs, "uninstalls": uninstalls,
            "conflicts": conflicts, "missing": missing}
```
- `expand_includes` is the graph walk and the only hard part.
- `collect_items` walks `order`, strips names, drops empties, dedupes keeping first-seen order.
- `find_conflicts` is one set intersection.

`catalog is not None` matters: an empty catalog is a real catalog in which everything is missing.

--- teach
### Depth-first with two sets
Write an inner `visit(current)` that appends to an outer `order` list and recurses over the includes. You need two different bookkeeping structures: `done` (fully visited: return early, which is how a diamond is visited once) and `path` (the manifests on the current recursion stack: seeing one again is a cycle). Push before recursing, pop after.
```python
def visit(current):
    if current in path:
        raise ValueError("include cycle: " + " -> ".join(path[path.index(current):] + [current]))
    if current in done:
        return
    if current not in manifests:
        raise KeyError(current)
    path.append(current)
    order.append(current)
    done.add(current)
    for child in manifests[current].get("included_manifests") or []:
        visit(child)
    path.pop()
```
Check the cycle before `done`, or a manifest that includes itself is silently accepted. One shared `visited` set cannot tell a diamond from a cycle.

--- quiz
`top` includes `l` and `r`; both `l` and `r` include `base`. What does `expand_includes(manifests, "top")` return?
- [x] `['top', 'l', 'base', 'r']`
- [ ] `['top', 'l', 'base', 'r', 'base']`
- [ ] It raises `ValueError`, because `base` is reached twice
> Pre-order means a manifest is listed before its includes, and depth-first means `l`'s subtree is finished before `r` starts. When `r` reaches `base`, `base` is in `done` but not on the current `path` (which is `top, r`), so it is skipped, not reported as a cycle.

--- predict
What does this print?
```python
path = ["a", "b", "c"]
current = "b"
print(" -> ".join(path[path.index(current):] + [current]))
```
answer: b -> c -> b
> `path.index("b")` is 1, so the slice is `["b", "c"]`, and appending `current` closes the loop. The tests check the message with `assertIn`, so the whole cycle must be there, starting and ending at the repeated name.

--- code
Write the body of `visit`: return if `current` is already in `done`; otherwise add it to `done` and `order`, then visit each name in its `included_manifests` (the key may be missing). Then call `visit("top")`.
```python
manifests = {"top": {"included_manifests": ["l", "r"]}, "l": {"included_manifests": ["base"]}, "r": {"included_manifests": ["base"]}, "base": {}}
order, done = [], set()

def visit(current):
```
check: order == ["top", "l", "base", "r"]
solution:     if current in done:
solution:         return
solution:     done.add(current)
solution:     order.append(current)
solution:     for child in manifests[current].get("included_manifests") or []:
solution:         visit(child)
solution: visit("top")
> Appending before recursing is what makes the order pre-order. `base` is added to `done` on the way through `l`, so when `r` reaches it the early `return` fires. Add the `path` check above the `done` check and you have the real `expand_includes`.

--- teach
### First-seen order, then set algebra
Lists keep order but do not dedupe; sets dedupe but forget order. For the item lists you need both, so walk with a `seen` set and append only new names. `list(dict.fromkeys(items))` does the same in one line.
```python
def _dedupe(items):
    seen, out = set(), []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
```
Clean each manifest's list first: `[(s or "").strip() for s in items or []]`, then drop the empty strings. Conflicts are pure set algebra, sorted so the answer does not depend on set order, and both lists are then filtered against `set(conflicts)` with a comprehension.

--- code
Set `clean` to the item names stripped, with empty names dropped and duplicates removed, keeping first-seen order.
```python
items = ["Zoom ", "Chrome", "", " Zoom", "Slack"]
```
check: clean == ["Zoom", "Chrome", "Slack"]
solution: seen, clean = set(), []
solution: for item in items:
solution:     name = item.strip()
solution:     if name and name not in seen:
solution:         seen.add(name)
solution:         clean.append(name)
> Strip first, so `"Zoom "` and `" Zoom"` become the same name and the second one is caught by `seen`. The `name and` part drops the empty string. `list(dict.fromkeys(...))` over the stripped, non-empty names is the one-line version.

--- fill
Complete `find_conflicts` so it returns the items present in both lists, in sorted order.
```python
def find_conflicts(installs, uninstalls):
    return sorted(set(installs) ___ set(uninstalls))
```
answer: &
> `&` is set intersection. `sorted` turns the set back into a list with a deterministic order; emitting a set directly would make the output depend on hashing.

--- teach
### Budget: 45 minutes
- 0–6: read twice, write the rules; draw the diamond and the three-node cycle on paper.
- 6–10: signatures and `resolve_manifest` as above; it is mostly done.
- 10–25: `expand_includes`. Test in this order: a solo manifest, a chain, the diamond, then the cycle and a self-include.
- 25–33: `_clean`, `_dedupe`, `collect_items`; check that the result depends on `order`.
- 33–37: `find_conflicts`, then run the end-to-end tests.
- 37–45: the catalog tests and the messy tree.

If `expand_includes` is not passing by minute 25, freeze it: `collect_items` and the composer earn credit on their own.

--- exercise 13.6

--- recap
- DFS with two structures: `done` handles diamonds, `path` detects cycles; check the cycle first.
- The cycle message is `path[path.index(current):] + [current]` joined by `" -> "`.
- Dedupe with a `seen` set to keep first-seen order.
- Conflicts are `sorted(set(a) & set(b))`, removed from both lists; `missing` only when `catalog is not None`.
