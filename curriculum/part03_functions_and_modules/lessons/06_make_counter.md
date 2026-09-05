# Putting it together: private state

--- teach #card-93c6a9ca1633594f
### Remembering between calls, without a global
"Give me a function that returns 100, then 101, then 102." The tempting answer is a global counter; it makes the function untestable and every counter shares it. The Python answer is a closure: an outer function holds the state, an inner function uses it, and you return the inner function. You built one in the `compose` lesson.
```python
def make_counter(start=0):
    current = start
    def next_value():
        ...
    return next_value
```
Each call to `make_counter` runs the outer body again, so each counter gets its own `current`.

--- teach #card-055e2282b9cb5853
### Assigning inside a function makes the name local
Reading an outer variable from an inner function just works. Assigning to it does not: Python then treats the name as a brand-new local, and `current += 1` fails with `UnboundLocalError` because the local has no value yet.
```python
def make_counter(start=0):
    current = start
    def next_value():
        current += 1        # UnboundLocalError
        return current
    return next_value
```
Reading is fine; rebinding needs a declaration.

--- quiz #card-ba19c8d71be4522d
Why does `current += 1` inside `next_value` raise `UnboundLocalError`?
- [ ] `current` was never defined anywhere
- [x] Assigning makes `current` local to `next_value`, and that local has no value yet
- [ ] Inner functions cannot see outer variables
> Any assignment in a function makes the name local for that whole function. The read on the right side of `+=` then finds an unset local, not the outer variable.

--- teach #card-cda76122c12152b9
### `nonlocal` points at the enclosing variable
`nonlocal current` says "the `current` I assign to is the one in the outer function". Now the inner function updates the shared state and keeps it between calls. Return the old value, then move on by `step`.
```python
def make_counter(start=0, step=1):
    current = start
    def next_value():
        nonlocal current
        value = current
        current += step
        return value
    return next_value
```
`global` would do the same for a module-level name; it is almost always the wrong fix.

--- code #card-c0808cbc7cef54f0
Write the body of `make_ticker(start)`: the returned function gives back the current value and then adds 1 for next time. Then make a ticker starting at 5 and print two calls on separate lines.
```python
def make_ticker(start):
```
expect: 5\n6
solution:     current = start
solution:     def tick():
solution:         nonlocal current
solution:         value = current
solution:         current += 1
solution:         return value
solution:     return tick
solution: t = make_ticker(5)
solution: print(t())
solution: print(t())
> `nonlocal current` lets `tick` rebind the outer variable, so the increment survives between calls. Return the old value first, then step.

--- predict #card-9369c7b88dc0595a
What does this print?
```python
def make_counter(start=0, step=1):
    current = start
    def next_value():
        nonlocal current
        value = current
        current += step
        return value
    return next_value

tick = make_counter(10, 5)
tick()
print(tick())
```
answer: 15
> The first call returns 10 and moves `current` to 15. The second call returns 15. `start` comes out first; `step` is added after.

--- fill #card-44476baf5ccc5628
Complete the declaration so the inner function can update the outer `current`.
```python
def next_value():
    ___ current
    value = current
    current += step
    return value
```
answer: nonlocal
> `nonlocal` binds the name to the enclosing function's variable. Without it, `current += step` would create an unset local and crash.

--- teach #card-63c5e0a1359652a0
### Mutating is not rebinding
A dict held by the outer function can be changed from the inner one with no declaration at all: `counts[key] = ...` mutates the dict, it does not assign a new value to the name `counts`. So a per-hostname tracker needs no `nonlocal`. Normalise the key for comparison only, as in Part 2.
```python
def make_checkin_tracker():
    counts = {}
    def record(hostname):
        key = hostname.strip().lower()
        counts[key] = counts.get(key, 0) + 1
        return counts[key]
    return record
```
`counts.get(key, 0)` is 0 for a first-time hostname, so the first call returns 1.

--- code #card-52d1fe1f7b0f5bb7
Write the body of `make_tally()`: it returns a function `add(key)` that counts how often each key has been seen and returns the new count, with no `nonlocal`. Then make a tally and print `add("a")`, `add("b")`, `add("a")` on separate lines.
```python
def make_tally():
```
expect: 1\n1\n2
solution:     counts = {}
solution:     def add(key):
solution:         counts[key] = counts.get(key, 0) + 1
solution:         return counts[key]
solution:     return add
solution: add = make_tally()
solution: print(add("a"))
solution: print(add("b"))
solution: print(add("a"))
> `counts[key] = ...` mutates the dict the outer `counts` points at; the name is never reassigned, so no declaration is needed.

--- quiz #card-d47c9f48c6f75a24
Which inner-function line needs `nonlocal` to work?
- [ ] `counts[key] = counts.get(key, 0) + 1`
- [x] `total = total + 1`
- [ ] `seen.add(key)`
> Only rebinding a name (`total = ...`) makes it local. Item assignment on a dict and `.add` on a set mutate the object the outer name points at, and need no declaration.

--- exercise 3.6 #card-8b9690a33ee750d7

--- recap #card-9f9ee40dd12058f2
- A closure holds state in the outer function and returns the inner function.
- Assigning to an outer name inside a function makes it local; `nonlocal` fixes that.
- Mutating a dict or set through an outer name needs no declaration.
- Each factory call creates independent state; no globals, no classes.
