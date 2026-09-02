import unittest

from exercise import PaginationError, fetch_all_pages

BASE = "https://mdm.example.com/v1/devices"


def make_get(pages):
    """Fake HTTP GET: serves canned bodies by exact URL and records every call."""
    calls = []

    def get(url):
        calls.append(url)
        return pages[url]

    get.calls = calls
    return get


class TestFetchAllPages(unittest.TestCase):
    def test_single_page(self):
        """One page with no cursor is fetched once"""
        get = make_get({BASE: {"items": ["a", "b"], "next_cursor": None}})
        self.assertEqual(fetch_all_pages(get, BASE), ["a", "b"])
        self.assertEqual(get.calls, [BASE])

    def test_follows_cursor_in_order(self):
        """Pages are concatenated in order and the cursor is added as a query param"""
        get = make_get({
            BASE: {"items": [1, 2], "next_cursor": "c2"},
            BASE + "?cursor=c2": {"items": [3, 4], "next_cursor": "c3"},
            BASE + "?cursor=c3": {"items": [5], "next_cursor": None},
        })
        self.assertEqual(fetch_all_pages(get, BASE), [1, 2, 3, 4, 5])
        self.assertEqual(get.calls, [BASE, BASE + "?cursor=c2", BASE + "?cursor=c3"])

    def test_missing_cursor_key_and_missing_items(self):
        """A missing next_cursor ends the walk; a page without items adds nothing"""
        get = make_get({
            BASE: {"next_cursor": "c2"},
            BASE + "?cursor=c2": {"items": ["z"]},
        })
        self.assertEqual(fetch_all_pages(get, BASE), ["z"])
        self.assertEqual(len(get.calls), 2)

    def test_keeps_existing_params(self):
        """Existing query params survive and the cursor is appended last"""
        start = BASE + "?limit=2&status=active"
        get = make_get({
            start: {"items": [1], "next_cursor": "c2"},
            start + "&cursor=c2": {"items": [2], "next_cursor": ""},
        })
        self.assertEqual(fetch_all_pages(get, start), [1, 2])
        self.assertEqual(get.calls[1], start + "&cursor=c2")

    def test_replaces_stale_cursor(self):
        """A cursor already in the original URL is replaced, not duplicated"""
        start = BASE + "?cursor=old&limit=2"
        get = make_get({
            start: {"items": [1], "next_cursor": "new"},
            BASE + "?limit=2&cursor=new": {"items": [2], "next_cursor": None},
        })
        self.assertEqual(fetch_all_pages(get, start), [1, 2])

    def test_loop_detected(self):
        """A cursor seen before raises PaginationError instead of looping forever"""
        get = make_get({
            BASE: {"items": [1], "next_cursor": "c2"},
            BASE + "?cursor=c2": {"items": [2], "next_cursor": "c2"},
        })
        with self.assertRaises(PaginationError):
            fetch_all_pages(get, BASE)
        self.assertLessEqual(len(get.calls), 3)

    def test_max_pages(self):
        """Needing more than max_pages requests raises PaginationError"""
        get = make_get({
            BASE: {"items": [1], "next_cursor": "c2"},
            BASE + "?cursor=c2": {"items": [2], "next_cursor": "c3"},
            BASE + "?cursor=c3": {"items": [3], "next_cursor": None},
        })
        with self.assertRaises(PaginationError):
            fetch_all_pages(get, BASE, max_pages=2)
        self.assertEqual(fetch_all_pages(make_get({
            BASE: {"items": [1], "next_cursor": "c2"},
            BASE + "?cursor=c2": {"items": [2], "next_cursor": None},
        }), BASE, max_pages=2), [1, 2])


if __name__ == "__main__":
    unittest.main()
