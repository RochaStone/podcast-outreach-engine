#!/usr/bin/env python3
"""Keep track of every pitch and who is due a nudge.

  python3 track.py add --show "The Show" --link https://... [--date 2026-10-26]
  python3 track.py set --show "The Show" --status replied      (pitched, nudged, replied, booked, aired, passed)
  python3 track.py due                                          lists who is due a follow-up today
  python3 track.py render                                       draws tracker/tracker.html

The tracker lives in tracker/tracker.md. Edit it by hand whenever you like.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import tracker as T  # noqa: E402
from engine.render import tracker_html  # noqa: E402
from engine.style import load_style  # noqa: E402


def _load(path: Path) -> list[dict]:
    return T.parse(path.read_text(encoding="utf-8")) if path.is_file() else []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Podcast pitch tracker.")
    ap.add_argument("command", choices=["add", "set", "due", "render"])
    ap.add_argument("--file", default="tracker/tracker.md")
    ap.add_argument("--out", default=None, help="HTML path for render (default next to the tracker file)")
    ap.add_argument("--show")
    ap.add_argument("--status")
    ap.add_argument("--link", default="")
    ap.add_argument("--notes", default=None)
    ap.add_argument("--date", default=None, help="YYYY-MM-DD, default today")
    ap.add_argument("--style", default=None, help="path to a style.json")
    ap.add_argument("--motif", default=None, help="analog, cyberpunk or y2k-blog (default: the motif in style.json)")
    ap.add_argument("--today", default=None, help="treat today as YYYY-MM-DD (for due and render)")
    a = ap.parse_args(argv)

    path = Path(a.file)
    day = date.fromisoformat(a.date) if a.date else date.today()
    today = date.fromisoformat(a.today) if a.today else date.today()
    rows = _load(path)

    try:
        if a.command == "add":
            if not a.show:
                ap.error("add needs --show")
            r = T.add(rows, a.show, day, a.link, a.notes or "")
            print(f"Added {r['show']}. First nudge {r['next_nudge']}.")
        elif a.command == "set":
            if not (a.show and a.status):
                ap.error("set needs --show and --status")
            r = T.set_status(rows, a.show, a.status, day, a.notes)
            print(f"{r['show']} is now {r['status']}. Next nudge: {r['next_nudge']}.")
        elif a.command == "due":
            d = T.due(rows, today)
            if not d:
                print("Nobody is due a nudge today.")
            for r in d:
                print(f"{r['show']}  |  pitched {r['date_pitched']}  |  nudges sent {r['nudges']} of 2  |  due {r['next_nudge']}")
            return 0
        elif a.command == "render":
            out = Path(a.out) if a.out else path.with_suffix(".html")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(tracker_html(rows, today, T.due(rows, today), load_style(a.style), a.motif), encoding="utf-8")
            print(f"Drew {out} with {len(rows)} pitches.")
            return 0
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(T.dump(rows), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
