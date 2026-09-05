# Graphs with defaultdict

--- teach #card-758857a2cc9a5e3e
### A graph as a dict of sets
A graph is nodes joined by edges. The simplest way to store one is an **adjacency dict**: each node maps to the set of its neighbours. Package conflicts are undirected (if `java8` conflicts with `java11`, the reverse is true too), so every edge is written in both directions.
```python
adj = {
    "java8":  {"java11"},
    "java11": {"java8", "java17"},
    "java17": {"java11"},
}
```
A set, not a list: the same edge added twice is stored once.

--- quiz #card-d97e3a18d6db56c0
After adding the undirected edge `("a", "b")`, which statement must be true?
- [ ] `"b" in adj["a"]` only
- [x] `"b" in adj["a"]` and `"a" in adj["b"]`
- [ ] `adj["a"] == adj["b"]`
> Undirected means both ends know about each other. Writing only one direction is the classic bug.

--- teach #card-f134a5069a8a5e50
### `defaultdict(set)` creates the set for you
A `defaultdict` calls its factory the first time a missing key is touched. With `set` as the factory, `adj[a].add(b)` works even when `a` has never been seen. Merely reading `adj[x]` registers `x` with an empty set, which is exactly how you add a node with no neighbours.
```python
>>> from collections import defaultdict
>>> adj = defaultdict(set)
>>> adj["java8"].add("java11")
>>> adj["java11"].add("java8")
>>> adj["solo"]
set()
>>> sorted(adj)
['java11', 'java8', 'solo']
```

--- code #card-28c4b864029e5a16
Build `adj` as a `defaultdict(set)` holding both directions of every edge, then print the sorted neighbours of `"b"`.
```python
from collections import defaultdict
edges = [("a", "b"), ("b", "c"), ("a", "b")]
```
expect: ['a', 'c']
check: adj["a"] == {"b"}
solution: adj = defaultdict(set)
solution: for x, y in edges:
solution:     adj[x].add(y)
solution:     adj[y].add(x)
solution: print(sorted(adj["b"]))
> Two `add` calls per edge give both directions. The repeated `("a", "b")` changes nothing because sets ignore duplicates.

--- predict #card-f9f3f81ca0c55e52
What does this print?
```python
from collections import defaultdict
adj = defaultdict(set)
adj["a"].add("b")
adj["c"]
print(sorted(adj))
```
answer: ['a', 'c']
> Touching `adj["c"]` created the key. Note `"b"` is only a value here, so it is not a key; the exercise touches both ends of every edge.

--- teach #card-7fe3e0af25bf53c0
### Freeze it before returning
That convenience is a trap after building: every lookup of an unknown node quietly creates it, so `if node in adj` starts lying. Convert to a plain `dict` at the boundary; callers then get a `KeyError` for unknown nodes, which is what they expect.
```python
def build_adjacency(edges, nodes=()):
    adj = defaultdict(set)
    for node in nodes:
        adj[node]
    for a, b in edges:
        adj[a]
        adj[b]
        if a != b:
            adj[a].add(b)
            adj[b].add(a)
    return dict(adj)
```
`for a, b in edges` unpacks each pair and works for any iterable, including generators.

--- code #card-e2d4fa8286c55459
Convert `adj` to a plain dict called `graph`, then print `sorted(graph)`.
```python
from collections import defaultdict
adj = defaultdict(set)
adj["a"].add("b"); adj["b"].add("a")
```
expect: ['a', 'b']
check: type(graph) is dict
solution: graph = dict(adj)
solution: print(sorted(graph))
> `dict(adj)` copies the entries into a normal dict. From here on, `graph["zzz"]` raises `KeyError` instead of inventing a node.

--- fill #card-87ebaf7de2845145
Complete the return so callers get a plain dict that raises `KeyError` for unknown nodes.
```python
return ___(adj)
```
answer: dict
> `dict(adj)` copies the keys and sets into a normal dict. The `defaultdict` behaviour stays inside the function.

--- teach #card-4b3f75423d185dff
### Self-loops and neighbour lists
An edge `("x", "x")` registers the node but adds no neighbour: `if a != b` skips the `add`. For `neighbors`, use `.get(node, ())` so an unknown node gives an empty result instead of a `KeyError`, and `sorted` to turn the unordered set into a stable list.
```python
def neighbors(adj, node):
    return sorted(adj.get(node, ()))
```

--- predict #card-cde5b18c257b55ab
What does this print?
```python
print(sorted({"java8", "corretto", "java17"}))
```
answer: ['corretto', 'java17', 'java8']
> Sets have no order, so `sorted` decides it: alphabetical, and `"java17"` comes before `"java8"` because `"1"` sorts before `"8"`.

--- exercise 10.6 #card-a3ad445c0baf5ed1

--- recap #card-03e048847e54545b
- An adjacency dict maps each node to a set of neighbours; undirected edges go both ways.
- `defaultdict(set)` creates the set on first touch; a bare `adj[x]` registers a node.
- Return `dict(adj)` so unknown nodes raise `KeyError` instead of being created.
- `sorted(adj.get(node, ()))` gives a stable neighbour list, `[]` for unknown nodes.
