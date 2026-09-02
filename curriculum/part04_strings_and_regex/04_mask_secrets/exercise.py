"""Mask secrets before a log line reaches a ticket.

Our helpdesk integration copies log lines into tickets. Write `mask_secrets(text)`
that returns the text with secret values masked so that only the last four
characters remain visible; every other character of the value becomes '*'. The
length of the value must not change, and everything around it stays as it was.

Two things count as a secret:

1. Key/value pairs whose key is one of: password, passwd, secret, token, api_key,
   apikey (matched case-insensitively). The key is followed by '=' or ':' with
   optional spaces on either side, then the value. The value runs until the next
   whitespace, ';', ',' or '&' character, or the end of the text. Keep the key
   and separator exactly as written.

2. Bearer tokens: the word "Bearer" (this exact capitalisation), one space, then
   the token, which is a run of letters, digits and the characters . _ - ~ + / =

Rules:
- a value of four characters or fewer is masked completely
- a key with nothing after the separator (end of text, or straight into ';')
  has no value and is left alone
- other key/value pairs such as user=jdoe are never touched
- the function must not change text that contains no secrets

Examples:
    >>> mask_secrets("user=jdoe password=hunter2secret")
    'user=jdoe password=*********cret'
    >>> mask_secrets("Authorization: Bearer abc123def456ghi7")
    'Authorization: Bearer ************ghi7'
    >>> mask_secrets("Token: ab")
    'Token: **'
"""
import re


def mask_secrets(text: str) -> str:
    raise NotImplementedError("write mask_secrets")
