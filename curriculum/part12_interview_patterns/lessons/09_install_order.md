# Topological sort: install order

--- teach
### The pattern: a dependency graph
"Package A needs B and C, C needs B. In what order do I install?" A dict of name to requirements is a **graph**, and ordering it so every package comes after what it needs is a **topological sort**. The brute force: repeatedly scan every unplaced package for one whose requirements are all placed.
```python
def install_order_slow(deps):
    placed, order = set(), []
    while len(order) < len(deps):
        ready = sorted(n for n in deps
                       if n not in placed and set(deps[n]) <= placed)
        if not ready:
            raise ValueError("dependency cycle")
        order.append(ready[0]); placed.add(ready[0])
    return order
```
Each round rescans everything to place one package. Say it: "Scan for anything ready, O(V squared). Kahn's algorithm does it in one pass with in-degree counts."

--- quiz
With V packages in one long chain, what does the scan-every-round approach cost?
- [ ] O(V): each package is placed once
- [x] O(V²): V rounds, each scanning all V packages
- [ ] O(V log V): the sort dominates
> Only one package is ready per round, so there are V rounds, and each round scans all V entries. With 3,000 packages that is nine million checks, visibly slower than linear.

--- teach
### The insight: count what each package still waits for
Kahn's algorithm keeps, for every package, the set of requirements not yet installed, and for every package, who depends on it. Anything with nothing left to wait for is ready. Pop a ready package, install it, and remove it from its dependants' waiting sets; whoever reaches zero becomes ready.
```python
import heapq
ready = [n for n in remaining if not remaining[n]]
heapq.heapify(ready)
order = []
while ready:
    name = heapq.heappop(ready)
    order.append(name)
    for dependant in dependants[name]:
        remaining[dependant].discard(name)
        if not remaining[dependant]:
            heapq.heappush(ready, dependant)
```
A heap instead of a plain queue pops the alphabetically first ready name, which makes the order unique and testable.

--- code
Write Kahn's loop: while `ready` is not empty, pop the smallest name, append it to `order`, and remove it from each dependant's waiting set, pushing any dependant that reaches zero. Then print `order`.
```python
import heapq
remaining = {"app": {"libc"}, "libc": set()}
dependants = {"app": set(), "libc": {"app"}}
ready, order = ["libc"], []
```
expect: ['libc', 'app']
solution: while ready:
solution:     name = heapq.heappop(ready)
solution:     order.append(name)
solution:     for dependant in dependants[name]:
solution:         remaining[dependant].discard(name)
solution:         if not remaining[dependant]:
solution:             heapq.heappush(ready, dependant)
solution: print(order)
> `libc` is the only ready package. Installing it removes it from `app`'s waiting set, which becomes empty, so `app` is pushed and installed next.

--- predict
What does this print?
```python
import heapq
ready = ["zsh", "bash", "fish"]
heapq.heapify(ready)
print(heapq.heappop(ready))
```
answer: bash
> A heap always pops its smallest item, and strings compare alphabetically. `bash` comes before `fish` and `zsh`, so it is installed first among the three ready shells.

--- teach
### Build both maps, including packages nobody listed
A name that appears only inside a requirements list, like `sdk` in `{"agent": ["sdk"]}`, is a real package with no requirements. `setdefault` puts it in both maps when it is first seen. Sets make duplicate names in a list harmless.
```python
remaining, dependants = {}, {}
for name, deps in packages.items():
    remaining.setdefault(name, set()).update(deps)
    dependants.setdefault(name, set())
    for dep in deps:
        remaining.setdefault(dep, set())
        dependants.setdefault(dep, set()).add(name)
```
Now `remaining[dep]` exists even when `dep` never appeared as a key, and `dependants[dep]` knows who to notify when it installs.

--- fill
Complete the step that makes a package ready once its last requirement is installed.
```python
remaining[dependant].discard(name)
if not remaining[dependant]:
    heapq.___(ready, dependant)
```
answer: heappush
> `heappush` adds the newly ready package to the heap, keeping alphabetical pops. `ready.append` would break the heap order and the alphabetical tie-break.

--- teach
### Leftovers mean a cycle, and a good answer names it
If the heap runs dry before every package is placed, the ones left over are waiting on each other. Say which: run a depth-first search over the leftovers, marking each package "in progress" while you are inside it and "done" when you leave. Meeting an "in progress" package means you walked in a loop; the path from it back to itself is the cycle.

Raise `ValueError("dependency cycle: a -> b -> c -> a")`. Innocent packages that merely depend on the cycle are stuck too, but must not be named. A package that requires itself is a cycle of one.

--- quiz
`install_order({"a": ["b"], "b": ["c"], "c": ["a"], "zlib": []})` runs Kahn's loop. What is in `order` when the heap runs dry?
- [x] `['zlib']`, with `a`, `b`, `c` left over
- [ ] `['a', 'b', 'c', 'zlib']`
- [ ] `[]`, nothing was ready
> Only `zlib` starts with no requirements. `a`, `b` and `c` each wait for one another, so none ever reaches zero. They are the leftovers, and the error message must name them and not `zlib`.

--- teach
### The cost, and how to say it
Every package enters the heap once and every dependency edge is removed once: O(V log V + E), the log paying for alphabetical pops. With a plain deque it would be O(V + E).

Say it out loud: "Kahn's algorithm: count what each package still waits for, keep a heap of ready ones for a deterministic order, and decrement dependants as I install. Anything left at the end is on or behind a cycle, and I run a DFS on the leftovers to name it."

Edge cases: an empty dict gives `[]`; every package appears exactly once.

--- exercise 12.9

--- recap
- "Install order", "who is reachable", "detect the cycle" are graph questions on a dict of lists.
- Kahn's algorithm: waiting sets per package, a heap of ready names, decrement dependants.
- `setdefault` puts dependency-only packages into both maps.
- Leftovers after the loop mean a cycle; a three-colour DFS names it. O(V log V + E).
