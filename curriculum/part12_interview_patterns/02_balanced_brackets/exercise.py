"""Balanced brackets in a script line.

A linter for the shell one-liners we ship in launchd jobs and Jamf policies
needs to reject lines whose brackets do not match up. Write
`balanced_brackets(text)` that returns True when every bracket in the text
is properly opened and closed, and False otherwise.

Rules:
- three kinds of bracket count: () [] {}
- a closing bracket must close the most recently opened bracket that is
  still open, and it must be of the same kind ("([)]" is not balanced)
- every other character (letters, quotes, spaces, $, |) is ignored
- a closing bracket with nothing open is unbalanced (")(")
- brackets still open at the end of the text are unbalanced ("((")
- an empty string is balanced

Complexity target: O(n) time and O(n) extra space, one pass with a stack.
The last test has a line of 60,000 characters nested 5,000 deep.

Examples:
    >>> balanced_brackets('if [ -f "$f" ]; then echo "${f}"; fi')
    True
    >>> balanced_brackets("([)]")
    False
    >>> balanced_brackets("")
    True
"""


def balanced_brackets(text: str) -> bool:
    raise NotImplementedError("write balanced_brackets")
