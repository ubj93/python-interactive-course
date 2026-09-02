import unittest
from datetime import date

from exercise import cumulative_targets, partition_devices, plan_rollout, skip_reason

RINGS = [("canary", [100]), ("early", [50, 100]), ("broad", [10, 40, 100])]
NAMES = ["canary", "early", "broad"]


def dev(serial, ring="broad", os_version="14.5", blockers=None):
    return {"serial": serial, "ring": ring, "os_version": os_version, "blockers": blockers or []}


class TestRolloutPlanner(unittest.TestCase):
    def test_skip_reason_order(self):
        """skip_reason: blockers first, then holds, then unknown ring, else None"""
        self.assertEqual(skip_reason(dev("A", blockers=["on_battery", "low_disk"]), NAMES, set()), "blocked: low_disk, on_battery")
        self.assertEqual(skip_reason(dev("A", os_version=" 14.4.1", blockers=["x"]), NAMES, {"14.4.1"}), "blocked: x")
        self.assertEqual(skip_reason(dev("A", os_version="14.4.1"), NAMES, {"14.4.1"}), "hold: 14.4.1")
        self.assertEqual(skip_reason(dev("A", ring="pilot"), NAMES, set()), "unknown ring: pilot")
        self.assertEqual(skip_reason({"serial": "A"}, NAMES, set()), "unknown ring: ")
        self.assertIsNone(skip_reason(dev("A", ring=" Broad "), NAMES, {"14.4.1"}))

    def test_cumulative_targets_rounding(self):
        """cumulative_targets rounds up with integer arithmetic"""
        self.assertEqual(cumulative_targets(7, [10, 40, 100]), [1, 3, 7])
        self.assertEqual(cumulative_targets(3, [10, 100]), [1, 3])
        self.assertEqual(cumulative_targets(0, [10, 100]), [0, 0])
        self.assertEqual(cumulative_targets(1, [100]), [1])
        self.assertEqual(cumulative_targets(200, [1, 33, 100]), [2, 66, 200])

    def test_cumulative_targets_validation(self):
        """cumulative_targets raises ValueError for empty, decreasing, or not-ending-at-100 percentages"""
        for bad in ([], [50, 25, 100], [10, 50], [100, 100, 90]):
            with self.assertRaises(ValueError, msg=str(bad)):
                cumulative_targets(10, bad)
        self.assertEqual(cumulative_targets(4, [50, 50, 100]), [2, 2, 4])

    def test_partition_devices(self):
        """partition_devices buckets eligible serials per ring (sorted) and lists skips sorted by serial"""
        devices = [
            dev("b2", "broad"), dev("B1", "Broad"), dev("c1", "canary", blockers=["low_disk"]),
            dev("E1", "early", os_version="14.4.1"), dev("z9", "nope"),
        ]
        by_ring, skipped = partition_devices(devices, NAMES, {"14.4.1"})
        self.assertEqual(by_ring, {"canary": [], "early": [], "broad": ["B1", "B2"]})
        self.assertEqual(skipped, [
            {"serial": "C1", "reason": "blocked: low_disk"},
            {"serial": "E1", "reason": "hold: 14.4.1"},
            {"serial": "Z9", "reason": "unknown ring: nope"},
        ])

    def test_partition_duplicates(self):
        """partition_devices keeps the first row for a serial and skips later ones as duplicate"""
        devices = [dev("A1", "canary"), dev(" a1 ", "broad"), dev("A1", "early", blockers=["x"])]
        by_ring, skipped = partition_devices(devices, NAMES, set())
        self.assertEqual(by_ring, {"canary": ["A1"], "early": [], "broad": []})
        self.assertEqual(skipped, [{"serial": "A1", "reason": "duplicate"}, {"serial": "A1", "reason": "duplicate"}])

    def test_plan_rollout_schedule(self):
        """plan_rollout numbers days across rings, dates them from start, and slices cumulatively"""
        devices = [dev("C1", "canary"), dev("C2", "canary")]
        devices += [dev(f"E{i}", "early") for i in range(1, 4)]
        devices += [dev(f"B{i}", "broad") for i in range(1, 8)]
        plan = plan_rollout(devices, RINGS, set(), date(2024, 6, 3))
        self.assertEqual(plan["skipped"], [])
        self.assertEqual(
            plan["days"],
            [
                {"day": 1, "date": "2024-06-03", "ring": "canary", "serials": ["C1", "C2"]},
                {"day": 2, "date": "2024-06-04", "ring": "early", "serials": ["E1", "E2"]},
                {"day": 3, "date": "2024-06-05", "ring": "early", "serials": ["E3"]},
                {"day": 4, "date": "2024-06-06", "ring": "broad", "serials": ["B1"]},
                {"day": 5, "date": "2024-06-07", "ring": "broad", "serials": ["B2", "B3"]},
                {"day": 6, "date": "2024-06-08", "ring": "broad", "serials": ["B4", "B5", "B6", "B7"]},
            ],
        )

    def test_plan_rollout_empty_days_and_month_rollover(self):
        """plan_rollout still emits days for empty rings and rolls dates across a month boundary"""
        plan = plan_rollout([dev("B1", "broad")], RINGS, set(), date(2024, 6, 29))
        self.assertEqual([(d["day"], d["date"], d["ring"], d["serials"]) for d in plan["days"]], [
            (1, "2024-06-29", "canary", []),
            (2, "2024-06-30", "early", []),
            (3, "2024-07-01", "early", []),
            (4, "2024-07-02", "broad", ["B1"]),
            (5, "2024-07-03", "broad", []),
            (6, "2024-07-04", "broad", []),
        ])
        self.assertEqual(plan_rollout([], [], set(), date(2024, 1, 1)), {"days": [], "skipped": []})

    def test_plan_rollout_messy_fleet(self):
        """plan_rollout end to end with holds, blockers, casing, whitespace and duplicates"""
        devices = [
            dev(" c02abc", "Canary"),
            dev("C02ABC", "canary"),
            dev("c02def", "EARLY ", os_version="14.4.1 "),
            dev("c02ghi", "early", blockers=["on_battery"]),
            dev("c02jkl", "early"),
            dev("c02mno", "broad"),
            dev("c02pqr", "broad"),
            dev("c02stu", "broad", os_version="14.4.1"),
            dev("c02vwx", "pilot"),
        ]
        plan = plan_rollout(devices, RINGS, {"14.4.1"}, date(2024, 6, 3))
        self.assertEqual([d["serials"] for d in plan["days"]], [["C02ABC"], ["C02JKL"], [], ["C02MNO"], [], ["C02PQR"]])
        self.assertEqual(plan["skipped"], [
            {"serial": "C02ABC", "reason": "duplicate"},
            {"serial": "C02DEF", "reason": "hold: 14.4.1"},
            {"serial": "C02GHI", "reason": "blocked: on_battery"},
            {"serial": "C02STU", "reason": "hold: 14.4.1"},
            {"serial": "C02VWX", "reason": "unknown ring: pilot"},
        ])


if __name__ == "__main__":
    unittest.main()
