"""Reference solutions for normalize_hostname."""


# Best practice: a chain of string methods, one rule per call, in the order the spec lists them.
def normalize_hostname(raw: str) -> str:
    return raw.strip().lower().split(".")[0].replace("_", "-")


# Clever: str.partition returns (before, sep, after) and never raises, so it avoids the [0].
def normalize_hostname_partition(raw: str) -> str:
    head, _, _ = raw.strip().lower().partition(".")
    return head.replace("_", "-")
