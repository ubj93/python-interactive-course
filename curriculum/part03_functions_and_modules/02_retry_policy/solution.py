"""Reference solutions for retry_policy."""
from typing import Any, Dict

DEFAULTS: Dict[str, Any] = {
    "max_attempts": 3,
    "base_delay": 1.0,
    "max_delay": 30.0,
    "backoff": 2.0,
    "retry_on": (429, 500, 502, 503, 504),
}


# Best practice: reject unknown keys before anything else (the thing **kwargs does NOT
# do for you), copy the defaults so the module-level dict is never mutated, then
# validate the merged result rather than each override in isolation, because the
# base/max relationship depends on both.
def retry_policy(**overrides: Any) -> Dict[str, Any]:
    unknown = set(overrides) - set(DEFAULTS)
    if unknown:
        raise TypeError(f"unexpected keyword argument {sorted(unknown)[0]!r}")
    policy = dict(DEFAULTS)
    policy.update(overrides)

    attempts = policy["max_attempts"]
    if not isinstance(attempts, int) or attempts < 1:
        raise ValueError(f"max_attempts must be an int >= 1, got {attempts!r}")
    if policy["base_delay"] < 0 or policy["max_delay"] < 0:
        raise ValueError("delays must be >= 0")
    if policy["max_delay"] < policy["base_delay"]:
        raise ValueError("max_delay must be >= base_delay")
    if policy["backoff"] < 1:
        raise ValueError(f"backoff must be >= 1, got {policy['backoff']!r}")
    policy["retry_on"] = tuple(sorted(set(policy["retry_on"])))
    return policy


# Clever: explicit keyword-only parameters. Python now raises TypeError for unknown
# names on its own, editors autocomplete the options, and the defaults are visible in
# the signature. This is what you should write when the keys are known up front;
# **kwargs is for forwarding options you do not interpret.
def retry_policy_explicit(
    *,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff: float = 2.0,
    retry_on: Any = (429, 500, 502, 503, 504),
) -> Dict[str, Any]:
    if not isinstance(max_attempts, int) or max_attempts < 1:
        raise ValueError(f"max_attempts must be an int >= 1, got {max_attempts!r}")
    if base_delay < 0 or max_delay < 0 or max_delay < base_delay:
        raise ValueError("delays must be >= 0 and max_delay >= base_delay")
    if backoff < 1:
        raise ValueError(f"backoff must be >= 1, got {backoff!r}")
    return {
        "max_attempts": max_attempts,
        "base_delay": base_delay,
        "max_delay": max_delay,
        "backoff": backoff,
        "retry_on": tuple(sorted(set(retry_on))),
    }
