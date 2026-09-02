# Your first class

--- teach
### A class is a blueprint; `__init__` fills it in
`class Device:` declares a new type. `__init__` is the method Python runs when you build one with `Device(...)`. Its first parameter, `self`, is the object being built; `self.hostname = ...` stores a value on that object as an attribute. Normalise input here, once, so no other code has to.
```python
class Device:
    def __init__(self, hostname, serial):
        self.hostname = hostname.strip().lower()
        self.serial = serial

d = Device("  MBP-J-DOE ", "C02XG1234ABC")
```
You never pass `self` yourself; Python fills it in.

--- code
Write the body of `__init__` (indented eight spaces): store `hostname` stripped and lowercased, and `serial` exactly as given.
```python
class Device:
    def __init__(self, hostname, serial):
```
check: Device("  MBP-J-DOE ", "C02X").hostname == "mbp-j-doe"
check: Device("a", "C02X").serial == "C02X"
solution:         self.hostname = hostname.strip().lower()
solution:         self.serial = serial
> Each `self.name = value` line creates an attribute on the new object. The clean-up happens once here, so every later read of `hostname` is already normalised.

--- teach
### Methods are functions that get `self`
Any `def` inside the class body is a method. Call it with a dot and Python passes the object as `self`, so the method can read its own attributes.
```python
class Device:
    ...
    def describe(self):
        return f"{self.hostname} ({self.serial})"

>>> d.describe()
'mbp-j-doe (C02XG1234ABC)'
```
`d.describe()` and `Device.describe(d)` are the same call. That is all `self` is: the first argument.

--- fill
Complete the method so it reads the object's own attribute.
```python
def describe(self):
    return f"{___.hostname}: {self.os_name}, {self.ram_gb} GB RAM"
```
answer: self
> Inside a method, attributes live on `self`. A bare `hostname` would be an undefined name.

--- teach
### `__repr__`: how the object prints
Without it, printing `d` shows `<Device object at 0x10ad0c1f0>`. Define `__repr__` to return the constructor call that would rebuild the object. The `!r` in the f-string uses `repr()` on the value, so strings keep their quotes and numbers do not get any.
```python
def __repr__(self):
    return f"Device(hostname={self.hostname!r}, serial={self.serial!r})"

>>> d
Device(hostname='mbp-j-doe', serial='C02XG1234ABC')
```
Methods whose names start and end with two underscores are "dunders": Python calls them for you at the right moment.

--- code
Add a `__repr__` method to the class (indented four spaces) so that `repr(Device("C02X"))` is `Device(serial='C02X')`.
```python
class Device:
    def __init__(self, serial):
        self.serial = serial
```
check: repr(Device("C02X")) == "Device(serial='C02X')"
solution:     def __repr__(self):
solution:         return f"Device(serial={self.serial!r})"
> `!r` is what puts the quotes around the serial. Without it the output would be `Device(serial=C02X)`, which is not valid Python.

--- teach
### `__eq__`: what `==` means for your type
By default two objects are equal only when they are the same object. Override `__eq__` to say what equal means in your domain: same serial, same device. For anything that is not a Device, return `NotImplemented`; Python then tries the other side and finally answers `False` instead of crashing.
```python
def __eq__(self, other):
    if not isinstance(other, Device):
        return NotImplemented
    return self.serial == other.serial
```
`isinstance(x, Device)` asks whether `x` was built by `Device` (or a subclass of it).

--- quiz
`Device.__eq__` is called with `other = "C02XG1234ABC"`, a plain string. What should it return?
- [ ] `False`
- [x] `NotImplemented`
- [ ] `self.serial == other`
> `NotImplemented` lets Python try `other.__eq__` and then fall back to `False`. Returning `False` directly usually works but breaks symmetry with other types; comparing the serial to a string would make a device equal to a piece of text.

--- teach
### `__hash__`: earn your place in a set
Defining `__eq__` silently sets `__hash__` to `None`, so your objects can no longer be set members or dict keys. Add `__hash__` back, and hash on the same fields you compare, so equal objects always share a hash.
```python
def __hash__(self):
    return hash(self.serial)

>>> len({Device("a", "S1"), Device("b", "S1")})
1
```
Hash only on fields that never change. The rule is: equal objects must have equal hashes.

--- quiz
`__eq__` compares serials. Which `__hash__` keeps sets and dicts working correctly?
- [ ] `return hash(self.hostname)`
- [x] `return hash(self.serial)`
- [ ] `return id(self)`
> Equal objects must hash equal. Two devices with the same serial but different hostnames are equal, so hashing on hostname or identity would put "equal" objects in different buckets and a set would keep both.

--- exercise 8.1

--- recap
- `class` declares a type; `__init__` builds each object and stores attributes on `self`.
- Methods get `self` first; call them with a dot.
- `__repr__` returns the rebuilding constructor call; `!r` quotes strings.
- `__eq__` returns `NotImplemented` for foreign types.
- Defining `__eq__` requires `__hash__` on the same fields.
