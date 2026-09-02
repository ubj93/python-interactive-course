"""Reference solutions for build_headers / build_url."""
from typing import Any, Dict, Optional
from urllib.parse import urlencode


# Best practice: start from a literal (a fresh dict each call), add the optional key only
# when there is something to send, and merge extra last so it can override. dict.update
# on our own dict never touches the caller's.
def build_headers(token: Optional[str], extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers = {"Accept": "application/json", "User-Agent": "cpe-tools/1.0"}
    token = (token or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra:
        headers.update(extra)
    return headers


# rstrip/lstrip make the join independent of how the caller wrote the pieces; urlencode
# with doseq=True does the escaping and the repeated keys.
def build_url(base: str, path: str, params: Optional[Dict[str, Any]] = None) -> str:
    url = base.rstrip("/") + "/" + path.lstrip("/")
    clean = {k: v for k, v in (params or {}).items() if v is not None}
    if clean:
        url += "?" + urlencode(clean, doseq=True)
    return url


# Clever: dict unpacking builds the merged dict in one expression; later keys win, which
# is exactly the override rule. Same behaviour, reads like the spec.
def build_headers_unpack(token: Optional[str], extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    token = (token or "").strip()
    auth = {"Authorization": f"Bearer {token}"} if token else {}
    return {"Accept": "application/json", "User-Agent": "cpe-tools/1.0", **auth, **(extra or {})}
