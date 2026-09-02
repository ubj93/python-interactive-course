"""Reference solutions for snake_to_camel and camel_to_snake."""
import re

# Two passes: first split "ACRONYMWord" into "ACRONYM_Word", then split "aB" / "1B".
_ACRONYM_THEN_WORD = re.compile(r"([A-Z]+)([A-Z][a-z])")
_LOWER_OR_DIGIT_THEN_UPPER = re.compile(r"([a-z0-9])([A-Z])")


# Best practice: split, drop empties, capitalize() each word after the first.
# str.capitalize lowercases the rest of the word and only uppercases the first character,
# which is exactly the camelCase rule; str.title would also capitalise after digits.
def snake_to_camel(name: str) -> str:
    words = [w.lower() for w in name.split("_") if w]
    if not words:
        return ""
    return words[0] + "".join(w.capitalize() for w in words[1:])


# Best practice: two small regex substitutions with backreferences, then lower().
# Each pattern says one thing; together they handle acronyms without a hand-written scanner.
def camel_to_snake(name: str) -> str:
    s = _ACRONYM_THEN_WORD.sub(r"\1_\2", name)
    s = _LOWER_OR_DIGIT_THEN_UPPER.sub(r"\1_\2", s)
    return s.lower()


# Clever: a single scan that decides, per character, whether a word boundary sits before it.
# Slower to read than the regex version, but it makes the acronym rule explicit.
def camel_to_snake_scan(name: str) -> str:
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            prev = name[i - 1]
            nxt = name[i + 1] if i + 1 < len(name) else ""
            starts_word = prev.islower() or prev.isdigit() or (prev.isupper() and nxt.islower())
            if starts_word:
                out.append("_")
        out.append(ch.lower())
    return "".join(out)
