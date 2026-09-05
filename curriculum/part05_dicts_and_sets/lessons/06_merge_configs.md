# Recursive merge

--- teach #card-735016cec249528a
### `isinstance` asks "is this a dict?"
`isinstance(value, dict)` returns `True` when `value` is a dict. The merge rule depends on the types of *both* sides: only when the old value and the new value are both dicts do you merge them; otherwise the new value simply wins, whether it is a list, a number, a dict replacing a scalar, or `None`.
```python
>>> isinstance({"a": 1}, dict)
True
>>> isinstance(["a"], dict)
False
```
Use the same test on every argument at the start and `raise TypeError(...)` for anything that is not a dict.

--- predict #card-8f4f90c4d3ee5350
What does this print?
```python
print(isinstance({}, dict), isinstance([], dict))
```
answer: True False
> An empty dict is still a dict. A list is not, even an empty one.

--- teach #card-f71b5b5362c650fb
### Copy the base, then write into the copy
`dict(base)` makes a new dict with the same keys and values. Assigning into the copy leaves `base` untouched, and the copy keeps base's key order, so new keys from the override land at the end.
```python
result = dict(base)
for key, value in override.items():
    result[key] = value
```
This alone is a flat merge: later values win and new keys are appended.

--- code #card-407844edb3e55aa8
Set `result` to a flat merge: a copy of `base` with every pair of `over` written over it. `base` must stay unchanged.
```python
base = {"a": 1, "b": 2}
over = {"b": 3, "c": 4}
```
check: result == {"a": 1, "b": 3, "c": 4}
check: base == {"a": 1, "b": 2}
solution: result = dict(base)
solution: for key, value in over.items():
solution:     result[key] = value
> `dict(base)` is a separate dict, so writing `b` and `c` into it leaves `base` alone. `b` is overwritten in place and keeps its position; `c` is appended.

--- teach #card-9bfeef717d9a5dd0
### Recursion: merge two, and call yourself for nested dicts
A recursive function calls itself on a smaller version of the problem. Here, "merge two dicts" is small when no value is a nested dict, and when a value *is* a nested dict on both sides, merging it is the same problem one level down.
```python
def merge_two(base, override):
    result = dict(base)
    for key, value in override.items():
        existing = result.get(key)
        if isinstance(existing, dict) and isinstance(value, dict):
            result[key] = merge_two(existing, value)
        else:
            result[key] = value
    return result
```
The recursion stops by itself: a level with no nested dicts never calls `merge_two` again.

--- fill #card-bf14b6382bcc5ed5
Complete the recursive call.
```python
if isinstance(existing, dict) and isinstance(value, dict):
    result[key] = ___(existing, value)
```
answer: merge_two
> Merging the two nested dicts is the same job, so the function calls itself. Any other combination of types falls to the `else` and the later value wins.

--- teach #card-05510c3888b859d1
### Shallow copies share nested values
`dict(base)` copies the top level only. A list or dict *inside* is the same object in both, so changing it through the result changes the input. `copy.deepcopy(x)` copies all the way down. Deep-copy the merged result once before returning it.
```python
import copy

return copy.deepcopy(merged)
```
Now the caller can append to a list in the result and the inputs stay exactly as they were.

--- quiz #card-3d46aa73a32f57e8
`base = {"tags": ["a"]}` and `r = dict(base)`. After `r["tags"].append("b")`, what is `base["tags"]`?
- [x] `['a', 'b']`
- [ ] `['a']`
- [ ] It raises an error
> Both dicts point at the same list, so appending through `r` is visible through `base`. That is the sharing `deepcopy` removes.

--- code #card-db81930c243b5c2a
Set `r` to a copy of `base` that shares nothing with it, so that changing `r["tags"]` cannot affect `base`.
```python
import copy
base = {"tags": ["a"]}
```
check: r == {"tags": ["a"]}
check: r["tags"] is not base["tags"]
solution: r = copy.deepcopy(base)
> `deepcopy` copies the dict and the list inside it, so the two `tags` lists are different objects. `dict(base)` would have passed the first check and failed the second.

--- teach #card-e961033bd30b50c8
### Any number of configs
`*configs` collects every positional argument into a tuple. Check that each is a dict, then fold them left to right starting from `{}`: merge the first into the empty dict, then the second into that result, and so on. With no arguments the loop never runs and `{}` comes back.
```python
merged = {}
for cfg in configs:
    merged = merge_two(merged, cfg)
```

--- exercise 5.6 #card-4f3aea3efdc7518e

--- recap #card-6eb589f329995cf5
- `isinstance(x, dict)` on both sides decides merge versus replace.
- `dict(base)` copies the top level and keeps key order.
- A recursive function calls itself on the nested dicts; the flat case ends it.
- `copy.deepcopy` breaks sharing with the inputs.
