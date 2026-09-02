# The stack pattern: balanced brackets

--- teach
### The pattern: "the most recently opened thing"
A linter must reject shell lines whose brackets do not match. A brute force that many people reach for: keep deleting adjacent pairs until nothing changes.
```python
def balanced_slow(text):
    text = "".join(ch for ch in text if ch in "()[]{}")
    while "()" in text or "[]" in text or "{}" in text:
        text = text.replace("()", "").replace("[]", "").replace("{}", "")
    return text == ""
```
It works, but every `replace` copies the whole string, and a line nested 5,000 deep needs 5,000 rounds. Whenever the rule is "the last thing opened must be the first thing closed", the pattern is a **stack**.

--- quiz
For a line with n bracket characters nested n/2 deep, what does the delete-pairs loop cost?
- [ ] O(n): one pass
- [x] O(n²): each of n/2 rounds scans and copies the whole string
- [ ] O(log n): the string halves every round
> Only the innermost pair matches on each round, so the loop runs n/2 times, and each round is an O(n) scan plus copy. That is quadratic.

--- teach
### A stack is a list you only touch at the end
`append` pushes, `pop` takes the most recent item back. Both are O(1). Walk the text once: push every opener; on a closer, pop and check it matches. A dict maps each closer to the opener it needs.
```python
PAIRS = {")": "(", "]": "[", "}": "{"}

stack = []
for ch in text:
    if ch in "([{":
        stack.append(ch)
    elif ch in PAIRS:
        if not stack or stack.pop() != PAIRS[ch]:
            return False
```
Every other character (letters, quotes, `$`, `|`) falls through both branches and is ignored.

--- code
Walk `text`: push every opener onto `stack`, and on every closer pop one item. Then print `stack`.
```python
PAIRS = {")": "(", "]": "[", "}": "{"}
stack = []
text = "([]"
```
expect: ['(']
solution: for ch in text:
solution:     if ch in "([{":
solution:         stack.append(ch)
solution:     elif ch in PAIRS:
solution:         stack.pop()
solution: print(stack)
> `(` and `[` are pushed, `]` pops the `[`, and the loop ends with `(` still open. A leftover on the stack is what tells you the text is unbalanced.

--- predict
What does this print?
```python
stack = []
for ch in "{[(":
    stack.append(ch)
print(stack.pop())
```
answer: (
> `pop()` with no argument removes and returns the *last* item pushed. The stack was `['{', '[', '(']`, so `(` comes off first. That is exactly why a stack matches "most recently opened".

--- teach
### The three ways to be unbalanced
Test these out loud before you code; each maps to one line.
- A closer with nothing open, `")("`: the stack is empty when `)` arrives. That is the `not stack` guard.
- The wrong kind of closer, `"([)]"`: `)` arrives but the top is `[`. That is the `!= PAIRS[ch]` check.
- Something left open, `"(("`: the loop ends with items still on the stack.

The last one is the classic miss. After the loop, return `not stack`: an empty stack means every opener was closed.

--- code
`ch` is a closer that has just arrived. Print `wrong` if the stack is empty or the item on top is not the opener it needs; otherwise print `ok`.
```python
PAIRS = {")": "(", "]": "[", "}": "{"}
stack = ["(", "["]
ch = ")"
```
expect: wrong
solution: if not stack or stack.pop() != PAIRS[ch]:
solution:     print("wrong")
solution: else:
solution:     print("ok")
> The top of the stack is `[`, but `)` needs `(`. That is the `"([)]"` case: right bracket, wrong kind. The `not stack` test must come first so `pop()` is never called on an empty list.

--- quiz
A candidate ends the function with `return True` instead of `return not stack`. Which input passes when it should fail?
- [ ] `")("`
- [ ] `"([)]"`
- [x] `"{[()]"`
> The loop never sees a bad closer in `"{[()]"`; it just finishes with `{` and `[` still on the stack. Only `return not stack` catches leftovers.

--- fill
Complete the check that rejects a closer with nothing open or of the wrong kind.
```python
elif ch in PAIRS:
    if not stack or stack.pop() ___ PAIRS[ch]:
        return False
```
answer: !=
> `PAIRS[ch]` is the opener this closer needs. If the popped item is a different opener, the nesting is wrong. The `not stack` check must come first, because `pop()` on an empty list raises.

--- teach
### The cost, and how to say it
One pass, each character pushed and popped at most once: O(n) time. The stack can hold every opener, so O(n) extra space in the worst case (a line nested 5,000 deep).

Say it out loud: "This is the stack pattern. The stack holds the brackets that are still open; a closer must match the top. O(n) time, O(n) space, and I check three failure cases: a closer with nothing open, the wrong kind, and leftovers at the end."

An empty string is balanced: the loop does nothing and `not []` is `True`.

--- exercise 12.2

--- recap
- "Most recently opened must close first" means a stack: `append` and `pop` from the end.
- A dict from closer to opener makes the match check one line.
- Three failures: empty stack on a closer, wrong opener on top, and leftovers after the loop.
- `return not stack` at the end; O(n) time, O(n) space.
