import unittest

from exercise import RecentEvents


def window(maxlen, kinds):
    w = RecentEvents(maxlen)
    for k in kinds:
        w.record(k)
    return w


class TestRecentEvents(unittest.TestCase):
    def test_record_and_len(self):
        """Recording grows the window up to maxlen and no further"""
        w = RecentEvents(3)
        self.assertEqual(len(w), 0)
        w.record("ok")
        w.record("ok")
        self.assertEqual(len(w), 2)
        for _ in range(5):
            w.record("timeout")
        self.assertEqual(len(w), 3)

    def test_counts_current_window(self):
        """counts() covers the events in the window"""
        w = window(5, ["ok", "timeout", "ok", "auth_failed"])
        self.assertEqual(w.counts(), {"ok": 2, "timeout": 1, "auth_failed": 1})

    def test_eviction_drops_oldest(self):
        """Once full, the oldest event leaves and its kind can vanish from counts"""
        w = window(3, ["ok", "timeout", "timeout", "timeout"])
        self.assertEqual(w.counts(), {"timeout": 3})
        w.record("ok")
        self.assertEqual(w.counts(), {"timeout": 2, "ok": 1})

    def test_most_common_order_and_limit(self):
        """most_common sorts by count desc then kind asc, and n limits the length"""
        w = window(10, ["timeout", "ok", "auth_failed", "ok", "timeout", "disk_full"])
        self.assertEqual(
            w.most_common(),
            [("ok", 2), ("timeout", 2), ("auth_failed", 1), ("disk_full", 1)],
        )
        self.assertEqual(w.most_common(1), [("ok", 2)])
        self.assertEqual(RecentEvents(4).most_common(), [])

    def test_ratio(self):
        """ratio is count / len, and 0.0 for an empty window or unknown kind"""
        w = window(4, ["ok", "timeout", "timeout", "ok"])
        self.assertAlmostEqual(w.ratio("timeout"), 0.5)
        self.assertEqual(w.ratio("disk_full"), 0.0)
        self.assertEqual(RecentEvents(4).ratio("ok"), 0.0)

    def test_alert_needs_full_window(self):
        """Alerts only when the window is full and the ratio meets the threshold"""
        w = window(4, ["timeout", "timeout", "timeout"])
        self.assertFalse(w.is_alerting("timeout", 0.5))
        w.record("ok")
        self.assertTrue(w.is_alerting("timeout", 0.75))
        self.assertFalse(w.is_alerting("timeout", 0.76))
        w.record("ok")
        w.record("ok")
        self.assertFalse(w.is_alerting("timeout", 0.75))

    def test_bad_maxlen(self):
        """maxlen of 0 or negative raises ValueError"""
        for bad in (0, -3):
            with self.assertRaises(ValueError, msg=bad):
                RecentEvents(bad)


if __name__ == "__main__":
    unittest.main()
