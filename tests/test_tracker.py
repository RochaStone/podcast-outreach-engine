import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine import tracker as T  # noqa: E402
from engine.render import shortlist_html, tracker_html  # noqa: E402


class DueDateTest(unittest.TestCase):
    def test_first_nudge_after_seven_days(self):
        rows = []
        r = T.add(rows, "Show A", date(2026, 10, 1))
        self.assertEqual(r["next_nudge"], "2026-10-08")
        self.assertEqual(T.due(rows, date(2026, 10, 7)), [])
        self.assertEqual([x["show"] for x in T.due(rows, date(2026, 10, 8))], ["Show A"])

    def test_second_nudge_after_ten_more_days_then_stop(self):
        rows = []
        T.add(rows, "Show A", date(2026, 10, 1))
        r = T.set_status(rows, "Show A", "nudged", date(2026, 10, 8))
        self.assertEqual((r["nudges"], r["next_nudge"]), (1, "2026-10-18"))
        r = T.set_status(rows, "Show A", "nudged", date(2026, 10, 18))
        self.assertEqual((r["nudges"], r["next_nudge"]), (2, "-"))
        self.assertEqual(T.due(rows, date(2027, 1, 1)), [])

    def test_closed_statuses_never_due(self):
        for st in ("replied", "booked", "aired", "passed"):
            rows = []
            T.add(rows, "Show A", date(2026, 10, 1))
            T.set_status(rows, "Show A", st, date(2026, 10, 2))
            self.assertEqual(T.due(rows, date(2026, 12, 1)), [], st)

    def test_round_trip_markdown_and_hand_edits(self):
        rows = []
        T.add(rows, "Show | Pipes", date(2026, 10, 1), "https://x.example.com", "note")
        md = T.dump(rows)
        back = T.parse(md)
        self.assertEqual(back[0]["show"], "Show / Pipes")
        self.assertEqual(back[0]["next_nudge"], "2026-10-08")
        hand = md.replace("2026-10-08", "2026-10-03")
        self.assertEqual(len(T.due(T.parse(hand), date(2026, 10, 3))), 1)

    def test_errors(self):
        rows = []
        T.add(rows, "Show A", date(2026, 10, 1))
        with self.assertRaises(ValueError):
            T.add(rows, "show a", date(2026, 10, 1))
        with self.assertRaises(ValueError):
            T.set_status(rows, "Show A", "ghosted", date(2026, 10, 1))
        with self.assertRaises(ValueError):
            T.set_status(rows, "Nope", "booked", date(2026, 10, 1))


class RenderSafetyTest(unittest.TestCase):
    def test_feed_text_is_escaped_and_bad_links_dropped(self):
        evil = {"slug": "x", "title": "<script>alert(1)</script>", "author": "<img src=x onerror=alert(1)>",
                "score": 50, "parts": {}, "reasons": ["<b>hi</b>"], "band": "Worth a ring",
                "website": "javascript:alert(1)", "guest_link": "", "apple_url": ""}
        html = shortlist_html([evil], {"date": "2026-10-26", "niche": "<i>x</i>"})
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertNotIn("<img src=x", html)
        self.assertNotIn("javascript:alert", html)
        self.assertIn("&lt;script&gt;", html)

    def test_invitation_card_house_line_and_user_name(self):
        house = shortlist_html([], {"date": "2026-10-26"})
        self.assertIn("YOU ARE INVITED TO THE ROCHEVERSE", house)
        self.assertIn("come build your founder world", house)
        self.assertIn("dress code: lore", house)
        named = shortlist_html([], {"date": "2026-10-26", "name": "Juno <b>Ashby</b>"})
        self.assertIn("YOU ARE INVITED TO JUNO &lt;B&gt;ASHBY&lt;/B&gt;", named)
        self.assertNotIn("YOU ARE INVITED TO THE ROCHEVERSE", named)

    def test_tracker_html_marks_due(self):
        rows = []
        T.add(rows, "Show A", date(2026, 10, 1))
        html = tracker_html(rows, date(2026, 10, 9), T.due(rows, date(2026, 10, 9)))
        self.assertIn("Nudge due!", html)


if __name__ == "__main__":
    unittest.main()
