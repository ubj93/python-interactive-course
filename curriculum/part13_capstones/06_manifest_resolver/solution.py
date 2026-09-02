"""Reference solution for manifest_resolver."""
from typing import Dict, Iterable, List, Optional, Set, Tuple


# Best practice: DFS with two sets. `done` stops repeated work (diamonds);
# `path` (the current recursion stack) is what detects a real cycle. Confusing the
# two is the classic bug: a single visited set reports diamonds as cycles, or
# misses cycles entirely, depending on when you add to it.
def expand_includes(manifests: Dict[str, dict], name: str) -> List[str]:
    order: List[str] = []
    done: Set[str] = set()
    path: List[str] = []

    def visit(current: str) -> None:
        if current in path:
            cycle = path[path.index(current):] + [current]
            raise ValueError("include cycle: " + " -> ".join(cycle))
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

    visit(name)
    return order


def _clean(items: Optional[Iterable[str]]) -> List[str]:
    return [s for s in ((item or "").strip() for item in items or []) if s]


def _dedupe(items: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def collect_items(manifests: Dict[str, dict], order: List[str]) -> Tuple[List[str], List[str]]:
    installs: List[str] = []
    uninstalls: List[str] = []
    for name in order:
        installs.extend(_clean(manifests[name].get("managed_installs")))
        uninstalls.extend(_clean(manifests[name].get("managed_uninstalls")))
    return _dedupe(installs), _dedupe(uninstalls)


def find_conflicts(installs: List[str], uninstalls: List[str]) -> List[str]:
    return sorted(set(installs) & set(uninstalls))


def resolve_manifest(manifests: Dict[str, dict], name: str, catalog: Optional[Iterable[str]] = None) -> dict:
    order = expand_includes(manifests, name)
    installs, uninstalls = collect_items(manifests, order)
    conflicts = find_conflicts(installs, uninstalls)
    conflict_set = set(conflicts)
    installs = [i for i in installs if i not in conflict_set]
    uninstalls = [u for u in uninstalls if u not in conflict_set]
    missing: List[str] = []
    if catalog is not None:
        known = set(catalog)
        missing = sorted({i for i in installs + uninstalls if i not in known})
    return {"manifests": order, "installs": installs, "uninstalls": uninstalls, "conflicts": conflicts, "missing": missing}
