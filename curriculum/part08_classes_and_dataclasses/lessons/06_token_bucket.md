# State and an injected clock

--- teach #card-d73e8217b57858f0
### Never read the wall clock inside the class
A rate limiter depends on time, and tests cannot wait for real seconds. So the class takes a `now` function in `__init__`, stores it, and calls `self._now()` whenever it needs the time. The tests pass a fake clock they move by hand; production passes `time.time`.
```python
class FakeClock:
    def __init__(self):
        self.t = 0.0
    def __call__(self):
        return self.t

clock = FakeClock()
bucket = TokenBucket(capacity=3, refill_per_second=1.0, now=clock)
```
`__call__` makes an object callable: `clock()` returns `clock.t`.

--- code #card-07564e7db575544e
Write a class `FakeClock` whose `__init__` sets `self.t = 0.0` and whose `__call__` returns `self.t`. Then create `clock = FakeClock()`.
```python
# your code here
```
check: clock() == 0.0
check: (setattr(clock, "t", 2.5), clock())[1] == 2.5
solution: class FakeClock:
solution:     def __init__(self):
solution:         self.t = 0.0
solution:     def __call__(self):
solution:         return self.t
solution: clock = FakeClock()
> `__call__` is the dunder behind `clock()`. The bucket never knows it is talking to a fake; it just calls `self._now()` and gets whatever `t` the test set.

--- teach #card-4e1c9042c1395250
### All state on `self`, validated up front
Check the arguments first and raise `ValueError`. Then store everything the object needs later: the capacity and rate, the clock, the token count, and when tokens were last refilled. Tokens are a `float` because half a second at one token per second gives half a token.
```python
def __init__(self, capacity, refill_per_second, now):
    if capacity < 1:
        raise ValueError(f"capacity must be >= 1, got {capacity}")
    if refill_per_second <= 0:
        raise ValueError("refill_per_second must be > 0")
    self.capacity = capacity
    self.rate = float(refill_per_second)
    self._now = now
    self._tokens = float(capacity)     # starts full
    self._last = now()
```

--- quiz #card-f188f5cd842553ed
Why is `self._tokens` stored as `float(capacity)` rather than `capacity`?
- [ ] Ints cannot be compared with floats
- [x] Refills add fractions of a token, and `available` must return a float
- [ ] Floats are faster
> `elapsed * rate` is usually fractional (0.5 seconds gives 0.5 tokens). Starting as a float keeps the type consistent from the first call.

--- teach #card-94c11b94730e5c64
### One private `_refill`, called at the start of every public call
Compute how long since the last refill, clamp a negative elapsed to zero (clocks can go backwards), add `elapsed * rate`, and never exceed capacity. Do this in one helper and call it first in `allow`, `available` and `seconds_until`, so the state is updated in exactly one place.
```python
def _refill(self):
    t = self._now()
    elapsed = max(0.0, t - self._last)
    self._tokens = min(float(self.capacity), self._tokens + elapsed * self.rate)
    self._last = t
```

--- code #card-ea71d294848955b5
Apply the refill rule: update `tokens` from the seconds elapsed between `last` and `now`, clamping a negative elapsed to zero and capping at `capacity`.
```python
capacity, rate = 3, 1.0
tokens, last, now = 0.5, 10.0, 12.0
```
check: tokens == 2.5
check: isinstance(tokens, float)
solution: elapsed = max(0.0, now - last)
solution: tokens = min(float(capacity), tokens + elapsed * rate)
> Two seconds at one token per second adds 2.0 to the 0.5 already there. `max(0.0, ...)` protects against a clock that went backwards, and `min(capacity, ...)` stops the bucket overflowing after a long wait.

--- teach #card-3cbb5e9543c050b9
### `allow` and `available`
`allow(cost)` first rejects a cost that could never succeed, then refills, then spends only if there is enough. A denied call spends nothing. `available` is a property that refills and returns the count.
```python
def allow(self, cost=1):
    if cost > self.capacity:
        raise ValueError(f"cost {cost} exceeds capacity {self.capacity}")
    self._refill()
    if self._tokens >= cost:
        self._tokens -= cost
        return True
    return False

@property
def available(self):
    self._refill()
    return self._tokens
```

--- fill #card-efae2a65f9e15c5c
Complete the test so a call is allowed only when there are enough tokens.
```python
if self._tokens ___ cost:
    self._tokens -= cost
    return True
return False
```
answer: >=
> Exactly `cost` tokens is enough, so the comparison is `>=`. With `>` a full bucket of 1 would deny a cost of 1.

--- teach #card-3e6070d089885554
### `seconds_until`: how long until enough tokens
After refilling, if the tokens already cover the cost the wait is `0.0`. Otherwise the shortfall divided by the rate is the wait in seconds. The same cost check as `allow` applies.
```python
def seconds_until(self, cost=1):
    if cost > self.capacity:
        raise ValueError(f"cost {cost} exceeds capacity {self.capacity}")
    self._refill()
    if self._tokens >= cost:
        return 0.0
    return (cost - self._tokens) / self.rate
```
Empty bucket, cost 1, half a token per second: `(1 - 0) / 0.5` is 2.0 seconds.

--- exercise 8.6 #card-fa90ee9dfda15a04

--- recap #card-079550f639325d6b
- Take a `now` callable in `__init__`; never call `time.time()` in the class.
- Validate arguments, then keep every piece of state on `self`.
- One `_refill` helper, called first in every public method; clamp negative elapsed, cap at capacity.
- `allow` spends only on success; `seconds_until` is `(cost - tokens) / rate`.
