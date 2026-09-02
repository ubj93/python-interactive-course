# Generator functions

--- teach
### `yield` makes a function lazy
A function that contains `yield` does not run when you call it. It returns a **generator**, and its body runs only when something asks for a value: it runs to the next `yield`, hands the value out, and pauses there until asked again.
```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

>>> gen = countdown(3)
>>> next(gen)
3
>>> list(gen)        # the rest
[2, 1]
```
`for` loops, `list()` and `next()` all pull values this way.

--- code
Write a generator function `evens(n)` that yields 0, 2, 4, ... for every even number below `n`. Then print `list(evens(7))`.
```python
# your code here
```
expect: [0, 2, 4, 6]
check: next(evens(5)) == 0
solution: def evens(n):
solution:     for i in range(0, n, 2):
solution:         yield i
solution: print(list(evens(7)))
> `yield` inside the loop hands out one value per pass and pauses. `list()` keeps asking until the loop ends, which is when the generator is exhausted.

--- predict
What does this print?
```python
def hosts():
    yield "mbp-j-doe"
    yield "win-lab-01"

gen = hosts()
print(next(gen))
```
answer: mbp-j-doe
> The body runs up to the first `yield` and pauses. A second `next(gen)` would resume and give `win-lab-01`.

--- teach
### Pull `n` items at a time with `islice`
`iter(iterable)` gives an iterator you can pull from. `itertools.islice(it, n)` takes up to `n` items from it, lazily, without indexing or knowing the length. Wrap it in `tuple(...)` to actually take them. When the iterator is exhausted, you get an empty tuple.
```python
>>> from itertools import islice
>>> it = iter(["a", "b", "c"])
>>> tuple(islice(it, 2))
('a', 'b')
>>> tuple(islice(it, 2))
('c',)
```
This works on any iterable: a list, a file, an infinite `count()`.

--- code
Set `batch` to a tuple of the first two items pulled from `it`, leaving the rest in place.
```python
from itertools import islice
it = iter(["a", "b", "c"])
```
check: batch == ("a", "b")
check: next(it) == "c"
solution: batch = tuple(islice(it, 2))
> `islice(it, 2)` pulls exactly two items from the shared iterator and `tuple()` collects them. The iterator remembers its position, so the next pull starts at `"c"`.

--- teach
### The batching loop
Keep taking a tuple of `n`. An empty tuple means the input ran out: `return` ends the generator. Otherwise `yield` the batch and go round again.
```python
def _batches(it, n):
    while True:
        batch = tuple(islice(it, n))
        if not batch:
            return
        yield batch
```
Because each round pulls only `n` items, an infinite input is fine: the caller stops asking, so the loop stops pulling.

--- quiz
What does `return` do inside a generator function?
- [ ] Returns the value to the caller of `next()`
- [x] Ends the stream; the consumer sees `StopIteration` and a `for` loop simply finishes
- [ ] Raises a `ValueError`
> A generator cannot hand a return value to `next()`; reaching `return` (or the end of the body) means "no more items". `list()` and `for` handle that quietly.

--- teach
### Validate in a normal function, then return the generator
Because a generator body is delayed, an `if n < 1: raise` inside it would not fire until the first `next()`. The exercise wants the error at call time. So the public function is a *normal* function: it checks, then returns the generator built by the inner function.
```python
def batched(iterable, n):
    if n < 1:
        raise ValueError("n must be >= 1")
    return _batches(iter(iterable), n)
```
`batched` has no `yield`, so its body runs immediately.

--- quiz
The `n < 1` check is inside the generator body. When does `batched([1, 2], 0)` raise?
- [ ] Immediately, when `batched` is called
- [x] Only when the first value is requested with `next()` or `list()`
- [ ] Never
> Nothing in a generator body runs until the first pull. That is the delayed-validation trap interviewers probe; splitting the function fixes it.

--- exercise 9.2

--- recap
- A function with `yield` returns a generator; its body runs only when values are pulled.
- `tuple(islice(it, n))` takes up to `n` items from an iterator; empty means exhausted.
- `return` in a generator ends the stream.
- Validate in a normal wrapper that returns the generator, so errors are raised at call time.
