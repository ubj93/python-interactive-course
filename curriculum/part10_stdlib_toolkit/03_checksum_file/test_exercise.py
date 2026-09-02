import hashlib
import io
import os
import tempfile
import unittest

from exercise import sha256_file, sha256_stream, verify_checksum

EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
HELLO = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"


class SpyFile:
    """A binary file that records how big every read() request was."""

    def __init__(self, data: bytes):
        self.buf = io.BytesIO(data)
        self.sizes = []

    def read(self, n=-1):
        self.sizes.append(n)
        return self.buf.read(n)


class TestChecksum(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "pkg.dmg")
        self.data = bytes(range(256)) * 40  # 10240 bytes, not a multiple of odd chunk sizes
        with open(self.path, "wb") as f:
            f.write(self.data)

    def tearDown(self):
        self.tmp.cleanup()

    def test_known_digests(self):
        """Empty input and b'hello world' give the well-known digests"""
        self.assertEqual(sha256_stream(io.BytesIO(b"")), EMPTY)
        self.assertEqual(sha256_stream(io.BytesIO(b"hello world")), HELLO)

    def test_file_matches_hashlib(self):
        """sha256_file agrees with hashlib on the whole content"""
        self.assertEqual(sha256_file(self.path), hashlib.sha256(self.data).hexdigest())

    def test_reads_in_chunks(self):
        """Never asks read() for more than chunk_size bytes, and needs several reads"""
        spy = SpyFile(self.data)
        digest = sha256_stream(spy, chunk_size=1000)
        self.assertEqual(digest, hashlib.sha256(self.data).hexdigest())
        self.assertTrue(all(0 < n <= 1000 for n in spy.sizes), spy.sizes)
        self.assertGreaterEqual(len(spy.sizes), 11)

    def test_chunk_size_independent(self):
        """Any chunk size gives the same digest"""
        for size in (1, 7, 1024, 1 << 20):
            self.assertEqual(sha256_file(self.path, chunk_size=size), hashlib.sha256(self.data).hexdigest(), size)

    def test_verify_tolerant(self):
        """Uppercase, whitespace and a sha256: prefix are all accepted"""
        digest = hashlib.sha256(self.data).hexdigest()
        self.assertTrue(verify_checksum(self.path, digest))
        self.assertTrue(verify_checksum(self.path, "  " + digest.upper() + "\n"))
        self.assertTrue(verify_checksum(self.path, "sha256:" + digest))
        self.assertTrue(verify_checksum(self.path, "SHA256:" + digest.upper()))

    def test_verify_mismatch(self):
        """A different digest, empty string or None is False"""
        self.assertFalse(verify_checksum(self.path, HELLO))
        self.assertFalse(verify_checksum(self.path, ""))
        self.assertFalse(verify_checksum(self.path, None))

    def test_missing_file(self):
        """A missing file raises FileNotFoundError"""
        with self.assertRaises(FileNotFoundError):
            sha256_file(os.path.join(self.tmp.name, "nope.pkg"))

    def test_bad_chunk_size(self):
        """chunk_size of 0 or negative raises ValueError"""
        for bad in (0, -1):
            with self.assertRaises(ValueError, msg=bad):
                sha256_stream(io.BytesIO(b"x"), chunk_size=bad)
            with self.assertRaises(ValueError, msg=bad):
                sha256_file(self.path, chunk_size=bad)


if __name__ == "__main__":
    unittest.main()
