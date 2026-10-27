"""Shared pieces for every page skin: fonts, colour tokens, drawings, the pick script and the data models.

One data model per page (shortlist, call log) is built here from the scored shows or tracker rows. Each motif
skin (analog, cyberpunk, y2k-blog) only arranges that model, so every look shows the same facts.
Models hold raw strings. Skins escape every value with html.escape and only print links from safe_url.
"""

from __future__ import annotations

import json
import re
from datetime import date
from html import escape

from .feeds import safe_url
from .style import BUNDLED, invite_lines, load_style
from .tracker import OPEN_STATUSES

FONT_AXES = {
    "Fraunces": ":ital,opsz,wght@0,9..144,400..900;1,9..144,400..900",
    "Bricolage Grotesque": ":opsz,wght@12..96,400..800",
    "DM Mono": ":ital,wght@0,400;0,500;1,400",
    "Silkscreen": ":wght@400;700",
    "Pixelify Sans": ":wght@400..700",
}
FALLBACKS = {
    "masthead": "Georgia,serif", "label": "system-ui,-apple-system,'Segoe UI',sans-serif",
    "body": "Georgia,serif", "script": "cursive", "scrawl": "cursive", "mono": "ui-monospace,Menlo,monospace",
}
FONT_KEYS = ("masthead", "label", "body", "script", "scrawl", "mono")
PIXEL_FONTS = ("Silkscreen", "Pixelify Sans")  # chrome labels only, cyberpunk and y2k-blog


def fonts_url(style: dict, pixel: bool = False) -> str:
    fams = []
    for key in FONT_KEYS:
        f = (style.get("fonts") or {}).get(key)
        if f and f not in fams:
            fams.append(f)
    if pixel:
        fams.extend(f for f in PIXEL_FONTS if f not in fams)
    q = "&".join("family=" + f.replace(" ", "+") + FONT_AXES.get(f, "") for f in fams)
    return f"https://fonts.googleapis.com/css2?{q}&display=swap"


def _pal(style: dict) -> dict:
    p = dict(style.get("palette", {}))
    p.setdefault("wine", p.get("plum") or p.get("hero"))
    return p


def root_css(style: dict) -> str:
    p, f = _pal(style), style.get("fonts", {})

    def fam(k):
        return (f"'{f[k]}'," if f.get(k) else "") + FALLBACKS[k]
    return (f":root{{--ground:{p.get('hero')};--candy:{p.get('accent')};--cream:{p.get('paper')};"
            f"--blush:{p.get('paper_pink')};--ink:{p.get('ink')};--magenta:{p.get('marker')};--plum:{p.get('plum')};"
            f"--wine:{p.get('wine')};--gold:{p.get('gold')};--lilac:{p.get('cool')};"
            f"--display:{fam('masthead')};--label:{fam('label')};--body:{fam('body')};--script:{fam('script')};"
            f"--marker:{fam('scrawl')};--mono:{fam('mono')};--pixel:'Silkscreen','Pixelify Sans',{FALLBACKS['mono']}}}")


def default_style() -> dict:
    return load_style(explicit=str(BUNDLED))


def phone_svg(style: dict) -> str:
    """The rotary phone in ground, cream and gold. Colours are validated hex from style.json."""
    p = _pal(style)
    g, c, au, ink = p.get("hero"), p.get("paper"), p.get("gold"), p.get("ink")
    holes = "".join(f'<circle cx="{x}" cy="{y}" r="10.5"/>' for x, y in
                    ((200, 170), (236, 182), (252, 214), (244, 250), (216, 271), (182, 272), (154, 252), (146, 216), (162, 183)))
    return f"""<svg class="phone" viewBox="0 0 400 330" role="img" aria-label="A rotary phone">
<path d="M60 300 L95 150 Q100 132 120 132 L280 132 Q300 132 305 150 L340 300 Z" fill="{g}" stroke="{ink}" stroke-width="3"/>
<path d="M78 296 L108 160" stroke="{au}" stroke-width="1.5"/><path d="M322 296 L292 160" stroke="{au}" stroke-width="1.5"/>
<path d="M40 112 Q40 70 90 62 L310 62 Q360 70 360 112 L360 124 Q360 140 340 140 L300 140 Q284 140 282 124 L278 104
L122 104 L118 124 Q116 140 100 140 L60 140 Q40 140 40 124 Z" fill="{c}" stroke="{ink}" stroke-width="3"/>
<path d="M70 80 Q90 72 120 72" fill="none" stroke="{au}" stroke-width="1.5"/>
<circle cx="200" cy="222" r="70" fill="{c}" stroke="{au}" stroke-width="2"/>
<circle cx="200" cy="222" r="62" fill="none" stroke="{ink}" stroke-width="1" opacity=".35"/>
<g fill="{g}" stroke="{au}" stroke-width="1.5">{holes}</g>
<circle cx="200" cy="222" r="24" fill="{g}" stroke="{au}" stroke-width="1.5"/>
<circle cx="200" cy="222" r="5" fill="{au}"/>
<path d="M262 262 L282 282" stroke="{au}" stroke-width="5" stroke-linecap="round"/>
<path d="M330 140 C 390 170, 380 250, 340 300" fill="none" stroke="{au}" stroke-width="2.5" stroke-dasharray="2 8" stroke-linecap="round"/>
</svg>"""


def coupe_svg(style: dict) -> str:
    p = _pal(style)
    return (f'<svg viewBox="0 0 44 60" aria-hidden="true"><path d="M4 8 Q22 30 40 8 Z" fill="none" stroke="{p.get("wine")}" '
            f'stroke-width="2"/><path d="M8 11 Q22 25 36 11" fill="{p.get("gold")}" opacity=".45"/>'
            f'<path d="M22 22 L22 50 M12 54 L32 54" stroke="{p.get("wine")}" stroke-width="2" stroke-linecap="round"/>'
            f'<circle cx="31" cy="4" r="2" fill="{p.get("gold")}"/><circle cx="36" cy="11" r="1.4" fill="{p.get("gold")}"/></svg>')


def pixel_heart(color: str, size: int = 14, label: str = "") -> str:
    """A 7x6 pixel heart. Colour is validated hex from style.json."""
    rows = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for y, r in enumerate(rows)
                    for x, c in enumerate(r) if c == "1")
    aria = f'role="img" aria-label="{escape(label)}"' if label else 'aria-hidden="true"'
    return (f'<svg class="px" viewBox="0 0 7 6" width="{size}" height="{size * 6 // 7}" {aria} '
            f'shape-rendering="crispEdges" fill="{color}">{rects}</svg>')


def pixel_star(color: str, size: int = 12) -> str:
    rows = ["00100", "00100", "11111", "01110", "01010"]
    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for y, r in enumerate(rows)
                    for x, c in enumerate(r) if c == "1")
    return (f'<svg class="px" viewBox="0 0 5 5" width="{size}" height="{size}" aria-hidden="true" '
            f'shape-rendering="crispEdges" fill="{color}">{rects}</svg>')


GRAIN = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 0.2 0 0 0 0 0.05 0 0 0 0 0.15 0 0 0 .06 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)'/></svg>\")")

PICK_JS = """
<script>
(function(){
  var KEY = 'poe-picks:' + document.body.getAttribute('data-run');
  var boxes = Array.prototype.slice.call(document.querySelectorAll('.pick input'));
  var out = document.getElementById('picks-out');
  var store = null;
  try { store = window.localStorage; } catch (e) { store = null; out.setAttribute('data-storage', 'off'); }
  function load(){
    if (!store) return [];
    try { return JSON.parse(store.getItem(KEY) || '[]'); } catch (e) { return []; }
  }
  function save(list){
    if (!store) return;
    try { store.setItem(KEY, JSON.stringify(list)); } catch (e) { store = null; }
  }
  function text(){
    var picked = boxes.filter(function(b){ return b.checked; }).map(function(b){ return b.getAttribute('data-slug'); });
    save(picked);
    document.getElementById('picks-n').textContent = picked.length;
    out.textContent = picked.length ? 'Pitch these shows from my shortlist: ' + picked.join(', ') : 'Tick the shows you want, then copy.';
    return out.textContent;
  }
  var saved = load();
  boxes.forEach(function(b){ if (saved.indexOf(b.getAttribute('data-slug')) > -1) b.checked = true; b.addEventListener('change', text); });
  document.getElementById('copy').addEventListener('click', function(){
    var t = text();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(t).then(function(){ out.textContent = 'Copied. Paste it to Claude: ' + t; },
        function(){ out.textContent = 'Copy this to Claude: ' + t; });
    } else { out.textContent = 'Copy this to Claude: ' + t; }
  });
  text();
})();
</script>
"""



def band_class(score: int) -> str:
    return "hi" if score >= 75 else "mid" if score >= 55 else "lo"


def link(url: str, label: str, cls: str = "") -> str:
    u = safe_url(url)
    if not u:
        return ""
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="{escape(u)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a>'


def prompt_host(style: dict) -> str:
    """The terminal host name: the style's magazine word (ROCHEVERSE -> rocheverse) or its name, slugged."""
    word = (style.get("lines") or {}).get("magazine") or style.get("name") or "hotline"
    return re.sub(r"[^a-z0-9]+", "-", word.lower()).strip("-") or "hotline"


RESET_CSS = """
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.45}
a{color:var(--wine);text-underline-offset:3px;text-decoration-thickness:1px}
.px{display:inline-block;vertical-align:middle}
.empty{font-family:var(--display);font-size:24px}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
@media print{.bar{display:none}body{background:#fff!important}}
"""


def page(title: str, style: dict, css: str, body: str, pixel: bool, body_attrs: str = "") -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{escape(fonts_url(style, pixel))}">
<style>{root_css(style)}{RESET_CSS}{css}</style></head>
<body{body_attrs}>{body}</body></html>
"""


PARTS = [("fit", "Fit"), ("recency", "Fresh"), ("guests", "Guests"), ("size", "Size"), ("cadence", "Rhythm")]


def shortlist_model(scored: list[dict], meta: dict, style: dict) -> dict:
    lines = style.get("lines", {}) or {}
    today = meta.get("date") or date.today().isoformat()
    niche = meta.get("niche") or "your niche"
    cards = []
    for i, s in enumerate(scored, 1):
        score = int(s.get("score", 0))
        parts = s.get("parts", {}) or {}
        cards.append({
            "i": i, "slug": s.get("slug", ""), "title": s.get("title") or "Untitled", "author": s.get("author") or "",
            "score": score, "band": s.get("band", ""), "cls": band_class(score), "reasons": list(s.get("reasons", []))[:5],
            "parts": [(lab, int(parts.get(k, 0))) for k, lab in PARTS],
            "links": [(lab, u) for lab, u in (("Be a guest page", s.get("guest_link", "")), ("Show website", s.get("website", "")),
                                             ("Listen", s.get("apple_url", ""))) if safe_url(u)],
        })
    return {
        "date": today, "niche": niche, "n": len(cards), "ring": sum(1 for c in cards if c["score"] >= 75),
        "run_id": json.dumps([today, niche, len(cards)])[:120], "cards": cards,
        "masthead": lines.get("masthead") or "The podcast issue", "name": style.get("name") or "",
        "owner": style.get("owner") or "", "invite": invite_lines(style, meta.get("name")), "host": prompt_host(style),
    }


def tracker_model(rows: list[dict], today: date, due_rows: list[dict], style: dict) -> dict:
    lines = style.get("lines", {}) or {}
    due_names = {r["show"] for r in due_rows}
    counts = {k: sum(1 for r in rows if r["status"] == k) for k in ("pitched", "nudged", "replied", "booked", "aired")}
    out = [{"show": r["show"], "date_pitched": r.get("date_pitched") or "-", "status": r.get("status") or "pitched",
            "nudges": str(r.get("nudges", 0)), "next_nudge": r.get("next_nudge") or "-", "link": r.get("link", ""),
            "notes": r.get("notes", ""), "due": r["show"] in due_names} for r in rows]
    return {
        "date": today.isoformat(), "rows": out, "counts": counts, "due_n": len(due_rows),
        "open_n": sum(1 for r in rows if r["status"] in OPEN_STATUSES),
        "masthead": lines.get("masthead") or "The call log", "name": style.get("name") or "",
        "affirm": (lines.get("affirm") or "Every send is yours").capitalize(), "host": prompt_host(style),
    }
