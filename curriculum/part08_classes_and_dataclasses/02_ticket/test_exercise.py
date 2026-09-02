import unittest
from dataclasses import fields, is_dataclass
from datetime import datetime

from exercise import Ticket

T0 = datetime(2024, 5, 1, 9, 0)
T1 = datetime(2024, 5, 1, 9, 30)
T2 = datetime(2024, 5, 2, 8, 0)


class TestTicket(unittest.TestCase):
    def test_is_a_dataclass_with_fields_in_order(self):
        """Ticket is a dataclass whose fields are priority, created, title, assignee, tags"""
        self.assertTrue(is_dataclass(Ticket))
        self.assertEqual([f.name for f in fields(Ticket)], ["priority", "created", "title", "assignee", "tags"])

    def test_defaults(self):
        """assignee defaults to None and tags to an empty list"""
        t = Ticket(2, T0, "Wi-Fi drops")
        self.assertEqual((t.priority, t.created, t.title), (2, T0, "Wi-Fi drops"))
        self.assertIsNone(t.assignee)
        self.assertEqual(t.tags, [])

    def test_tags_are_not_shared(self):
        """Every ticket gets its own tags list"""
        a, b = Ticket(2, T0, "a"), Ticket(2, T0, "b")
        a.tags.append("network")
        self.assertEqual(b.tags, [])

    def test_equality_and_repr_are_generated(self):
        """Two tickets with the same field values are equal and repr shows the fields"""
        self.assertEqual(Ticket(2, T0, "a", "j.doe", ["x"]), Ticket(2, T0, "a", "j.doe", ["x"]))
        self.assertNotEqual(Ticket(2, T0, "a"), Ticket(3, T0, "a"))
        self.assertIn("priority=2", repr(Ticket(2, T0, "a")))

    def test_is_urgent(self):
        """is_urgent is True only for priority 1"""
        self.assertTrue(Ticket(1, T0, "a").is_urgent)
        self.assertFalse(Ticket(2, T0, "a").is_urgent)

    def test_sorts_by_priority_then_created(self):
        """sorted() orders by priority first, then oldest created first"""
        late_p1 = Ticket(1, T2, "late p1")
        early_p1 = Ticket(1, T0, "early p1")
        p3 = Ticket(3, T0, "p3")
        p2 = Ticket(2, T1, "p2")
        result = sorted([p3, late_p1, p2, early_p1])
        self.assertEqual([t.title for t in result], ["early p1", "late p1", "p2", "p3"])
        self.assertTrue(early_p1 < late_p1)
        self.assertTrue(p3 >= p2)

    def test_priority_validation(self):
        """priority outside 1..4 raises ValueError"""
        for bad in (0, 5, -1):
            with self.assertRaises(ValueError, msg=bad):
                Ticket(bad, T0, "x")
        Ticket(4, T0, "ok")  # boundary is allowed

    def test_from_dict(self):
        """from_dict parses the ISO timestamp and fills missing optional keys"""
        full = Ticket.from_dict({
            "priority": 1, "created": "2024-05-01T09:30:00", "title": "Laptop stolen",
            "assignee": "j.doe", "tags": ["security", "hardware"],
        })
        self.assertEqual(full, Ticket(1, T1, "Laptop stolen", "j.doe", ["security", "hardware"]))
        minimal = Ticket.from_dict({"priority": 2, "created": "2024-05-01T09:00:00", "title": "Wi-Fi drops"})
        self.assertEqual(minimal, Ticket(2, T0, "Wi-Fi drops"))
        src = {"priority": 3, "created": "2024-05-02T08:00:00", "title": "x", "tags": ["a"]}
        t = Ticket.from_dict(src)
        t.tags.append("b")
        self.assertEqual(src["tags"], ["a"])
        with self.assertRaises(ValueError):
            Ticket.from_dict({"priority": 9, "created": "2024-05-01T09:00:00", "title": "bad"})


if __name__ == "__main__":
    unittest.main()
