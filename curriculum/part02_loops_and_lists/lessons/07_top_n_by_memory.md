# Putting it together: sorting records

--- teach
### `sorted` returns a new list; `.sort()` returns None
`sorted(xs)` gives back a sorted copy and leaves `xs` alone. `xs.sort()` sorts in place and returns `None`, so `xs = xs.sort()` throws your list away. Interviewers see that one weekly. When you were told not to modify the input, `sorted` is the only choice.
```python
>>> ram = [16, 32, 8]
>>> sorted(ram)
[8, 16, 32]
>>> ram
[16, 32, 8]
>>> sorted(ram, reverse=True)
[32, 16, 8]
```

--- predict
What does this print?
```python
xs = [3, 1, 2]
result = xs.sort()
print(result)
```
answer: None
> `.sort()` sorts `xs` in place and returns `None`. `xs` is now `[1, 2, 3]`, but `result` is not.

--- teach
### `key` says what to sort by
Records cannot be compared directly, so give `sorted` a `key` function: it is called once per item and the items are ordered by what it returns. A `lambda` is a tiny one-expression function written inline.
```python
>>> devices = [{"hostname": "b", "memory_gb": 16}, {"hostname": "a", "memory_gb": 32}]
>>> sorted(devices, key=lambda d: d["memory_gb"])[0]["hostname"]
'b'
```
`lambda d: d["memory_gb"]` means "given `d`, return its memory".

--- code
Print the hostname of the device with the least memory, using `sorted` with a `key`.
```python
devices = [{"hostname": "nuc-01", "memory_gb": 16}, {"hostname": "win-lab-01", "memory_gb": 8}, {"hostname": "mbp-j-doe", "memory_gb": 32}]
```
expect: win-lab-01
solution: print(sorted(devices, key=lambda d: d["memory_gb"])[0]["hostname"])
> Sorting by memory puts 8 GB first; `[0]` takes that record and `["hostname"]` reads its name.

--- fill
Complete the call so the devices are ordered by hostname.
```python
by_name = sorted(devices, key=lambda d: d[___])
```
answer: "hostname"|'hostname'
> The key function returns the value to sort on. Returning `d["hostname"]` orders the records alphabetically by hostname.

--- teach
### A tuple key sorts by several things
Return a tuple from the key. Tuples compare element by element, so the first field decides and the second breaks ties. Negating a number reverses its direction, so `(-memory, hostname)` means memory descending, then hostname ascending, in one call.
```python
>>> sorted(devices, key=lambda d: (-d["memory_gb"], d["hostname"]))
```
`reverse=True` would flip both fields; the minus sign flips just the number. Strings cannot be negated; the chapter shows the two-pass trick for that case.

--- code
Set `ranked` to the devices ordered by memory descending, with ties broken by hostname ascending, in one `sorted` call.
```python
devices = [{"hostname": "nuc-01", "memory_gb": 16}, {"hostname": "mbp-j-doe", "memory_gb": 32}, {"hostname": "mbp-a-kim", "memory_gb": 32}]
```
check: [d["hostname"] for d in ranked] == ["mbp-a-kim", "mbp-j-doe", "nuc-01"]
solution: ranked = sorted(devices, key=lambda d: (-d["memory_gb"], d["hostname"]))
> The key tuple is `(-32, "mbp-a-kim")`, `(-32, "mbp-j-doe")`, `(-16, "nuc-01")`. The negative number sorts big memory first; the hostname breaks the tie.

--- predict
What does this print?
```python
devs = [("nuc", 16), ("kim", 32), ("doe", 32)]
top = sorted(devs, key=lambda d: (-d[1], d[0]))
print(top[0][0])
```
answer: doe
> Both 32 GB machines tie on `-32`; the tuple then compares names and "doe" comes before "kim". 16 GB sorts last.

--- teach
### Missing memory counts as zero; take the first `n`
`d.get("memory_gb")` is `None` for a missing or null field, and `None` cannot be negated. `d.get("memory_gb") or 0` turns both cases into `0`. Then slice the sorted list: `[:n]` gives the first `n`, and a slice larger than the list just gives everything. Return `[]` for `n <= 0` before doing any work.
```python
ranked = sorted(devices, key=lambda d: (-(d.get("memory_gb") or 0), d["hostname"]))
top = []
for d in ranked[:n]:
    top.append(d["hostname"])
return top
```

--- quiz
Why does `sorted(devices, key=lambda d: d["memory_gb"], reverse=True)` not fully solve the exercise?
- [ ] `reverse=True` is not allowed together with `key`
- [x] Ties on memory would not be ordered by hostname
- [ ] It modifies `devices`
> `reverse=True` orders memory descending but says nothing about ties; equal records keep their input order. The tuple key `(-memory, hostname)` handles both in one call. `sorted` never modifies its input.

--- exercise 2.7

--- recap
- `sorted(xs)` returns a new list; `xs.sort()` returns `None`.
- `key=lambda d: d["field"]` sorts records by a field.
- A tuple key `(-number, text)` sorts descending by number, then ascending by text.
- `xs[:n]` takes the first `n`; `d.get(k) or 0` handles missing values.
