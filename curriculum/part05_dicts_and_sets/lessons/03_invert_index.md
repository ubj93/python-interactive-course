# Inverting a mapping

--- teach #card-d22a102c76a958a5
### Walk the pairs with `.items()`
`for key, value in d.items()` gives each key and its value together. When the value is a list, a second loop walks its members. Build the inverted dict by assigning each member as a key and the outer key as its value.
```python
device_to_user = {}
for user, serials in user_to_devices.items():
    for serial in serials:
        device_to_user[serial] = user
```
The outer loop runs in dict order and the inner in list order, so the result's keys come out in encounter order, as the exercise asks. An empty list simply runs the inner loop zero times.

--- predict #card-f5354371b9ed570c
What does this print?
```python
d = {"jdoe": ["A", "B"], "asmith": []}
for user, serials in d.items():
    print(user, len(serials))
```
answer: jdoe 2 asmith 0
> `items()` yields `('jdoe', ['A', 'B'])` then `('asmith', [])`. Each print shows the user and the list length, on two lines.

--- code #card-01f3e3b1b4465056
Build `device_to_user`, mapping each serial in `user_to_devices` to its user. No conflict check yet.
```python
user_to_devices = {"jdoe": ["A", "B"], "asmith": ["C"]}
```
check: device_to_user == {"A": "jdoe", "B": "jdoe", "C": "asmith"}
check: list(device_to_user) == ["A", "B", "C"]
solution: device_to_user = {}
solution: for user, serials in user_to_devices.items():
solution:     for serial in serials:
solution:         device_to_user[serial] = user
> The outer loop gives one user and their list; the inner loop assigns each serial. Keys land in the order they were met: `A`, `B` from `jdoe`, then `C`.

--- teach #card-f83ede0473b05a3c
### Assignment overwrites silently
Assigning to a key that already exists replaces the value with no warning. For an index that must be one-to-one, that is a bug waiting to happen: a serial under two users would quietly keep the last one.
```python
>>> d = {}
>>> d["C02A"] = "jdoe"
>>> d["C02A"] = "asmith"
>>> d
{'C02A': 'asmith'}
```
A dict comprehension, `{s: u for u, ss in d.items() for s in ss}`, has the same silent behaviour. When duplicates are an error, write the loop and check first.

--- predict #card-ee2295123dab57f2
What does this print?
```python
d = {}
d["C02A"] = "jdoe"
d["C02A"] = "jdoe"
print(len(d))
```
answer: 1
> The same key assigned twice is still one key. That is why a serial listed twice under the *same* user is not a conflict: the value does not change.

--- teach #card-f73495356d8954ad
### Check before you insert, and say which serial
Look up the serial before assigning. If it is already there with a *different* user, raise `ValueError` with the serial in the message; the test looks for it there. Same user again is fine.
```python
owner = device_to_user.get(serial)
if owner is not None and owner != user:
    raise ValueError(f"serial {serial} is assigned to both {owner} and {user}")
device_to_user[serial] = user
```
`get` returns `None` for a new serial, so the first condition guards the comparison.

--- fill #card-38d0c1d6e6065871
Complete the error so the conflicting serial appears in the message.
```python
raise ValueError(f"serial ___ is assigned to both {owner} and {user}")
```
answer: {serial}
> Inside an f-string, `{serial}` is replaced by the value. A message that names the serial is what lets the person reading the log fix the directory.

--- code #card-3b35062709c35a5c
If `serial` is already in `d` under a different user, raise `ValueError` naming the serial; otherwise store `user` under `serial`.
```python
d = {"A": "jdoe"}
serial, user = "B", "asmith"
```
check: d == {"A": "jdoe", "B": "asmith"}
solution: owner = d.get(serial)
solution: if owner is not None and owner != user:
solution:     raise ValueError(f"serial {serial} is assigned to both {owner} and {user}")
solution: d[serial] = user
> `B` is new, so `get` returns `None`, the guard is skipped and the pair is stored. Change `serial` to `"A"` and the same code raises with `A` in the message.

--- teach #card-81e8cbf3bc985f57
### Leave the input alone
Reading a dict with `.items()` and reading a list with `for` change nothing. Methods like `pop`, `clear`, `append` and `sort` do. Build a *new* dict for the result and never call a mutating method on the argument; the test compares the input before and after.

--- quiz #card-244a4b86ff9c585b
Which line modifies the caller's data?
- [x] `serials.append(serial)`
- [ ] `for serial in serials:`
- [ ] `device_to_user[serial] = user`
> `append` changes the list the caller passed in. Iterating reads it, and assigning into your own new dict touches only your dict.

--- exercise 5.3 #card-16deb12c7eaf509e

--- recap #card-ffa2a6c19e595611
- `for k, v in d.items()` walks pairs; nest a loop for list values.
- Assigning an existing key overwrites silently; comprehensions do too.
- Look up first; raise `ValueError` with the serial when the owner differs.
- Build a new dict and never mutate the input.
