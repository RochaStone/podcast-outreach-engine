import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine import tracker as T  # noqa: E402
from engine.render import shortlist_html, tracker_html  # noqa: E402
from engine.style import BUNDLED, invite_lines, load_style  # noqa: E402

OTHER = ROOT / "tests" / "fixtures" / "style.other.json"
SHOW = {"slug": "a", "title": "A Show", "score": 80, "parts": {}, "reasons": ["r"], "band": "Ring today"}


class StyleLoadTest(unittest.TestCase):
    def test_fallback_order(self):
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as home:
            cwd, home = Path(cwd), Path(home)
            self.assertIn("bundled", load_style(cwd=cwd, home=home)["_source"])
            (home / ".rocha-coded").mkdir()
            (home / ".rocha-coded" / "style.json").write_text(json.dumps({"name": "Home"}))
            self.assertEqual(load_style(cwd=cwd, home=home)["name"], "Home")
            (cwd / "style.json").write_text(json.dumps({"name": "Here"}))
            self.assertEqual(load_style(cwd=cwd, home=home)["name"], "Here")
            self.assertEqual(load_style(str(OTHER), cwd=cwd, home=home)["name"], "Fictional Studio")

    def test_missing_keys_filled_and_bad_values_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "s.json"
            p.write_text(json.dumps({"palette": {"hero": "red;}body{display:none"}, "fonts": {"body": "x'</style>"}}))
            s = load_style(str(p))
            house = load_style(str(BUNDLED))
            self.assertEqual(s["palette"]["hero"], house["palette"]["hero"])
            self.assertEqual(s["fonts"]["body"], house["fonts"]["body"])
            self.assertNotIn("affirm", s.get("lines", {}))  # her words never leak into a user style

    def test_broken_json_falls_through(self):
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as home:
            (Path(cwd) / "style.json").write_text("{not json")
            self.assertIn("bundled", load_style(cwd=Path(cwd), home=Path(home))["_source"])

    def test_invite_lines(self):
        house = load_style(str(BUNDLED))
        self.assertEqual(invite_lines(house), ["YOU ARE INVITED TO THE ROCHEVERSE",
                                               "come build your founder world", "dress code: lore"])
        other = load_style(str(OTHER))
        self.assertEqual(invite_lines(other), ["YOU ARE INVITED TO MARA QUILL", "say it plainly", "dress code: tea"])
        self.assertEqual(invite_lines(other, "Juno")[0], "YOU ARE INVITED TO JUNO")


class InviteFormsTest(unittest.TestCase):
    def test_string_and_list_forms(self):
        s = {"lines": {"invite": "YOU ARE INVITED TO A / come in / dress code: b"}}
        self.assertEqual(invite_lines(s), ["YOU ARE INVITED TO A", "come in", "dress code: b"])
        s = {"lines": {"invite": ["YOU ARE INVITED TO A", "come in", "dress code: b"]}}
        self.assertEqual(invite_lines(s), ["YOU ARE INVITED TO A", "come in", "dress code: b"])
        self.assertEqual(invite_lines(s, "Juno")[0], "YOU ARE INVITED TO JUNO")

    def test_bundled_uses_string_form_and_empty_references(self):
        raw = json.loads(BUNDLED.read_text(encoding="utf-8"))
        self.assertIsInstance(raw["lines"]["invite"], str)
        self.assertEqual(raw["references"], [])


class SecondStyleRenderTest(unittest.TestCase):
    def test_shortlist_masthead_and_hero_colour_change(self):
        house = shortlist_html([SHOW], {"date": "2026-10-26"})
        other = shortlist_html([SHOW], {"date": "2026-10-26"}, load_style(str(OTHER)))
        self.assertIn("THE ROCHEVERSE TIMES", house)
        self.assertIn("--ground:#50163C", house)  # palette.hero is the ground
        for retired in ("Playfair", "Archivo", "Newsreader", "Courier", "#FF2D8A"):
            self.assertNotIn(retired, house)
        self.assertIn("THE QUILL QUARTERLY", other)
        self.assertNotIn("THE ROCHEVERSE TIMES", other)
        self.assertIn("--ground:#1F6F5C", other)
        self.assertNotIn("--ground:#50163C", other)
        self.assertIn("family=Fraunces", other)
        self.assertIn("YOU ARE INVITED TO MARA QUILL", other)

    def test_tracker_uses_style(self):
        rows = []
        T.add(rows, "A Show", date(2026, 10, 1))
        html = tracker_html(rows, date(2026, 10, 9), T.due(rows, date(2026, 10, 9)), load_style(str(OTHER)))
        self.assertIn("THE QUILL QUARTERLY", html)
        self.assertIn("One good call a day", html)
        self.assertIn("--ground:#1F6F5C", html)


if __name__ == "__main__":
    unittest.main()
