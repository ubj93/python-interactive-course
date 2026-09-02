import unittest

from exercise import Device, Inventory

A = Device("C02XG1234ABC", "mbp-j-doe")
B = Device("7GH2K3Q", "win-lab-01")
C = Device("FVFXC1234A", "mbp-a-lee")


class TestInventory(unittest.TestCase):
    def test_empty(self):
        """A new inventory has length 0 and get() returns the default"""
        inv = Inventory()
        self.assertEqual(len(inv), 0)
        self.assertIsNone(inv.get("C02XG1234ABC"))
        self.assertEqual(inv.get("C02XG1234ABC", "missing"), "missing")
        self.assertEqual(list(inv), [])

    def test_add_get_and_index(self):
        """add() stores by serial; get() and [] find it"""
        inv = Inventory()
        inv.add(A)
        inv.add(B)
        self.assertEqual(len(inv), 2)
        self.assertEqual(inv.get("7GH2K3Q"), B)
        self.assertEqual(inv["C02XG1234ABC"], A)

    def test_duplicate_serial_raises(self):
        """Adding a serial that exists raises ValueError and keeps the original"""
        inv = Inventory([A])
        with self.assertRaises(ValueError):
            inv.add(Device("C02XG1234ABC", "renamed"))
        self.assertEqual(inv["C02XG1234ABC"].hostname, "mbp-j-doe")
        self.assertEqual(len(inv), 1)

    def test_contains(self):
        """`in` accepts a serial string or a Device; other types are False"""
        inv = Inventory([A, B])
        self.assertIn("C02XG1234ABC", inv)
        self.assertIn(A, inv)
        self.assertIn(Device("7GH2K3Q", "different-hostname"), inv)
        self.assertNotIn("FVFXC1234A", inv)
        self.assertNotIn(C, inv)
        self.assertNotIn(42, inv)
        self.assertNotIn(None, inv)

    def test_iteration_order_and_reuse(self):
        """Iteration follows insertion order and works more than once"""
        inv = Inventory([B, A, C])
        self.assertEqual([d.serial for d in inv], ["7GH2K3Q", "C02XG1234ABC", "FVFXC1234A"])
        self.assertEqual([d.serial for d in inv], ["7GH2K3Q", "C02XG1234ABC", "FVFXC1234A"])
        self.assertEqual(sorted(d.hostname for d in inv), ["mbp-a-lee", "mbp-j-doe", "win-lab-01"])

    def test_remove(self):
        """remove() returns the device, shrinks the inventory and frees the serial"""
        inv = Inventory([A, B, C])
        self.assertEqual(inv.remove("7GH2K3Q"), B)
        self.assertEqual(len(inv), 2)
        self.assertNotIn("7GH2K3Q", inv)
        self.assertEqual([d.serial for d in inv], ["C02XG1234ABC", "FVFXC1234A"])
        inv.add(Device("7GH2K3Q", "reimaged"))
        self.assertEqual(inv["7GH2K3Q"].hostname, "reimaged")

    def test_missing_serial_raises_keyerror(self):
        """[] and remove() raise KeyError for an unknown serial"""
        inv = Inventory([A])
        with self.assertRaises(KeyError):
            inv["NOPE"]
        with self.assertRaises(KeyError):
            inv.remove("NOPE")
        self.assertEqual(len(inv), 1)

    def test_constructor_rejects_duplicates(self):
        """Duplicates in the constructor iterable raise, like add() would"""
        with self.assertRaises(ValueError):
            Inventory([A, Device("C02XG1234ABC", "twin")])
        inv = Inventory(iter([A, B]))
        self.assertEqual(len(inv), 2)


if __name__ == "__main__":
    unittest.main()
