"""Verify a package download with SHA-256.

Munki and Jamf both publish a checksum next to every package, and we compare it
before installing anything. Installers can be several gigabytes, so never read a
whole file into memory. Write three functions.

`sha256_stream(fileobj, chunk_size=65536)` reads a binary file-like object in
pieces of at most `chunk_size` bytes, calling `fileobj.read(chunk_size)` until it
returns b"", and returns the lowercase hex digest.

`sha256_file(path, chunk_size=65536)` opens `path` in binary mode and returns its
digest via sha256_stream. A missing file raises FileNotFoundError (let `open` do
that; do not catch it).

`verify_checksum(path, expected)` returns True when the file's digest matches
`expected`. The comparison is case-insensitive and ignores surrounding
whitespace, and an optional "sha256:" prefix on `expected` is accepted. Anything
else, including None or an empty string, is False.

Rules:
- chunk_size must be a positive int; raise ValueError otherwise (both functions)
- never call read() with no argument or with a number larger than chunk_size
- the digest of empty input is
  "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

Examples:
    >>> import io
    >>> sha256_stream(io.BytesIO(b"hello world"))
    'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
    >>> verify_checksum("pkg.dmg", "SHA256:B94D27B9...")   # doctest: +SKIP
    True
"""
import hashlib
from typing import BinaryIO, Optional


def sha256_stream(fileobj: BinaryIO, chunk_size: int = 65536) -> str:
    raise NotImplementedError("write sha256_stream")


def sha256_file(path: str, chunk_size: int = 65536) -> str:
    raise NotImplementedError("write sha256_file")


def verify_checksum(path: str, expected: Optional[str]) -> bool:
    raise NotImplementedError("write verify_checksum")
