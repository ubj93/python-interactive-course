"""Manifest resolver: includes, installs, uninstalls, conflicts.

Munki-style manifests are a dict of name -> manifest, and a manifest may include
other manifests. Given the whole set and a starting manifest, work out what a
client would end up installing and removing, in a stable order, and flag the
contradictions.

    manifests = {
        "site_default": {"included_manifests": ["security_baseline"], "managed_installs": ["Chrome", "Slack"]},
        "security_baseline": {"managed_installs": ["CrowdStrike"], "managed_uninstalls": ["Slack"]},
        "eng_laptops": {"included_manifests": ["site_default", "security_baseline"], "managed_installs": ["Docker"]},
    }

Every key is optional. Item names are stripped; empty names are ignored.

expand_includes(manifests, name) -> list of manifest names
- depth-first, pre-order: the manifest itself, then each of its includes in
  listed order, recursively; a manifest already visited is not visited again
  (a diamond is fine)
- a name not present in `manifests` raises KeyError
- an include cycle raises ValueError whose message contains the cycle as names
  joined by " -> ", for example "a -> b -> a"

collect_items(manifests, order) -> (installs, uninstalls)
- walk the manifests in `order`; each list keeps items in first-seen order with
  duplicates dropped

find_conflicts(installs, uninstalls) -> list
- sorted names present in both lists

resolve_manifest(manifests, name, catalog=None) -> dict
- {"manifests": order, "installs": [...], "uninstalls": [...],
   "conflicts": [...], "missing": [...]}
- conflicting items are removed from BOTH installs and uninstalls and listed
  in "conflicts" (a human has to pick)
- when `catalog` (an iterable of known item names) is given, "missing" is the
  sorted list of remaining installs and uninstalls that are not in it; the
  items stay in their lists. Without a catalog, "missing" is []

Examples:
    >>> expand_includes(manifests, "eng_laptops")
    ['eng_laptops', 'site_default', 'security_baseline']
    >>> resolve_manifest(manifests, "eng_laptops")["conflicts"]
    ['Slack']
    >>> resolve_manifest(manifests, "eng_laptops")["installs"]
    ['Docker', 'Chrome', 'CrowdStrike']
"""
from typing import Dict, Iterable, List, Optional, Tuple


def expand_includes(manifests: Dict[str, dict], name: str) -> List[str]:
    raise NotImplementedError("write expand_includes")


def collect_items(manifests: Dict[str, dict], order: List[str]) -> Tuple[List[str], List[str]]:
    raise NotImplementedError("write collect_items")


def find_conflicts(installs: List[str], uninstalls: List[str]) -> List[str]:
    raise NotImplementedError("write find_conflicts")


def resolve_manifest(manifests: Dict[str, dict], name: str, catalog: Optional[Iterable[str]] = None) -> dict:
    raise NotImplementedError("write resolve_manifest")
