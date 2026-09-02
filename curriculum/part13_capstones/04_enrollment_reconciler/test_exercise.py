import unittest

from exercise import active_users, decide, index_by_serial, reconcile

ACTIVE = {"alice@example.com", "bob@example.com"}


def inv(serial="A", owner="alice@example.com", status="in_use"):
    return {"serial": serial, "owner": owner, "status": status}


def mdm(serial="A", user="alice@example.com"):
    return {"serial": serial, "user": user}


class TestEnrollmentReconciler(unittest.TestCase):
    def test_index_by_serial(self):
        """index_by_serial normalises serials, keeps the first row, reports duplicates, skips blanks"""
        rows = [mdm(" c02abc "), mdm("C02ABC", "second"), mdm(""), {"serial": None}, {"user": "x"}, mdm("xyz")]
        by_serial, dups = index_by_serial(rows)
        self.assertEqual(sorted(by_serial), ["C02ABC", "XYZ"])
        self.assertEqual(by_serial["C02ABC"]["user"], "alice@example.com")
        self.assertEqual(dups, {"C02ABC"})
        self.assertEqual(index_by_serial([]), ({}, set()))

    def test_active_users(self):
        """active_users lowercases and strips, and drops inactive or nameless entries"""
        directory = [
            {"user": " Alice@Example.com", "active": True},
            {"user": "bob@example.com", "active": False},
            {"user": "carol@example.com", "active": 1},
            {"user": "", "active": True},
            {"active": True},
        ]
        self.assertEqual(active_users(directory), {"alice@example.com", "carol@example.com"})

    def test_decide_inventory_status_rules(self):
        """decide: retired, in stock and unknown statuses; absent-from-inventory"""
        self.assertEqual(decide(mdm(), inv(status="retired"), ACTIVE), ("retire", "retired in inventory"))
        self.assertIsNone(decide(None, inv(status="Retired "), ACTIVE))
        self.assertEqual(decide(mdm(), inv(status="in_stock"), ACTIVE), ("investigate", "in stock but enrolled"))
        self.assertIsNone(decide(None, inv(status="in_stock"), ACTIVE))
        self.assertEqual(decide(mdm(), inv(status="lost"), ACTIVE), ("investigate", "unknown inventory status 'lost'"))
        self.assertEqual(decide(mdm(), None, ACTIVE), ("investigate", "not in inventory"))

    def test_decide_enroll_reassign_ok(self):
        """decide: enroll when not in mdm, reassign on user mismatch, None when consistent"""
        self.assertEqual(decide(None, inv(), ACTIVE), ("enroll", "not enrolled"))
        self.assertEqual(decide(mdm(user="Bob@Example.com "), inv(), ACTIVE), ("reassign", "mdm user bob@example.com != owner alice@example.com"))
        self.assertEqual(decide(mdm(user=None), inv(), ACTIVE), ("reassign", "mdm user none != owner alice@example.com"))
        self.assertIsNone(decide(mdm(user="ALICE@example.com"), inv(owner=" alice@example.com"), ACTIVE))

    def test_decide_owner_and_duplicate_rules(self):
        """decide: duplicates beat everything; missing or inactive owners are investigated before enroll"""
        self.assertEqual(decide(mdm(), inv(status="retired"), ACTIVE, "mdm"), ("investigate", "duplicate rows in mdm"))
        self.assertEqual(decide(None, None, ACTIVE, "inventory"), ("investigate", "duplicate rows in inventory"))
        self.assertEqual(decide(None, inv(owner=""), ACTIVE), ("investigate", "no owner"))
        self.assertEqual(decide(None, inv(owner=None), ACTIVE), ("investigate", "no owner"))
        self.assertEqual(decide(None, inv(owner="Zed@example.com"), ACTIVE), ("investigate", "owner zed@example.com not active in directory"))
        self.assertEqual(decide(mdm(user="zed@example.com"), inv(owner="zed@example.com"), ACTIVE), ("investigate", "owner zed@example.com not active in directory"))

    def test_reconcile_end_to_end(self):
        """reconcile produces one record per actionable serial, sorted by action then serial"""
        directory = [{"user": "alice@example.com", "active": True}, {"user": "bob@example.com", "active": True}]
        mdm_rows = [mdm("A1", "alice@example.com"), mdm("B1", "alice@example.com"), mdm("R1", "bob@example.com"), mdm("X1", "")]
        inventory = [inv("A1"), inv("B1", "bob@example.com"), inv("R1", status="retired"), inv("E1", "bob@example.com"), inv("S1", status="in_stock")]
        self.assertEqual(
            reconcile(mdm_rows, directory, inventory),
            [
                {"serial": "E1", "action": "enroll", "reason": "not enrolled"},
                {"serial": "X1", "action": "investigate", "reason": "not in inventory"},
                {"serial": "B1", "action": "reassign", "reason": "mdm user alice@example.com != owner bob@example.com"},
                {"serial": "R1", "action": "retire", "reason": "retired in inventory"},
            ],
        )

    def test_reconcile_messy_sources(self):
        """reconcile survives casing, whitespace, missing serials and duplicate rows across sources"""
        directory = [{"user": "Alice@Example.com", "active": True}, {"user": "bob@example.com", "active": False}]
        mdm_rows = [
            mdm(" c02abc", "ALICE@example.com"),
            mdm("C02ABC ", "alice@example.com"),
            mdm("c02def", "alice@example.com"),
            {"serial": None, "user": "ghost@example.com"},
            mdm("c02ghi", None),
        ]
        inventory = [
            inv("C02ABC"),
            inv("c02def ", " Alice@example.com ", " In_Use"),
            inv("C02GHI", "bob@example.com"),
            inv("", "alice@example.com"),
            inv("C02JKL", "alice@example.com"),
            inv("c02jkl", "alice@example.com"),
        ]
        self.assertEqual(
            reconcile(mdm_rows, directory, inventory),
            [
                {"serial": "C02ABC", "action": "investigate", "reason": "duplicate rows in mdm"},
                {"serial": "C02GHI", "action": "investigate", "reason": "owner bob@example.com not active in directory"},
                {"serial": "C02JKL", "action": "investigate", "reason": "duplicate rows in inventory"},
            ],
        )

    def test_reconcile_empty_sources(self):
        """reconcile of empty or fully consistent sources returns []"""
        self.assertEqual(reconcile([], [], []), [])
        directory = [{"user": "alice@example.com", "active": True}]
        self.assertEqual(reconcile([mdm("A")], directory, [inv("A")]), [])


if __name__ == "__main__":
    unittest.main()
