"""Follow a cursor until the API runs out of pages.

The MDM lists devices 100 at a time. Each response looks like

    {"items": [...], "next_cursor": "eyJvZmZzZXQiOjEwMH0"}

and the last page has "next_cursor" set to null (or missing). To get the next
page you request the same URL with `cursor=<value>` added as a query parameter.

Write `fetch_all_pages(get, url, max_pages=100)` that returns one list with the
items of every page, in order. `get` is a callable `get(url) -> dict` (the parsed
JSON body). The tests pass a fake that serves canned pages and records the URLs
it was asked for; nothing touches the network.

Rules:
- the first request is `get(url)` exactly as given
- for every following page, build the URL from the *original* url: remove any
  existing `cursor` parameter, keep the other parameters in their order, and
  append `cursor=<next_cursor>` last. Use urllib.parse (urlsplit, parse_qsl,
  urlencode, urlunsplit) rather than string surgery.
- stop when next_cursor is missing, None or ""
- a page without an "items" key contributes nothing
- a cursor you have already used means the API is looping: raise PaginationError
  (defined below) instead of running forever
- if you would need more than max_pages requests, raise PaginationError
- do not catch exceptions raised by `get`; let them propagate

Examples:
    >>> pages = {
    ...     "https://mdm.example.com/v1/devices": {"items": [1, 2], "next_cursor": "c2"},
    ...     "https://mdm.example.com/v1/devices?cursor=c2": {"items": [3], "next_cursor": None},
    ... }
    >>> fetch_all_pages(pages.__getitem__, "https://mdm.example.com/v1/devices")
    [1, 2, 3]
"""
from typing import Any, Callable, Dict, List
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


class PaginationError(Exception):
    """Raised when pagination loops or exceeds the page budget."""


def fetch_all_pages(get: Callable[[str], Dict[str, Any]], url: str, max_pages: int = 100) -> List[Any]:
    raise NotImplementedError("write fetch_all_pages")
