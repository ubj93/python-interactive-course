"""Reference solutions for install_order."""
import heapq
from typing import Dict, List, Optional, Set


def _find_cycle(remaining: Dict[str, Set[str]]) -> List[str]:
    """Depth-first search with three colours over the unresolved packages.

    Meeting a package that is still "in progress" (on the current path) means the
    path from that package to here is a cycle. Returns it closed, e.g. [a, b, a].
    """
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {name: WHITE for name in remaining}
    path: List[str] = []

    def visit(name: str) -> Optional[List[str]]:
        colour[name] = GREY
        path.append(name)
        for dep in sorted(remaining[name]):
            if dep not in colour:
                continue
            if colour[dep] == GREY:
                return path[path.index(dep):] + [dep]
            if colour[dep] == WHITE:
                found = visit(dep)
                if found:
                    return found
        path.pop()
        colour[name] = BLACK
        return None

    for name in sorted(remaining):
        if colour[name] == WHITE:
            found = visit(name)
            if found:
                return found
    return []


# Best practice: Kahn's algorithm. Track the unmet dependencies of every package and
# who depends on whom; a heap of ready packages gives the alphabetical tie-break.
# Whatever is left when the heap runs dry is in (or behind) a cycle; a DFS names it.
# Time O(V log V + E), space O(V + E).
def install_order(packages: Dict[str, List[str]]) -> List[str]:
    remaining: Dict[str, Set[str]] = {}
    dependants: Dict[str, Set[str]] = {}
    for name, deps in packages.items():
        remaining.setdefault(name, set()).update(deps)
        dependants.setdefault(name, set())
        for dep in deps:
            remaining.setdefault(dep, set())
            dependants.setdefault(dep, set()).add(name)

    ready = [name for name, deps in remaining.items() if not deps]
    heapq.heapify(ready)
    order: List[str] = []
    while ready:
        name = heapq.heappop(ready)
        order.append(name)
        for dependant in dependants[name]:
            remaining[dependant].discard(name)
            if not remaining[dependant]:
                heapq.heappush(ready, dependant)

    if len(order) != len(remaining):
        unresolved = {name: deps for name, deps in remaining.items() if name not in order}
        cycle = _find_cycle(unresolved)
        raise ValueError("dependency cycle: " + " -> ".join(cycle))
    return order


# Brute force, for comparison: repeatedly scan every unplaced package and take the
# alphabetically first one whose dependencies are all placed. Same output; O(V^2 + V*E)
# because every round rescans everything, which shows on the 3,000-package chain.
def install_order_scan(packages: Dict[str, List[str]]) -> List[str]:
    deps: Dict[str, Set[str]] = {}
    for name, required in packages.items():
        deps.setdefault(name, set()).update(required)
        for dep in required:
            deps.setdefault(dep, set())
    placed: Set[str] = set()
    order: List[str] = []
    while len(order) < len(deps):
        candidates = sorted(name for name in deps if name not in placed and deps[name] <= placed)
        if not candidates:
            unresolved = {name: d for name, d in deps.items() if name not in placed}
            raise ValueError("dependency cycle: " + " -> ".join(_find_cycle(unresolved)))
        order.append(candidates[0])
        placed.add(candidates[0])
    return order
