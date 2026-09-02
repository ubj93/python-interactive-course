"""Reference solutions for sha256_stream / sha256_file / verify_checksum."""
import hashlib
from functools import partial
from typing import BinaryIO, Optional


# Best practice: a hash object accumulates with .update(); feed it fixed-size reads until
# read() returns b"". Memory stays flat no matter how big the file is.
def sha256_stream(fileobj: BinaryIO, chunk_size: int = 65536) -> str:
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive int")
    h = hashlib.sha256()
    while True:
        chunk = fileobj.read(chunk_size)
        if not chunk:
            break
        h.update(chunk)
    return h.hexdigest()


def sha256_file(path: str, chunk_size: int = 65536) -> str:
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive int")
    with open(path, "rb") as f:
        return sha256_stream(f, chunk_size)


# Normalise the expected value, never the digest: hexdigest() is already lowercase.
def verify_checksum(path: str, expected: Optional[str]) -> bool:
    if not expected:
        return False
    want = expected.strip().lower()
    if want.startswith("sha256:"):
        want = want[len("sha256:"):]
    return want == sha256_file(path)


# Clever: two-argument iter() calls a function until it returns the sentinel. Pythonistas
# recognise iter(partial(f.read, n), b"") instantly; interviewers like seeing it named.
def sha256_stream_iter(fileobj: BinaryIO, chunk_size: int = 65536) -> str:
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive int")
    h = hashlib.sha256()
    for chunk in iter(partial(fileobj.read, chunk_size), b""):
        h.update(chunk)
    return h.hexdigest()
