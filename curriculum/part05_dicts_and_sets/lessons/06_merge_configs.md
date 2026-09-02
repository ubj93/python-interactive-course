# Recursive merge

--- teach
### `isinstance` asks "is this a dict?"
`isinstance(value, dict)` returns `True` when `value` is a dict. The merge rule depends on the types of *both* sides: only when the old value and the new value are both dicts do you merge them; otherwise the new value simply wins, whether it is a list, a number, a dict replacing a scalar, or `None`.
```python
>>> isinstance({"a": 1}, dict)
True
>>> isinstance(["a"], dict)
False
```
Use the same test on every argument at the start and `raise TypeError(...)` for anything that is not a dict.

--- predict
What does this print?
```python
print(isinstance({}, dict), isinstance([], dict))
```
answer: True False
> An empty dict is still a dict. A list is not, even an empty one.

--- teach
### Copy the base, then write into the copy
`dict(base)` makes a new dict with the same keys and values. Assigning into the copy leaves `base` untouched, and the copy keeps base's key order, so new keys from the override land at the end.
```python
result = dict(base)
for key, value in override.items():
    result[key] = value
```
This alone is a flat merge: later values win and new keys are appended.

--- predict
What does this print?
```python
base = {"a": 1}
r = dict(base)
r["b"] = 2
print(base)
```
answer: {'a': 1}
> `dict(base)` is a separate dict. Adding `b` to the copy does not touch the original.

--- teach
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

--- fill
Complete the recursive call.
```python
if isinstance(existing, dict) and isinstance(value, dict):
    result[key] = ___(existing, value)
```
answer: merge_two
> Merging the two nested dicts is the same job, so the function calls itself. Any other combination of types falls to the `else` and the later value wins.

--- teach
### Shallow copies share nested values
`dict(base)` copies the top level only. A list or dict *inside* is the same object in both, so changing it through the result changes the input. `copy.deepcopy(x)` copies all the way down. Deep-copy the merged result once before returning it.
```python
import copy

return copy.deepcopy(merged)
```
Now the caller can append to a list in the result and the inputs stay exactly as they were.

--- quiz
`base = {"tags": ["a"]}` and `r = dict(base)`. After `r["tags"].append("b")`, what is `base["tags"]`?
- [x] `['a', 'b']`
- [ ] `['a']`
- [ ] It raises an error
> Both dicts point at the same list, so appending through `r` is visible through `base`. That is the sharing `deepcopy` removes.

--- teach
### Any number of configs
`*configs` collects every positional argument into a tuple. Check that each is a dict, then fold them left to right starting from `{}`: merge the first into the empty dict, then the second into that result, and so on. With no arguments the loop never runs and `{}` comes back.
```python
merged = {}
for cfg in configs:
    merged = merge_two(merged, cfg)
```

--- exercise 5.6

--- recap
- `isinstance(x, dict)` on both sides decides merge versus replace.
- `dict(base)` copies the top level and keeps key order.
- A recursive function calls itself on the nested dicts; the flat case ends it.
- `copy.deepcopy` breaks sharing with the inputs.
