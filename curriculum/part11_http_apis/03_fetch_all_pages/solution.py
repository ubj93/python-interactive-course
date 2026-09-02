"""Reference solutions for fetch_all_pages."""
from typing import Any, Callable, Dict, Iterator, List
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


class PaginationError(Exception):
    """Raised when pagination loops or exceeds the page budget."""


# urlsplit/urlunsplit keep scheme, host and path intact; parse_qsl gives an ordered list of
# pairs so we can drop the old cursor and append the new one without disturbing the rest.
def _with_cursor(url: str, cursor: str) -> str:
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k != "cursor"]
    query.append(("cursor", cursor))
    return urlunsplit(parts._replace(query=urlencode(query)))


# Best practice: a loop with a visited set and a page budget. The two guards are what
# separate "works on the happy path" from "safe to run unattended at 3am".
def fetch_all_pages(get: Callable[[str], Dict[str, Any]], url: str, max_pages: int = 100) -> List[Any]:
    items: List[Any] = []
    seen = set()
    next_url = url
    for _ in range(max_pages):
        body = get(next_url)
        items.extend(body.get("items") or [])
        cursor = body.get("next_cursor")
        if not cursor:
            return items
        if cursor in seen:
            raise PaginationError(f"cursor {cursor!r} repeated; the API is looping")
        seen.add(cursor)
        next_url = _with_cursor(url, cursor)
    raise PaginationError(f"more than {max_pages} pages")


# Clever: a generator yields pages lazily so a caller can stop early or stream to disk;
# the eager list version is just list(chain.from_iterable(...)). Same guards, same URLs.
def iter_pages(get: Callable[[str], Dict[str, Any]], url: str, max_pages: int = 100) -> Iterator[List[Any]]:
    seen = set()
    next_url = url
    for _ in range(max_pages):
        body = get(next_url)
        yield body.get("items") or []
        cursor = body.get("next_cursor")
        if not cursor:
            return
        if cursor in seen:
            raise PaginationError(f"cursor {cursor!r} repeated; the API is looping")
        seen.add(cursor)
        next_url = _with_cursor(url, cursor)
    raise PaginationError(f"more than {max_pages} pages")


def fetch_all_pages_lazy(get: Callable[[str], Dict[str, Any]], url: str, max_pages: int = 100) -> List[Any]:
    return [item for page in iter_pages(get, url, max_pages) for item in page]
