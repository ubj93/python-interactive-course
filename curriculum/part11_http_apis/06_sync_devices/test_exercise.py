import unittest

from exercise import sync_devices


class FakeClient:
    """Records every call instead of talking to an API."""

    def __init__(self):
        self.calls = []

    def create(self, record):
        self.calls.append(("create", record))
        return {"id": "new-" + record["serial"]}

    def update(self, remote_id, changes):
        self.calls.append(("update", remote_id, changes))

    def delete(self, remote_id):
        self.calls.append(("delete", remote_id))


def summary(created=(), updated=(), deleted=(), unchanged=()):
    return {"created": list(created), "updated": list(updated), "deleted": list(deleted), "unchanged": list(unchanged)}


class TestSyncDevices(unittest.TestCase):
    def test_identical_is_unchanged(self):
        """Matching records make no calls and are listed as unchanged"""
        client = FakeClient()
        local = [{"serial": "A1", "name": "mbp-a", "group": "eng"}]
        remote = [{"id": "1", "serial": "A1", "name": "mbp-a", "group": "eng", "last_seen": "2024-05-01"}]
        self.assertEqual(sync_devices(local, remote, client), summary(unchanged=["A1"]))
        self.assertEqual(client.calls, [])

    def test_create(self):
        """A local-only device is created with only serial and the fields"""
        client = FakeClient()
        local = [{"serial": "B2", "name": "mbp-b", "group": "eng", "notes": "ignore me"}]
        self.assertEqual(sync_devices(local, [], client), summary(created=["B2"]))
        self.assertEqual(client.calls, [("create", {"serial": "B2", "name": "mbp-b", "group": "eng"})])

    def test_update_only_changed_fields(self):
        """An update sends only the fields that differ"""
        client = FakeClient()
        local = [{"serial": "A1", "name": "mbp-a", "group": "sales"}]
        remote = [{"id": "17", "serial": "A1", "name": "mbp-a", "group": "eng"}]
        self.assertEqual(sync_devices(local, remote, client), summary(updated=["A1"]))
        self.assertEqual(client.calls, [("update", "17", {"group": "sales"})])

    def test_delete(self):
        """A remote-only device is deleted by its id"""
        client = FakeClient()
        remote = [{"id": "9", "serial": "Z9", "name": "old", "group": "eng"}]
        self.assertEqual(sync_devices([], remote, client), summary(deleted=["Z9"]))
        self.assertEqual(client.calls, [("delete", "9")])

    def test_mixed_ordering(self):
        """Creates, then updates, then deletes, each sorted by serial"""
        client = FakeClient()
        local = [
            {"serial": "C3", "name": "c", "group": "eng"},
            {"serial": "A1", "name": "a-new", "group": "eng"},
            {"serial": "B2", "name": "b", "group": "eng"},
            {"serial": "D4", "name": "d", "group": "eng"},
        ]
        remote = [
            {"id": "r-d", "serial": "D4", "name": "d", "group": "eng"},
            {"id": "r-a", "serial": "A1", "name": "a", "group": "eng"},
            {"id": "r-z", "serial": "Z9", "name": "z", "group": "eng"},
            {"id": "r-x", "serial": "X8", "name": "x", "group": "eng"},
        ]
        result = sync_devices(local, remote, client)
        self.assertEqual(result, summary(created=["B2", "C3"], updated=["A1"], deleted=["X8", "Z9"], unchanged=["D4"]))
        self.assertEqual(
            client.calls,
            [
                ("create", {"serial": "B2", "name": "b", "group": "eng"}),
                ("create", {"serial": "C3", "name": "c", "group": "eng"}),
                ("update", "r-a", {"name": "a-new"}),
                ("delete", "r-x"),
                ("delete", "r-z"),
            ],
        )

    def test_serial_normalisation_and_missing_fields(self):
        """Serials match after strip/upper; missing fields count as None"""
        client = FakeClient()
        local = [{"serial": " c02x ", "name": "mbp"}]
        remote = [{"id": "5", "serial": "C02X", "name": "mbp", "group": "eng"}]
        self.assertEqual(sync_devices(local, remote, client), summary(updated=["C02X"]))
        self.assertEqual(client.calls, [("update", "5", {"group": None})])
        client = FakeClient()
        self.assertEqual(sync_devices([{"serial": "n1"}], [], client), summary(created=["N1"]))
        self.assertEqual(client.calls, [("create", {"serial": "N1", "name": None, "group": None})])

    def test_dry_run_and_custom_fields(self):
        """dry_run reports the plan without calling; fields controls what is compared"""
        client = FakeClient()
        local = [{"serial": "A1", "name": "new", "group": "eng", "os": "14.5"}]
        remote = [{"id": "1", "serial": "A1", "name": "old", "group": "eng", "os": "14.5"}]
        self.assertEqual(sync_devices(local, remote, client, dry_run=True), summary(updated=["A1"]))
        self.assertEqual(client.calls, [])
        self.assertEqual(sync_devices(local, remote, client, fields=("os",)), summary(unchanged=["A1"]))
        self.assertEqual(client.calls, [])

    def test_invalid_input_before_any_call(self):
        """Blank or duplicate serials raise ValueError and nothing is sent"""
        client = FakeClient()
        good = {"serial": "A1", "name": "a", "group": "eng"}
        for local, remote in [
            ([good, {"serial": "", "name": "x", "group": "eng"}], []),
            ([good, {"name": "x", "group": "eng"}], []),
            ([good, {"serial": "a1", "name": "dup", "group": "eng"}], []),
            ([], [{"id": "1", **good}, {"id": "2", **good}]),
            ([{"serial": "NEW", "name": "n", "group": "g"}, good], [{"id": "1", **good}, {"id": "2", "serial": "A1 "}]),
        ]:
            with self.assertRaises(ValueError, msg=(local, remote)):
                sync_devices(local, remote, client)
        self.assertEqual(client.calls, [])


if __name__ == "__main__":
    unittest.main()
