"""Reference solutions for mask_secrets."""
import re

# Group 1 is everything to keep (key and separator, or "Bearer "), group 2 is the value.
# The alternation is wrapped so both branches expose the same two groups.
# (?i:...) scopes IGNORECASE to the key names only, so "Bearer" keeps its exact spelling.
SECRET = re.compile(
    r"((?i:password|passwd|secret|token|api_key|apikey)\s*[=:]\s*)([^\s;,&]+)"
    r"|(Bearer )([A-Za-z0-9._~+/=-]+)"
)


def _mask(value: str) -> str:
    keep = value[-4:] if len(value) > 4 else ""
    return "*" * (len(value) - len(keep)) + keep


# Best practice: re.sub with a callable. The callable decides what to do per match,
# so the masking rule lives in one small, testable function.
def mask_secrets(text: str) -> str:
    def replace(m: "re.Match") -> str:
        prefix = m.group(1) or m.group(3)
        value = m.group(2) or m.group(4)
        return prefix + _mask(value)

    return SECRET.sub(replace, text)


# Clever: keep the two patterns separate and run them in turn. Slightly more work per call,
# but each pattern reads on its own and "Bearer" is no longer case-insensitive.
KV_SECRET = re.compile(r"((?:password|passwd|secret|token|api_key|apikey)\s*[=:]\s*)([^\s;,&]+)", re.I)
BEARER = re.compile(r"(Bearer )([A-Za-z0-9._~+/=-]+)")


def mask_secrets_two_pass(text: str) -> str:
    repl = lambda m: m.group(1) + _mask(m.group(2))  # noqa: E731
    return BEARER.sub(repl, KV_SECRET.sub(repl, text))
