# Hashing a file in chunks

--- teach
### A hash turns bytes into a fixed-size fingerprint
`hashlib.sha256(data).hexdigest()` gives 64 hex characters that change completely if one byte of `data` changes. Vendors publish this digest next to a package so you can check the download. The input must be **bytes**, never `str`: encode text first.
```python
>>> import hashlib
>>> hashlib.sha256(b"hello world").hexdigest()
'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
>>> hashlib.sha256("hello world".encode("utf-8")).hexdigest() == _
True
```

--- quiz
What does `hashlib.sha256("hello")` do?
- [ ] Returns the digest of the text
- [x] Raises `TypeError` because the input is `str`, not bytes
- [ ] Returns `None`
> Hash functions work on bytes. `"hello".encode("utf-8")` or `b"hello"` is what you pass.

--- teach
### The hash object accumulates
Create an empty hash with `hashlib.sha256()` and feed it pieces with `.update()`. The final digest is the same as hashing everything at once. That is what makes it possible to hash a 4 GB installer without loading it into memory.
```python
>>> h = hashlib.sha256()
>>> h.update(b"hello ")
>>> h.update(b"world")
>>> h.hexdigest()
'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
```

--- code
Feed every chunk in `chunks` to `h`, then print the first 8 characters of the digest.
```python
import hashlib
h = hashlib.sha256()
chunks = [b"hello ", b"world"]
```
expect: b94d27b9
check: h.hexdigest() == hashlib.sha256(b"hello world").hexdigest()
solution: for chunk in chunks:
solution:     h.update(chunk)
solution: print(h.hexdigest()[:8])
> Each `update` adds bytes to the running hash. After both chunks the digest equals that of `b"hello world"`, which starts `b94d27b9`.

--- predict
What does this print?
```python
import hashlib
h = hashlib.sha256()
h.update(b"hello ")
h.update(b"world")
print(h.hexdigest() == hashlib.sha256(b"hello world").hexdigest())
```
answer: True
> Where the pieces are cut does not matter. The digest depends only on the bytes in order.

--- teach
### Read a file in chunks
Open with `"rb"` (read, binary) so reads return bytes. `f.read(n)` returns **at most** `n` bytes, and `b""` (empty bytes) once the file is exhausted. So: read a chunk, stop when it is empty, otherwise update the hash. Anything with a `.read(n)` method works, including `io.BytesIO` in tests.
```python
h = hashlib.sha256()
with open(path, "rb") as f:
    while True:
        chunk = f.read(65536)
        if not chunk:
            break
        h.update(chunk)
```
Never call `f.read()` with no argument: that reads the whole file at once.

--- code
Write the loop that reads `f` in pieces of `chunk_size` bytes until `read` returns `b""`, feeding each piece to `h`. Then print the first 8 characters of the digest.
```python
import hashlib, io
f = io.BytesIO(b"hello world")
h, chunk_size = hashlib.sha256(), 4
```
expect: b94d27b9
solution: while True:
solution:     chunk = f.read(chunk_size)
solution:     if not chunk:
solution:         break
solution:     h.update(chunk)
solution: print(h.hexdigest()[:8])
> Three reads of 4, 4 and 3 bytes, then an empty `b""` that ends the loop. `io.BytesIO` behaves like a file opened with `"rb"`, which is why tests use it.

--- fill
Complete the loop so it stops when the file is exhausted.
```python
while True:
    chunk = fileobj.read(chunk_size)
    if not chunk:
        ___
    h.update(chunk)
```
answer: break
> An empty `b""` is falsy, so `not chunk` is True at the end of the file and `break` leaves the loop.

--- teach
### Compare digests tolerantly
`hexdigest()` is already lowercase hex. What people paste is not: uppercase, trailing newline, sometimes a `sha256:` prefix. Normalise the **expected** value, then compare. `None` or an empty string can never match, so return `False` early.
```python
if not expected:
    return False
want = expected.strip().lower()
if want.startswith("sha256:"):
    want = want[len("sha256:"):]
return want == sha256_file(path)
```

--- predict
What does this print?
```python
want = "  SHA256:AbC1\n".strip().lower()
if want.startswith("sha256:"):
    want = want[len("sha256:"):]
print(want)
```
answer: abc1
> `strip` removes the spaces and newline, `lower` folds the case, and the slice drops the seven-character prefix.

--- teach
### Validate what is yours, let the rest raise
`chunk_size` is your rule, so check it first and raise `ValueError` for zero or negatives. A missing file is not your rule: `open` raises `FileNotFoundError` with a good message, so do not catch it.
```python
if not isinstance(chunk_size, int) or chunk_size <= 0:
    raise ValueError("chunk_size must be a positive int")
```

--- exercise 10.3

--- recap
- `hashlib.sha256(data).hexdigest()` hashes bytes; encode text first.
- `.update(chunk)` accumulates; the digest depends only on the bytes in order.
- Read files with `"rb"` and `f.read(n)` in a loop; `b""` means end of file.
- Normalise the expected digest (strip, lower, drop `sha256:`) before comparing.
