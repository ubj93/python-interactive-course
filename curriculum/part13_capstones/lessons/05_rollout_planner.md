# Capstone: rollout planner

--- teach
### The ticket
An OS update goes out in rings, one after another. Each ring has a list of cumulative percentage targets, one per day: `("broad", [10, 40, 100])` means 10% of the ring on its first day, 40% by its second, all of it by its third. Devices with blockers, devices on a held OS version, and devices in an unknown ring are skipped with a reason. Repeated serials are skipped too. Produce a day-by-day schedule with dates counted from `start`, plus the skipped list.

Rules in your own words:
```
- normalise: serial upper, ring lower, os_version stripped, (x or "") everywhere
- skip: blockers (sorted) > hold > unknown ring > eligible
- duplicate: checked before skip_reason; the first row counts
- targets: ceil(n * pct / 100) in integers; validate pcts first
- days: one per ring per pct, numbered across rings; slice previous:target
```

--- teach
### Four functions, in dependency order
- `skip_reason(device, ring_names, holds)` returns a reason string or `None`. It is the only place the eligibility policy lives.
- `partition_devices(devices, ring_names, holds)` returns `({ring: sorted serials}, skipped)`. Pre-create a key for every ring so empty rings still appear; keep a `seen` set for duplicates.
- `cumulative_targets(n, pcts)` returns one integer per day, and raises `ValueError` on bad percentages.
- `plan_rollout(devices, rings, holds, start)` composes them.
```python
by_ring, skipped = partition_devices(devices, [name for name, _ in rings], holds)
days, day = [], 0
for name, pcts in rings:
    serials, previous = by_ring[name], 0
    for target in cumulative_targets(len(serials), pcts):
        day += 1
        days.append({"day": day, "date": ..., "ring": name, "serials": serials[previous:target]})
        previous = target
```

--- teach
### Ceiling division without floats
"10% of 3 devices" must be 1, and 0 devices must give 0. `math.ceil(n * pct / 100)` goes through a float and can round differently on some inputs; the plan must be reproducible. Integer ceiling is a one-liner:
```python
>>> (3 * 10 + 99) // 100
1
>>> (0 * 10 + 99) // 100
0
```
Adding `99` before floor-dividing by 100 pushes any non-zero remainder up to the next whole number. Validate first: `pcts` must be non-empty, non-decreasing and end at 100. `any(a > b for a, b in zip(pcts, pcts[1:]))` compares each element with the next one in a single line.

--- code
Set `targets` to the cumulative integer targets for a ring of `n` devices, one per percentage, rounding up without floats.
```python
n = 7
pcts = [10, 40, 100]
```
check: targets == [1, 3, 7]
solution: targets = [(n * pct + 99) // 100 for pct in pcts]
> One list comprehension, one integer expression per day. 10% of 7 is 0.7, which rounds up to 1; 40% is 2.8, so 3; 100% is 7 exactly, and the `+ 99` does not push an exact multiple over.

--- predict
What does this print?
```python
print((7 * 10 + 99) // 100, (7 * 40 + 99) // 100, (7 * 100 + 99) // 100)
```
answer: 1 3 7
> 70 + 99 is 169, and 169 // 100 is 1; 280 + 99 is 379, so 3; 700 + 99 is 799, so 7. The targets are cumulative, so the broad ring's days get 1 device, then 2 more, then 4 more.

--- quiz
`partition_devices` sees `dev("A1", "canary")`, then `dev(" a1 ", "broad")`, then `dev("A1", "early", blockers=["x"])`. What reason does the third row get?
- [ ] `"blocked: x"`
- [x] `"duplicate"`
- [ ] It is not listed; only the second row is a duplicate
> The duplicate check runs before `skip_reason`, and every later row with a seen serial is a duplicate no matter what else is wrong with it. The first row already went into `canary`. Normalise the serial before checking the `seen` set, or `" a1 "` slips through.

--- fill
Complete the schedule loop so each day gets only the devices that are new since the previous day.
```python
for target in cumulative_targets(len(serials), pcts):
    day += 1
    days.append({"day": day, "date": (start + timedelta(days=day - 1)).isoformat(),
                 "ring": name, "serials": serials[___:target]})
    previous = target
```
answer: previous
> The targets are cumulative, so today's slice starts where yesterday's ended. `previous` restarts at 0 for each ring, but `day` keeps counting across rings, which is why `timedelta(days=day - 1)` dates the whole plan from `start`.

--- code
Build the schedule for one ring: append one dict per target to `days` with `day` (from 1), `date` (ISO text, counted from `start`), `ring` `"broad"`, and the serials that are new that day.
```python
from datetime import date, timedelta
start, serials, targets = date(2024, 6, 29), ["B1", "B2", "B3"], [1, 3]
days = []
```
check: days == [{"day": 1, "date": "2024-06-29", "ring": "broad", "serials": ["B1"]}, {"day": 2, "date": "2024-06-30", "ring": "broad", "serials": ["B2", "B3"]}]
solution: day, previous = 0, 0
solution: for target in targets:
solution:     day += 1
solution:     days.append({"day": day, "date": (start + timedelta(days=day - 1)).isoformat(), "ring": "broad", "serials": serials[previous:target]})
solution:     previous = target
> Day 1 is `start` itself, so the offset is `day - 1`. The slice `serials[0:1]` gives `B1`, then `serials[1:3]` gives the two new ones. In `plan_rollout` the `day` counter lives outside the ring loop so numbering continues across rings.

--- teach
### Budget: 45 minutes
- 0–6: read twice, write the rules; say "duplicate beats blocked" out loud.
- 6–10: signatures and the `plan_rollout` skeleton above.
- 10–16: `cumulative_targets`, including the `ValueError` cases; five one-line checks.
- 16–24: `skip_reason` in spec order: blockers, hold, ring.
- 24–34: `partition_devices`: pre-created ring keys, `seen`, sort every list at the end.
- 34–41: fill in `plan_rollout`; run the schedule and month-rollover tests.
- 41–45: the messy-fleet test.

`plan_rollout` should not compute anything itself: if you are stripping or sorting inside it, move that into `partition_devices`.

--- exercise 13.5

--- recap
- `skip_reason` is the one place the policy lives; `None` is the only "go".
- Duplicates are checked before `skip_reason`; the first row counts.
- `(n * pct + 99) // 100` is integer ceiling; validate `pcts` before computing.
- A running `day` across rings, `start + timedelta(days=day - 1)`, and `serials[previous:target]`.
