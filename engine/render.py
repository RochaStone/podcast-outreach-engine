"""HTML pages for podcast-outreach-engine: the shortlist (Hotline) and the tracker (Call Log).

One render path. The page's data is built once (engine/common.py), then drawn by the motif skin the user
picked in style.json or with --motif: analog (paper you could hold), cyberpunk (the girly terminal) or
y2k-blog (the 2003 blog page). Colours and fonts come from style.json for every skin; palette.hero is the
ground colour. Every value from a feed is escaped and every link is checked to be http(s).
"""

from __future__ import annotations

from datetime import date

from . import skin_analog, skin_cyber, skin_y2k
from .common import default_style, fonts_url, root_css, shortlist_model, tracker_model  # noqa: F401 (re-exported)

MOTIFS = ("analog", "cyberpunk", "y2k-blog")
# Older motif names from the shared schema map to the nearest family.
ALIASES = {
    "guest-check": "analog", "front-page": "analog", "magazine-scrawl": "analog", "pink-paper": "analog",
    "rotary": "analog", "leopard": "analog", "neutral": "analog",
    "retro-tv": "cyberpunk", "terminal": "cyberpunk",
    "sticker-collage": "y2k-blog", "y2k": "y2k-blog", "blog": "y2k-blog",
}
SKINS = {"analog": skin_analog, "cyberpunk": skin_cyber, "y2k-blog": skin_y2k}


def resolve_motif(value: str | None) -> str:
    v = (value or "").strip().lower()
    if v in MOTIFS:
        return v
    return ALIASES.get(v, "analog")


def shortlist_html(scored: list[dict], meta: dict, style: dict | None = None, motif: str | None = None) -> str:
    style = style or default_style()
    skin = SKINS[resolve_motif(motif or style.get("motif"))]
    return skin.shortlist(shortlist_model(scored, meta, style), style)


def tracker_html(rows: list[dict], today: date, due_rows: list[dict], style: dict | None = None,
                 motif: str | None = None) -> str:
    style = style or default_style()
    skin = SKINS[resolve_motif(motif or style.get("motif"))]
    return skin.tracker(tracker_model(rows, today, due_rows, style), style)
