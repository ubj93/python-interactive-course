# Counting once per device, then ranking

--- teach
### Count each app once per device
A device's list may name the same app several times. `set(apps)` collapses it to the distinct names without touching the original list. Loop over `installs.values()` when you do not need the serial, and apply the counting idiom to each distinct app.
```python
counts = {}
for apps in installs.values():
    for app in set(apps):
        counts[app] = counts.get(app, 0) + 1
```
Three devices with `Chrome` give `Chrome: 3`, no matter how many copies each device has.

--- predict
What does this print?
```python
print(sorted(set(["Slack", "Chrome", "Slack"])))
```
answer: ['Chrome', 'Slack']
> The set keeps one `Slack`. `sorted` puts the names in alphabetical order; the list you started from is unchanged.

--- code
Count into `counts` how many devices in `installs` have each app, counting an app once per device.
```python
installs = {"C02A": ["Slack", "Slack", "Chrome"], "C02B": ["Chrome"]}
```
check: counts == {"Slack": 1, "Chrome": 2}
solution: counts = {}
solution: for apps in installs.values():
solution:     for app in set(apps):
solution:         counts[app] = counts.get(app, 0) + 1
> `set(apps)` turns the first device's list into `{"Slack", "Chrome"}`, so `Slack` is counted once. `Chrome` appears on both devices and reaches 2.

--- teach
### Sort pairs with a two-part key
`counts.items()` gives `(app, count)` tuples. Sort them with a key function that returns a tuple: Python compares the first element, and only on a tie the second. Negating the count sorts it descending while the name still sorts ascending, all in one `sorted` call.
```python
ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
```
`item[1]` is the count, `item[0]` the name. You saw multi-key sorting in Part 2; this is the same trick with a minus sign.

--- predict
What does this print?
```python
pairs = [("Zoom", 2), ("Chrome", 2), ("Slack", 1)]
print(sorted(pairs, key=lambda t: (-t[1], t[0])))
```
answer: [('Chrome', 2), ('Zoom', 2), ('Slack', 1)]
> Both `Zoom` and `Chrome` have `-2` as the first key, so the tie goes to the name, and `Chrome` comes first. `Slack` has `-1`, which is larger, so it sorts last.

--- code
Set `ranked` to the `(app, count)` pairs of `counts`, sorted by count descending and then by name ascending.
```python
counts = {"Zoom": 2, "Chrome": 2, "Slack": 1}
```
check: ranked == [("Chrome", 2), ("Zoom", 2), ("Slack", 1)]
solution: ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
> `items()` gives the pairs, and the key tuple `(-count, name)` orders them: the highest count first, and among equal counts the alphabetically first name.

--- quiz
Why not `sorted(counts.items(), key=lambda t: (t[1], t[0]), reverse=True)`?
- [x] `reverse` flips the name order too, so ties come out Z to A
- [ ] `reverse=True` does not work with tuple keys
- [ ] It is the same and either is fine
> `reverse` reverses the whole ordering. The counts are then descending as wanted, but tied names are descending too. The spec wants names ascending on a tie, so negate the count instead.

--- teach
### Take the first k
A slice `[:k]` returns at most `k` items and never raises, even when `k` is larger than the list. Guard `k <= 0` first and return `[]`. Names compare as plain strings, so uppercase letters sort before lowercase: `"Chrome"` comes before `"chrome"`.
```python
if k <= 0:
    return []
return ranked[:k]
```

--- fill
Complete the return so at most `k` entries come back.
```python
return ranked[___]
```
answer: :k
> `ranked[:k]` is the first `k` items. With `k` larger than the list you get the whole list, which is what "fewer when there are fewer distinct apps" means.

--- exercise 5.5

--- recap
- `set(apps)` dedupes one device's list without changing it.
- Count with `counts[app] = counts.get(app, 0) + 1`.
- `sorted(items, key=lambda t: (-t[1], t[0]))`: count descending, name ascending.
- `ranked[:k]` never raises; guard `k <= 0` separately.
