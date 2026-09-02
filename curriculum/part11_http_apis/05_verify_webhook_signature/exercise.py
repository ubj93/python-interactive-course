"""Verify a webhook signature.

The MDM posts a JSON payload to our endpoint whenever a device enrols. Anyone
on the internet can post to that endpoint too, so every request carries a
signature computed with a secret only we and the vendor know:

    X-Signature: t=1714813200,v1=5f1c...e2

`v1` is HMAC-SHA256, as lowercase hex, of the bytes `"<t>." + body` under the
shared secret. `t` is the unix time when the vendor signed it, which lets us
reject replays. Write two functions.

`sign_payload(secret, body, timestamp)` returns the hex signature string.
`secret` and `body` may be str (encode as UTF-8) or bytes.

`verify_webhook_signature(secret, body, headers, now, tolerance=300)` returns
True only when all of these hold, and False otherwise (never raise for bad input):

- the X-Signature header exists (header name matched case-insensitively)
- it parses as comma-separated key=value pairs with an integer `t` and at least
  one `v1`; whitespace around pairs is tolerated
- abs(now - t) <= tolerance seconds (`now` is injected by the caller)
- at least one `v1` value equals sign_payload(secret, body, t). Several v1
  entries can appear while the vendor rotates secrets; any match is enough.
- compare with `hmac.compare_digest`, never `==`, so timing does not leak which
  prefix of the signature was right

Examples:
    >>> sig = sign_payload("s3cret", b'{"event":"enrolled"}', 1714813200)
    >>> headers = {"X-Signature": f"t=1714813200,v1={sig}"}
    >>> verify_webhook_signature("s3cret", b'{"event":"enrolled"}', headers, now=1714813260)
    True
    >>> verify_webhook_signature("s3cret", b'{"event":"wiped"}', headers, now=1714813260)
    False
"""
import hashlib
import hmac
from typing import Mapping, Union


def sign_payload(secret: Union[str, bytes], body: Union[str, bytes], timestamp: int) -> str:
    raise NotImplementedError("write sign_payload")


def verify_webhook_signature(
    secret: Union[str, bytes],
    body: Union[str, bytes],
    headers: Mapping[str, str],
    now: int,
    tolerance: int = 300,
) -> bool:
    raise NotImplementedError("write verify_webhook_signature")
