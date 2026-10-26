#!/usr/bin/env python3
"""Score the shows against your guest profile and draw the shortlist.

  python3 score.py shows/shows.json --profile profile/guest-profile.md --out shortlist/

Writes shortlist/shortlist.json (every show, best first, with reasons) and
shortlist/shortlist.html (the top shows as rotary cards you can tick).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine.render import shortlist_html  # noqa: E402
from engine.style import load_style  # noqa: E402
from engine.scoring import parse_profile, score_all  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Score podcasts against your guest profile.")
    ap.add_argument("shows", help="path to shows.json from discover.py")
    ap.add_argument("--profile", required=True, help="path to guest-profile.md")
    ap.add_argument("--out", default="shortlist", help="output folder (default shortlist/)")
    ap.add_argument("--top", type=int, default=24, help="how many cards on the HTML page (default 24)")
    ap.add_argument("--min", type=int, default=0, help="hide cards below this score on the HTML page")
    ap.add_argument("--name", default=None, help="your name for the invitation card on the page")
    ap.add_argument("--style", default=None, help="path to a style.json (default ./style.json, then ~/.rocha-coded/style.json)")
    ap.add_argument("--today", default=None, help="score as if today were YYYY-MM-DD")
    a = ap.parse_args(argv)

    try:
        data = json.loads(Path(a.shows).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"Could not read {a.shows}: {e}", file=sys.stderr)
        return 1
    try:
        profile = parse_profile(Path(a.profile).read_text(encoding="utf-8"))
    except OSError as e:
        print(f"Could not read {a.profile}: {e}", file=sys.stderr)
        return 1
    if not any(profile.get(k) for k in ("help", "changes", "who")):
        print("The profile has no answers under 'Who you help' or 'What changes for them' yet.", file=sys.stderr)
        return 1

    today = date.fromisoformat(a.today) if a.today else date.today()
    shows = data.get("shows", data if isinstance(data, list) else [])
    scored = score_all(shows, profile, today)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    query = data.get("query", {}) if isinstance(data, dict) else {}
    (out / "shortlist.json").write_text(json.dumps({
        "scored_on": today.isoformat(), "query": query, "shows": scored,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    cards = [s for s in scored if s["score"] >= a.min][: a.top]
    style = load_style(a.style)
    html = shortlist_html(cards, {"date": today.isoformat(), "name": a.name, "niche": (query.get("niche") or "").split(",")[0].strip()}, style)
    (out / "shortlist.html").write_text(html, encoding="utf-8")

    print(f"Style: {style['_source']}")
    print(f"Scored {len(scored)} shows. Top {len(cards)} on {out / 'shortlist.html'}")
    for s in scored[:10]:
        print(f"  {s['score']:>3}  {s['title'][:56]}  ({s['band']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
