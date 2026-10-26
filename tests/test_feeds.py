import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine import feeds  # noqa: E402

FIXTURE = (ROOT / "tests" / "fixtures" / "feed.xml").read_text(encoding="utf-8")


class ParseFeedTest(unittest.TestCase):
    def setUp(self):
        self.f = feeds.parse_feed(FIXTURE)

    def test_basic_facts(self):
        self.assertEqual(self.f["title"], "Run Home Mama")
        self.assertEqual(self.f["episode_count"], 5)
        self.assertEqual(self.f["last_episode_date"], "2026-10-22")
        self.assertEqual(self.f["cadence_days"], 7.0)
        self.assertEqual(self.f["language"], "en-gb")
        self.assertEqual(self.f["author"], "Fictional Host One")

    def test_public_website_and_guest_page(self):
        self.assertEqual(self.f["website"], "https://runhomemama.example.com/")
        self.assertEqual(self.f["guest_link"], "https://runhomemama.example.com/be-a-guest")

    def test_never_keeps_email_addresses(self):
        blob = repr(self.f)
        self.assertNotIn("@runhomemama", blob)
        self.assertNotIn("owner@", blob)
        self.assertIn("[email removed]", self.f["description"])

    def test_guest_ratio_from_titles(self):
        # with Ama Lewis, Hana Price on, ft. Bea Morton = 3 of 5
        self.assertEqual(self.f["guest_ratio"], 0.6)

    def test_broken_xml_falls_back_to_regex(self):
        broken = FIXTURE.replace("</channel>", "").replace("<itunes:owner>", "<itunes:owner")
        f = feeds.parse_feed(broken)
        self.assertEqual(f["title"], "Run Home Mama")
        self.assertEqual(f["episode_count"], 5)
        self.assertEqual(f["last_episode_date"], "2026-10-22")


class HelperTest(unittest.TestCase):
    def test_guest_title_heuristic(self):
        yes = ["Pricing with Jane Doe", "Industry myths With Courtney Miller", "Ep 4: Ana Ruiz on rest",
               "Interview: a founder", "Feat. Dani Rowe: strong mums", "Joined by a physio", "Big talk | Mia Stone"]
        no = ["Listener questions", "Babyloss", "Episode 212; Rainy long runs and lost trainers",
              "How to Stop Letting Fear Rule Your Life"]
        for t in yes:
            self.assertTrue(feeds.looks_like_guest_episode(t), t)
        for t in no:
            self.assertFalse(feeds.looks_like_guest_episode(t), t)

    def test_guest_ratio_empty(self):
        self.assertIsNone(feeds.guest_ratio([]))

    def test_cadence(self):
        d = [datetime(2026, 10, day, tzinfo=timezone.utc) for day in (1, 8, 15, 22)]
        self.assertEqual(feeds.cadence_days(d), 7.0)
        self.assertIsNone(feeds.cadence_days(d[:1]))

    def test_normalize_feed_url_dedupes(self):
        a = feeds.normalize_feed_url("https://www.Feeds.example.com/show/")
        b = feeds.normalize_feed_url("http://feeds.example.com/show")
        self.assertEqual(a, b)

    def test_safe_url_blocks_scripts(self):
        self.assertEqual(feeds.safe_url("javascript:alert(1)"), "")
        self.assertEqual(feeds.safe_url("mailto:a@b.co"), "")
        self.assertEqual(feeds.safe_url("https://ok.example.com/x"), "https://ok.example.com/x")

    def test_slugify(self):
        self.assertEqual(feeds.slugify("The Strong After Baby Show!"), "the-strong-after-baby-show")
        self.assertEqual(feeds.slugify("???"), "show")

    def test_parse_date_formats(self):
        self.assertEqual(feeds.parse_date("Thu, 22 Oct 2026 06:00:00 +0000").date().isoformat(), "2026-10-22")
        self.assertEqual(feeds.parse_date("2026-10-22T06:00:00Z").date().isoformat(), "2026-10-22")
        self.assertIsNone(feeds.parse_date("not a date"))


if __name__ == "__main__":
    unittest.main()
