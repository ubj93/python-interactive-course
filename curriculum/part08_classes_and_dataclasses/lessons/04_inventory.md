# Container protocols

--- teach
### Has a dict, is not a dict
An `Inventory` could inherit from `dict`, but then `update`, `setdefault` and `inv[k] = v` would all skip your checks. Instead, keep a dict *inside* the object and expose only the operations you mean to support. The leading underscore in `_by_serial` says "internal, not part of the API".
```python
class Inventory:
    def __init__(self):
        self._by_serial = {}

    def add(self, device):
        if device.serial in self._by_serial:
            raise ValueError(f"duplicate serial: {device.serial}")
        self._by_serial[device.serial] = device
```
This is composition: the container *has* a dict.

--- quiz
Why not write `class Inventory(dict)` and add an `add` method?
- [ ] Dicts cannot be subclassed
- [x] Callers could still use `inv[k] = v` or `update` and bypass the duplicate check
- [ ] Subclasses of dict lose insertion order
> Inheriting exposes the whole parent API. Every dict method that writes would skip `add`. Composition means the only way in is the method you wrote.

--- teach
### `__len__` and `__getitem__`
`len(inv)` calls `inv.__len__()`. `inv["C02X"]` calls `inv.__getitem__("C02X")`, and a missing key should raise `KeyError`. Indexing the internal dict already does exactly that, so pass the work through.
```python
def __len__(self):
    return len(self._by_serial)

def __getitem__(self, serial):
    return self._by_serial[serial]
```
`get(serial, default=None)` is the same idea with `self._by_serial.get(serial, default)`, and `remove` uses `self._by_serial.pop(serial)`, which deletes and returns the value, or raises `KeyError`.

--- predict
What does this print?
```python
class Box:
    def __len__(self):
        return 3

print(len(Box()))
```
answer: 3
> `len()` does not count anything itself; it calls the object's `__len__` and trusts the answer.

--- teach
### `__iter__` must hand out a fresh iterator
`for d in inv` calls `inv.__iter__()` and then `next()` on what comes back. Return the iterator of the internal container each time and every loop starts from the beginning. Dict values keep insertion order, which is what the exercise asks for.
```python
def __iter__(self):
    return iter(self._by_serial.values())
```
A generator function with `yield` also works. What does not work: returning `self` with a `__next__` that keeps a position, because then the inventory can only be looped over once.

--- quiz
`__iter__` returns `self`, and `__next__` advances a counter stored on `self`. What goes wrong?
- [ ] `for` refuses objects that return themselves
- [x] The second loop over the object starts where the first one stopped, or is empty
- [ ] `len()` stops working
> The position lives on the one object, so it is not reset between loops. A fresh iterator per call (`iter(...)` or a generator) keeps no state on the inventory.

--- teach
### `__contains__` decides what `in` accepts
`x in inv` calls `inv.__contains__(x)`. Here `x` may be a serial string or a Device, so branch on the type with `isinstance` and answer `False` for anything else, rather than raising.
```python
def __contains__(self, item):
    if isinstance(item, str):
        return item in self._by_serial
    if isinstance(item, Device):
        return item.serial in self._by_serial
    return False
```
Without `__contains__`, Python would fall back to iterating and comparing, which is slower and would never match a serial string.

--- fill
Complete the branch that handles a serial string.
```python
if isinstance(item, ___):
    return item in self._by_serial
```
answer: str
> A serial is text, so `str` is the type to test. The Device branch reads `item.serial` first, and the final `return False` covers `42` or `None`.

--- teach
### The optional constructor argument
`Inventory(devices)` should add each device through `add`, so duplicates raise. `devices` defaults to `None`, and it may be a one-shot iterator, so loop over it exactly once.
```python
def __init__(self, devices=None):
    self._by_serial = {}
    if devices is not None:
        for device in devices:
            self.add(device)
```
Never write `devices=[]` as the default; that is the mutable default argument trap from Part 3.

--- exercise 8.4

--- recap
- Compose: the inventory *has* a dict; only `add` writes to it.
- `__len__`, `__getitem__` (raise `KeyError`) and `__contains__` map `len`, `[]` and `in` onto the dict.
- `__iter__` returns a fresh iterator each call: `iter(self._by_serial.values())`.
- `dict.pop` deletes and returns; `dict.get` takes a default.
