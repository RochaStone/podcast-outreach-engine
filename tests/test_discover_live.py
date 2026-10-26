"""One live query against the Apple Podcasts search. Skipped when offline."""

import socket
import sys
import unittest
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import discover  # noqa: E402


def online() -> bool:
    try:
        socket.create_connection(("itunes.apple.com", 443), timeout=5).close()
        return True
    except OSError:
        return False


class OfflineHelpersTest(unittest.TestCase):
    def test_terms_combine_niche_and_audience(self):
        t = discover.terms_from("pilates, women's health", "new mums")
        self.assertEqual(t, ["pilates", "women's health", "new mums", "pilates new mums"])

    def test_merge_dedupes_by_feed(self):
        found = {}
        discover.merge(found, {"feed_url": "https://www.a.example.com/feed/", "title": "A", "sources": ["apple"],
                               "found_by": ["x"], "website": ""})
        discover.merge(found, {"feed_url": "http://a.example.com/feed", "title": "A", "sources": ["podcastindex"],
                               "found_by": ["y"], "website": "https://a.example.com"})
        self.assertEqual(len(found), 1)
        v = next(iter(found.values()))
        self.assertEqual(v["sources"], ["apple", "podcastindex"])
        self.assertEqual(v["website"], "https://a.example.com")

    def test_podcastindex_auth_header_shape(self):
        h = discover.podcastindex_headers("KEY", "SECRET")
        self.assertEqual(set(h), {"X-Auth-Key", "X-Auth-Date", "Authorization"})
        self.assertEqual(len(h["Authorization"]), 40)


@unittest.skipUnless(online(), "network unavailable")
class LiveAppleSearchTest(unittest.TestCase):
    def test_itunes_returns_podcasts_with_feeds(self):
        try:
            res = discover.search_itunes("running", "US", 5, timeout=20)
        except urllib.error.URLError as e:
            self.skipTest(f"network error: {e}")
        self.assertGreater(len(res), 0)
        for r in res:
            self.assertTrue(r["feed_url"].startswith("http"))
            self.assertTrue(r["title"])


if __name__ == "__main__":
    unittest.main()
