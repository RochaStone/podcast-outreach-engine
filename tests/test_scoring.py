import json
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine import scoring as S  # noqa: E402

PROFILE = S.parse_profile((ROOT / "examples" / "guest-profile.md").read_text(encoding="utf-8"))
SHOWS = json.loads((ROOT / "tests" / "fixtures" / "shows.json").read_text(encoding="utf-8"))["shows"]
TODAY = date(2026, 10, 26)


def by_slug(slug):
    return next(s for s in SHOWS if s["slug"] == slug)


class ProfileTest(unittest.TestCase):
    def test_all_ten_sections_read(self):
        for k in S.SECTION_KEYS.values():
            self.assertTrue(PROFILE[k], k)

    def test_template_comment_is_ignored(self):
        p = S.parse_profile("<!-- note -->\n## 2. Who you help\nNew mums\n")
        self.assertEqual(p["help"], "New mums")


class FitTest(unittest.TestCase):
    def test_strong_fit(self):
        fit, terms = S.score_fit(PROFILE, by_slug("run-home-mama"))
        self.assertGreaterEqual(fit, 80)
        self.assertIn("new mums", terms)

    def test_no_fit(self):
        fit, _ = S.score_fit(PROFILE, by_slug("founders-who-lift"))
        self.assertLess(fit, 20)

    def test_phrase_skips_small_words(self):
        fit, terms = S.score_fit({"help": "mums who want a return to running"},
                                 {"title": "Return to run", "description": "", "recent_titles": []})
        self.assertIn("return running", terms)


class RecencyTest(unittest.TestCase):
    def test_ladder(self):
        self.assertEqual(S.score_recency("2026-10-22", TODAY), 100)
        self.assertEqual(S.score_recency("2026-10-14", TODAY), 85)
        self.assertEqual(S.score_recency("2026-09-29", TODAY), 70)
        self.assertEqual(S.score_recency("2026-09-01", TODAY), 50)
        self.assertEqual(S.score_recency("2026-08-01", TODAY), 30)
        self.assertEqual(S.score_recency("2026-05-02", TODAY), 0)
        self.assertEqual(S.score_recency(None, TODAY), 0)
        self.assertEqual(S.score_recency("garbage", TODAY), 0)

    def test_inactive_flag(self):
        s = S.score_show(by_slug("quiet-hours-sleep-club"), PROFILE, TODAY)
        self.assertFalse(s["active_90_days"])


class FormatTest(unittest.TestCase):
    def test_guest_scores(self):
        self.assertEqual(S.score_guests(0.6), 100)
        self.assertEqual(S.score_guests(0.3), 50)
        self.assertEqual(S.score_guests(0.0), 0)
        self.assertEqual(S.score_guests(None), 30)

    def test_solo_show_is_capped(self):
        s = S.score_show(by_slug("mum-miles"), PROFILE, TODAY)
        self.assertLessEqual(s["score"], S.SOLO_CAP)
        self.assertTrue(any("solo" in r for r in s["reasons"]))

    def test_size_and_cadence_bands(self):
        self.assertEqual(S.score_size(5), 20)
        self.assertEqual(S.score_size(100), 100)
        self.assertEqual(S.score_size(900), 60)
        self.assertEqual(S.score_cadence(7), 100)
        self.assertEqual(S.score_cadence(None), 30)


class RankingTest(unittest.TestCase):
    def setUp(self):
        self.ranked = S.score_all(SHOWS, PROFILE, TODAY)

    def test_weights_sum_to_one(self):
        self.assertAlmostEqual(sum(S.WEIGHTS.values()), 1.0)

    def test_love_list_on_top(self):
        self.assertEqual(self.ranked[0]["slug"], "run-home-mama")
        self.assertIn("On your love list.", self.ranked[0]["reasons"])

    def test_refused_topic_sinks(self):
        diet = next(s for s in self.ranked if s["slug"] == "diet-reset-daily")
        self.assertLessEqual(diet["score"], S.REFUSE_CAP)
        self.assertEqual(diet["band"], "Maybe later")
        self.assertIn("crash diets", diet["refuse_hits"])

    def test_every_show_has_reasons_and_bounded_score(self):
        for s in self.ranked:
            self.assertTrue(0 <= s["score"] <= 100)
            self.assertGreaterEqual(len(s["reasons"]), 2)

    def test_sorted_best_first(self):
        scores = [s["score"] for s in self.ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
