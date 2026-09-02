"""Reference solutions for balanced_brackets."""

PAIRS = {")": "(", "]": "[", "}": "{"}


# Best practice: a list used as a stack. Openers are pushed; a closer must match the
# top. Whatever is left on the stack at the end was never closed.
# Time O(n), space O(n) (worst case every character is an opener).
def balanced_brackets(text: str) -> bool:
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in PAIRS:
            if not stack or stack.pop() != PAIRS[ch]:
                return False
    return not stack


# Alternative: push the *expected closer* instead of the opener, so the comparison
# at pop time is a plain equality with no lookup. Same complexity, slightly less code.
CLOSER = {"(": ")", "[": "]", "{": "}"}


def balanced_brackets_expected(text: str) -> bool:
    expected = []
    for ch in text:
        if ch in CLOSER:
            expected.append(CLOSER[ch])
        elif ch in ")]}":
            if not expected or expected.pop() != ch:
                return False
    return not expected
