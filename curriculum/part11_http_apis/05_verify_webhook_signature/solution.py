"""Reference solutions for sign_payload / verify_webhook_signature."""
import hashlib
import hmac
from typing import List, Mapping, Optional, Tuple, Union


def _bytes(value: Union[str, bytes]) -> bytes:
    return value.encode("utf-8") if isinstance(value, str) else value


# hmac.new(key, msg, digestmod): the key is the secret, the message is what we are
# vouching for. Prefixing the timestamp binds it to the signature so a replay cannot
# change it.
def sign_payload(secret: Union[str, bytes], body: Union[str, bytes], timestamp: int) -> str:
    message = f"{timestamp}.".encode("utf-8") + _bytes(body)
    return hmac.new(_bytes(secret), message, hashlib.sha256).hexdigest()


def _header(headers: Mapping[str, str], name: str) -> Optional[str]:
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return None


def _parse_signature(value: str) -> Tuple[Optional[int], List[str]]:
    timestamp, sigs = None, []
    for pair in value.split(","):
        key, sep, val = pair.strip().partition("=")
        if not sep:
            continue
        if key.strip() == "t":
            try:
                timestamp = int(val.strip())
            except ValueError:
                return None, []
        elif key.strip() == "v1":
            sigs.append(val.strip())
    return timestamp, sigs


# Best practice: cheap structural checks first (header present, parseable, fresh), the
# HMAC last, and a constant-time comparison. Each failure returns False; nothing raises.
def verify_webhook_signature(
    secret: Union[str, bytes],
    body: Union[str, bytes],
    headers: Mapping[str, str],
    now: int,
    tolerance: int = 300,
) -> bool:
    raw = _header(headers, "X-Signature")
    if not raw:
        return False
    timestamp, sigs = _parse_signature(raw)
    if timestamp is None or not sigs:
        return False
    if abs(now - timestamp) > tolerance:
        return False
    expected = sign_payload(secret, body, timestamp)
    return any(hmac.compare_digest(expected, sig) for sig in sigs)


# Clever: dict(parse_qsl(...)) would lose the repeated v1, so instead split into pairs and
# group with a defaultdict. Same semantics, fewer lines, and it shows you know that
# "key=value,key=value" is not quite a query string.
def _parse_signature_grouped(value: str):
    from collections import defaultdict
    groups = defaultdict(list)
    for pair in value.split(","):
        key, sep, val = pair.strip().partition("=")
        if sep:
            groups[key.strip()].append(val.strip())
    return groups
