import unittest

from exercise import bytes_to_human


class TestBytesToHuman(unittest.TestCase):
    def test_bytes(self):
        """Values under 1024 stay in whole bytes"""
        self.assertEqual(bytes_to_human(0), "0 B")
        self.assertEqual(bytes_to_human(1), "1 B")
        self.assertEqual(bytes_to_human(1023), "1023 B")

    def test_kib(self):
        """1024 and 1536 bytes"""
        self.assertEqual(bytes_to_human(1024), "1.0 KiB")
        self.assertEqual(bytes_to_human(1536), "1.5 KiB")

    def test_larger_units(self):
        """MiB, GiB, TiB, PiB"""
        self.assertEqual(bytes_to_human(3 * 1024 ** 2), "3.0 MiB")
        self.assertEqual(bytes_to_human(5 * 1024 ** 3), "5.0 GiB")
        self.assertEqual(bytes_to_human(int(2.5 * 1024 ** 4)), "2.5 TiB")
        self.assertEqual(bytes_to_human(1024 ** 5), "1.0 PiB")

    def test_rounding(self):
        """One decimal place, rounded"""
        self.assertEqual(bytes_to_human(1024 + 100), "1.1 KiB")
        self.assertEqual(bytes_to_human(1024 ** 3 - 1), "1024.0 MiB")

    def test_beyond_pib_stays_pib(self):
        """Values past PiB keep using PiB"""
        self.assertEqual(bytes_to_human(2048 * 1024 ** 5), "2048.0 PiB")

    def test_negative_raises(self):
        """Negative counts raise ValueError"""
        with self.assertRaises(ValueError):
            bytes_to_human(-1)


if __name__ == "__main__":
    unittest.main()
