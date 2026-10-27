import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine import tracker as T  # noqa: E402
from engine.render import MOTIFS, resolve_motif, shortlist_html, tracker_html  # noqa: E402
from engine.style import load_style  # noqa: E402

SHOW = {"slug": "run-home-mama", "title": "Run Home Mama", "author": "Host", "score": 88, "band": "Ring today",
        "reasons": ["They talk about new mums."], "parts": {"fit": 90, "recency": 100, "guests": 80, "size": 100, "cadence": 100},
        "website": "https://a.example.com", "guest_link": "", "apple_url": ""}
EVIL = dict(SHOW, slug="x", title="<script>alert(1)</script>", author="<img src=x onerror=alert(1)>",
            reasons=["<b>x</b>"], website="javascript:alert(1)")
META = {"date": "2026-10-26", "niche": "postnatal running"}

SHORT_MARKERS = {
    "analog": ["Call the girls!", 'aria-label="A rotary phone"', "Hotline"],
    "cyberpunk": ['rocheverse:~$</span> dial --niche "postnatal running"', 'class="key"', 'class="blocks"', "cursor"],
    "y2k-blog": ["hotline.exe", "you are visitor no.", "000,777", "currently pitching", 'class="px"'],
}
TRACK_MARKERS = {
    "analog": ["While you were out", "Call Log"],
    "cyberpunk": ["calllog --due", "[BOOKED]"],
    "y2k-blog": ["calllog.exe", "Guestbook", "signed 2026-10-01"],
}


def rows():
    r = []
    T.add(r, "Run Home Mama", date(2026, 10, 1), "https://a.example.com", "Recording soon")
    T.set_status(r, "Run Home Mama", "booked", date(2026, 10, 2))
    T.add(r, "Second Show", date(2026, 10, 1))
    return r


class MotifTest(unittest.TestCase):
    def test_each_motif_renders_its_signature(self):
        for m in MOTIFS:
            html = shortlist_html([SHOW], META, motif=m)
            self.assertIn(f'data-motif="{m}"', html)
            for marker in SHORT_MARKERS[m]:
                self.assertIn(marker, html, f"{m}: {marker}")
            self.assertIn('class="pick"', html)  # the pick script works in every skin
            self.assertIn('id="copy"', html)

    def test_each_motif_tracker(self):
        r = rows()
        due = T.due(r, date(2026, 10, 9))
        for m in MOTIFS:
            html = tracker_html(r, date(2026, 10, 9), due, motif=m)
            self.assertIn(f'data-motif="{m}"', html)
            for marker in TRACK_MARKERS[m]:
                self.assertIn(marker, html, f"{m}: {marker}")
            self.assertIn("Second Show", html)

    def test_same_facts_in_every_motif(self):
        for m in MOTIFS:
            html = shortlist_html([SHOW], META, motif=m)
            for fact in ("Run Home Mama", "88", "They talk about new mums.", "https://a.example.com"):
                self.assertIn(fact, html, f"{m}: {fact}")

    def test_escaping_in_every_motif(self):
        for m in MOTIFS:
            html = shortlist_html([EVIL], META, motif=m)
            self.assertNotIn("<script>alert(1)</script>", html, m)
            self.assertNotIn("<img src=x", html, m)
            self.assertNotIn("javascript:alert", html, m)

    def test_no_glow_anywhere(self):
        for m in MOTIFS:
            for html in (shortlist_html([SHOW], META, motif=m), tracker_html(rows(), date(2026, 10, 9), [], motif=m)):
                self.assertNotIn("text-shadow", html, m)
                self.assertNotIn("glow", html.lower(), m)
                self.assertNotIn("body{background:var(--lilac)", html, m)

    def test_pixel_font_only_where_needed(self):
        self.assertNotIn("family=Silkscreen", shortlist_html([SHOW], META, motif="analog"))
        self.assertIn("family=Silkscreen", shortlist_html([SHOW], META, motif="cyberpunk"))
        self.assertIn("family=Silkscreen", shortlist_html([SHOW], META, motif="y2k-blog"))

    def test_aliases_and_default(self):
        self.assertEqual(resolve_motif("guest-check"), "analog")
        self.assertEqual(resolve_motif("rotary"), "analog")
        self.assertEqual(resolve_motif("retro-tv"), "cyberpunk")
        self.assertEqual(resolve_motif("sticker-collage"), "y2k-blog")
        self.assertEqual(resolve_motif("Y2K-BLOG"), "y2k-blog")
        self.assertEqual(resolve_motif("anything"), "analog")
        self.assertEqual(resolve_motif(None), "analog")

    def test_style_motif_is_used_and_flag_overrides(self):
        style = load_style(str(ROOT / "examples" / "style.rocha-coded.json"))
        self.assertEqual(style["motif"], "analog")
        style["motif"] = "y2k-blog"
        self.assertIn('data-motif="y2k-blog"', shortlist_html([SHOW], META, style))
        self.assertIn('data-motif="cyberpunk"', shortlist_html([SHOW], META, style, motif="cyberpunk"))

    def test_terminal_host_follows_the_style(self):
        other = load_style(str(ROOT / "tests" / "fixtures" / "style.other.json"))
        html = shortlist_html([SHOW], META, other, motif="cyberpunk")
        self.assertIn("fictional-studio:~$", html)
        self.assertNotIn("rocheverse:~$", html)


if __name__ == "__main__":
    unittest.main()
