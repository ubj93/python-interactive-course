"""Headers and URLs for a REST client.

Every MDM script starts by building the same two things: a headers dict with a
bearer token, and a URL with query parameters. Write both helpers.

`build_headers(token, extra=None)` returns a new dict every call:

- always contains "Accept": "application/json" and "User-Agent": "cpe-tools/1.0"
- contains "Authorization": "Bearer <token>" only when `token` is a non-empty
  string after stripping whitespace (the stripped token is used); when token is
  None or blank the key is omitted entirely. Never send "Bearer None".
- `extra`, when given, is merged last so it can override the defaults; the
  caller's dict is left untouched.

`build_url(base, path, params=None)`:

- joins base and path with exactly one "/" whatever slashes they start or end with
- appends "?" + `urllib.parse.urlencode(params, doseq=True)` when there is
  anything to encode; keys whose value is None are dropped first
- a list value becomes repeated keys: {"status": ["active", "stale"]} ->
  "status=active&status=stale"
- values are percent-encoded by urlencode ("a b" -> "a+b"); do not hand-roll it
- no "?" at all when params is None, empty, or only None values

Examples:
    >>> build_headers("abc123")
    {'Accept': 'application/json', 'User-Agent': 'cpe-tools/1.0', 'Authorization': 'Bearer abc123'}
    >>> build_headers(None)
    {'Accept': 'application/json', 'User-Agent': 'cpe-tools/1.0'}
    >>> build_url("https://mdm.example.com/api/", "/v1/devices", {"limit": 50, "q": "mbp lab"})
    'https://mdm.example.com/api/v1/devices?limit=50&q=mbp+lab'
"""
from typing import Any, Dict, Optional
from urllib.parse import urlencode


def build_headers(token: Optional[str], extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    raise NotImplementedError("write build_headers")


def build_url(base: str, path: str, params: Optional[Dict[str, Any]] = None) -> str:
    raise NotImplementedError("write build_url")
