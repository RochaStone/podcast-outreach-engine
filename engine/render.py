"""HTML pages for podcast-outreach-engine: the shortlist (Hotline) and the tracker (Call Log).

The current Rocheverse look: a plum masthead band on cream paper, Fraunces display, Bricolage Grotesque
labels, DM Mono numbers, one Pinyon Script line, candy pink as the single accent, gold hairlines.
Every colour and font comes from style.json (palette.hero is the GROUND colour). Every value from a feed
is escaped and every link is checked to be http(s). Pages open from disk in any browser; fonts load from
Google Fonts when online and fall back to system fonts offline.
"""

from __future__ import annotations

import json
from datetime import date
from html import escape

from .feeds import safe_url
from .style import BUNDLED, invite_lines, load_style
from .tracker import OPEN_STATUSES

# Known Google Fonts axes. Any other family is requested plain (weight 400), which never errors.
FONT_AXES = {
    "Fraunces": ":ital,opsz,wght@0,9..144,400..900;1,9..144,400..900",
    "Bricolage Grotesque": ":opsz,wght@12..96,400..800",
    "DM Mono": ":ital,wght@0,400;0,500;1,400",
}
FALLBACKS = {
    "masthead": "Georgia,serif", "label": "system-ui,-apple-system,'Segoe UI',sans-serif",
    "body": "Georgia,serif", "script": "cursive", "scrawl": "cursive", "mono": "ui-monospace,Menlo,monospace",
}
FONT_KEYS = ("masthead", "label", "body", "script", "scrawl", "mono")


def fonts_url(style: dict) -> str:
    fams = []
    for key in FONT_KEYS:
        f = (style.get("fonts") or {}).get(key)
        if f and f not in fams:
            fams.append(f)
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
            f"--marker:{fam('scrawl')};--mono:{fam('mono')}}}")


def _default_style() -> dict:
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


GRAIN = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 0.2 0 0 0 0 0.05 0 0 0 0 0.15 0 0 0 .06 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)'/></svg>\")")

BASE_CSS = """
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--cream);background-image:GRAIN;color:var(--ink);font-family:var(--body);
font-size:17px;line-height:1.45}
a{color:var(--wine);text-underline-offset:3px;text-decoration-thickness:1px}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px 120px}
.lab{font-family:var(--label);font-weight:800;font-size:12px;letter-spacing:.14em;text-transform:uppercase}
.band{background:var(--ground);color:var(--cream);margin:0 -16px;padding:22px 32px 40px;position:relative}
.band::after{content:"";position:absolute;left:32px;right:32px;bottom:14px;border-top:1px solid var(--gold)}
.band .top{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;opacity:.85}
.band .top .date{font-family:var(--mono);font-weight:400;letter-spacing:.04em;text-transform:none}
.band h1{font-family:var(--display);font-weight:900;color:var(--cream);margin:8px 0 0;line-height:.95;
font-size:clamp(64px,14vw,176px);letter-spacing:-.025em}
.cover-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:24px;align-items:center;padding:30px 0 26px;
border-bottom:1px solid var(--gold);margin-bottom:30px}
.cover{display:flex;flex-direction:column;gap:12px}.cover p{margin:0}
.script{font-family:var(--script);color:var(--magenta);font-size:clamp(44px,6.5vw,76px);line-height:1;margin:0 0 6px;
font-weight:400}
.line{font-family:var(--display);font-size:clamp(20px,2.5vw,28px);font-weight:600;line-height:1.12;max-width:22ch}
.line em{color:var(--wine);font-style:italic;font-weight:600}
.side{display:flex;flex-direction:column;align-items:center;gap:20px}
.phone{width:100%;max-width:330px;filter:drop-shadow(0 14px 18px rgba(59,18,48,.22))}
.invite{position:relative;background:var(--cream);color:var(--wine);border:1px solid var(--gold);outline:1px solid var(--wine);
outline-offset:4px;padding:16px 22px 16px 70px;transform:rotate(1.5deg);box-shadow:0 12px 24px rgba(59,18,48,.18);
max-width:380px;text-align:left;margin:6px}
.invite svg{position:absolute;left:16px;top:50%;transform:translateY(-50%);width:40px}
.invite .t1{font-family:var(--display);font-weight:800;font-size:16px;letter-spacing:.06em;line-height:1.2;margin:0}
.invite .t2{font-family:var(--display);font-style:italic;font-size:17px;margin:4px 0 0}
.invite .t3{font-family:var(--mono);font-size:13px;letter-spacing:.06em;margin:6px 0 0}
.pill{display:inline-block;border-radius:999px;padding:4px 12px;font-family:var(--label);font-weight:800;font-size:11px;
letter-spacing:.12em;text-transform:uppercase;color:var(--ink)}
.foot{margin-top:52px;border-top:1px solid var(--gold);padding-top:14px;display:flex;justify-content:space-between;
gap:12px;flex-wrap:wrap;align-items:baseline}
.yours{font-family:var(--display);font-style:italic;color:var(--wine);font-size:20px}
.empty{font-family:var(--display);font-size:26px}
@media (max-width:760px){.cover-grid{grid-template-columns:1fr}.phone{max-width:230px}.band{padding:18px 16px 24px}
.band::after{left:16px;right:16px}}
""".replace("GRAIN", GRAIN)

SHORTLIST_CSS = """
.how{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 30px;align-items:center}
.how span{border:1px solid var(--gold);border-radius:999px;padding:4px 12px;font-family:var(--label);font-weight:800;
font-size:11px;letter-spacing:.12em;text-transform:uppercase}
.how b{font-family:var(--mono);font-weight:500;letter-spacing:0}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:40px 26px}
.card{position:relative;background:var(--cream);border:1.5px solid var(--ink);border-radius:16px 16px 12px 12px;
padding:24px 20px 46px;box-shadow:0 14px 28px rgba(59,18,48,.16),0 2px 0 rgba(59,18,48,.25);display:flex;
flex-direction:column;gap:11px}
.card::before,.card::after{content:"";position:absolute;bottom:-2px;width:34px;height:19px;background:var(--cream);
border:1.5px solid var(--ink);border-bottom:none;border-radius:16px 16px 0 0}
.card::before{left:calc(50% - 64px)}.card::after{left:calc(50% + 30px)}
.rank,.tab{position:absolute;top:-17px;border-radius:9px 9px 0 0;padding:2px 12px 2px;font-family:var(--mono);
font-weight:500;font-size:14px}
.rank{left:20px;background:var(--ground);color:var(--cream)}
.tab{right:20px;background:var(--candy);color:var(--ink);border:1.5px solid var(--ink);border-bottom:none}
.head{display:flex;gap:14px;align-items:center}
.dial{flex:0 0 auto;width:74px;height:74px;border-radius:50%;border:1.5px solid var(--gold);padding:5px;
background:conic-gradient(var(--candy) calc(var(--s)*1%),var(--blush) 0) content-box;display:grid;place-items:center;
position:relative}
.dial b{position:absolute;inset:14px;border-radius:50%;background:var(--cream);border:1px solid var(--gold);display:grid;
place-items:center;font-family:var(--mono);font-weight:500;font-size:18px;color:var(--ink)}
.title{font-family:var(--display);font-weight:800;font-size:22px;line-height:1.08;margin:0}
.by{font-family:var(--label);font-weight:800;font-size:12px;color:var(--wine);margin-top:4px}
.p-hi{background:var(--candy)}.p-mid{background:var(--lilac)}.p-lo{background:transparent;border:1px solid var(--ink);opacity:.7}
.card .pill{align-self:flex-start}
.why{margin:0;padding-left:18px;font-size:16px}.why li{margin:2px 0}.why li::marker{color:var(--gold)}
.bars{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;text-align:center;line-height:1.25;padding-top:4px;
border-top:1px solid var(--gold)}
.bars div{font-family:var(--label);font-weight:800;font-size:10px;letter-spacing:.08em;text-transform:uppercase}
.bars b{display:block;font-family:var(--mono);font-weight:500;font-size:13px;letter-spacing:0}
.bars i{display:block;height:5px;background:var(--blush);margin-top:3px;position:relative;border-radius:3px;overflow:hidden}
.bars i::after{content:"";position:absolute;inset:0 auto 0 0;width:calc(var(--v)*1%);background:var(--ground)}
.links{display:flex;gap:14px;flex-wrap:wrap;font-family:var(--label);font-weight:800;font-size:13px}
.pick{display:flex;align-items:center;gap:10px;margin-top:auto;font-family:var(--label);font-weight:800;font-size:15px;
color:var(--ink);cursor:pointer;user-select:none}
.pick input{appearance:none;-webkit-appearance:none;width:24px;height:24px;border:1.5px solid var(--ink);
background:var(--cream);border-radius:6px;display:grid;place-items:center;margin:0;cursor:pointer}
.pick input:checked{background:var(--ground);border-color:var(--ground)}
.pick input:checked::after{content:"\\2713";color:var(--cream);font-weight:900;font-size:16px;font-family:var(--body)}
.pick input:focus-visible{outline:2px solid var(--magenta);outline-offset:2px}
.bar{position:fixed;left:0;right:0;bottom:0;background:var(--ground);color:var(--cream);padding:12px 16px;display:flex;
gap:14px;align-items:center;justify-content:center;flex-wrap:wrap;z-index:5;border-top:1px solid var(--gold)}
.bar b{font-family:var(--mono);font-weight:500}
.bar button{font-family:var(--label);font-weight:800;background:var(--candy);color:var(--ink);border:0;border-radius:999px;
padding:9px 18px;cursor:pointer;font-size:14px}
.bar button:focus-visible{outline:2px solid var(--cream);outline-offset:3px}
.bar output{font-family:var(--mono);font-size:13px;max-width:60ch;overflow-wrap:anywhere}
"""


def _band_class(score: int) -> str:
    return "p-hi" if score >= 75 else "p-mid" if score >= 55 else "p-lo"


def _link(url: str, label: str) -> str:
    u = safe_url(url)
    if not u:
        return ""
    return f'<a href="{escape(u)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a>'


def _card(i: int, s: dict) -> str:
    score = int(s.get("score", 0))
    parts = s.get("parts", {})
    labels = [("fit", "Fit"), ("recency", "Fresh"), ("guests", "Guests"), ("size", "Size"), ("cadence", "Rhythm")]
    bars = "".join(
        f'<div>{escape(lab)}<br><b>{int(parts.get(k, 0))}</b><i style="--v:{int(parts.get(k, 0))}"></i></div>' for k, lab in labels
    )
    why = "".join(f"<li>{escape(r)}</li>" for r in s.get("reasons", [])[:5])
    links = [
        _link(s.get("guest_link", ""), "Be a guest page"),
        _link(s.get("website", ""), "Show website"),
        _link(s.get("apple_url", ""), "Listen"),
    ]
    links_html = "".join(x for x in links if x) or '<span class="by">No public link in the feed</span>'
    by = f'<div class="by">{escape(s.get("author") or "")}</div>' if s.get("author") else ""
    slug = escape(s.get("slug", ""))
    return f"""<article class="card">
<span class="rank">no.{i:02d}</span><span class="tab">{score}/100</span>
<div class="head"><div class="dial" style="--s:{score}"><b>{score}</b></div>
<div><h2 class="title">{escape(s.get("title", "Untitled"))}</h2>{by}</div></div>
<span class="pill {_band_class(score)}">{escape(s.get("band", ""))}</span>
<ul class="why">{why}</ul>
<div class="bars" aria-label="Score parts">{bars}</div>
<div class="links">{links_html}</div>
<label class="pick"><input type="checkbox" data-slug="{slug}" data-title="{escape(s.get("title", ""))}"> Pitch this one</label>
</article>"""


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



def invite_card(style: dict, name: str | None) -> str:
    """Invitation lines come from style.json. --name replaces who you are invited to."""
    l1, l2, l3 = (escape(x) for x in invite_lines(style, name))
    if not l1:
        return ""
    return (f'<div class="invite">{coupe_svg(style)}<p class="t1">{l1}</p>'
            f'<p class="t2">{l2}</p><p class="t3">{l3}</p></div>')


def shortlist_html(scored: list[dict], meta: dict, style: dict | None = None) -> str:
    style = style or _default_style()
    lines = style.get("lines", {})
    n = len(scored)
    ring = sum(1 for s in scored if s.get("score", 0) >= 75)
    today = meta.get("date") or date.today().isoformat()
    niche = meta.get("niche") or "your niche"
    cards = "".join(_card(i + 1, s) for i, s in enumerate(scored)) or \
        '<p class="empty">No shows yet. Run discover, then score.</p>'
    run_id = escape(json.dumps([today, niche, n])[:120])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Podcast Hotline</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{escape(fonts_url(style))}">
<style>{root_css(style)}{BASE_CSS}{SHORTLIST_CSS}</style></head>
<body data-run="{run_id}"><div class="wrap">
<header class="band">
<div class="top lab"><span>{escape(lines.get("masthead") or "The podcast issue")}</span><span class="date">{escape(today)}</span><span>{escape(style.get("name") or "")}</span></div>
<h1>Hotline</h1>
</header>
<section class="cover-grid"><div class="cover">
<p class="script">Call the girls!</p>
<p class="line"><em>{n} shows</em> where {escape(niche)} is the conversation</p>
<p class="line">{ring} ready to <em>ring today</em>, ranked by fit</p>
<p class="line">Tick the ones you want. <em>You press send.</em></p>
</div><div class="side">{phone_svg(style)}{invite_card(style, meta.get("name"))}</div></section>
<div class="how"><span>fit <b>35%</b></span><span>fresh <b>20%</b></span><span>guests <b>20%</b></span><span>size <b>15%</b></span><span>rhythm <b>10%</b></span></div>
<main class="cards">{cards}</main>
<footer class="foot"><span class="yours">Every send is yours. Nothing goes out on its own.</span>
<span class="lab">Rocha Coded. Free tools from the Rocheverse.</span></footer>
</div>
<div class="bar"><span class="lab">picks <b id="picks-n">0</b></span><button id="copy" type="button">Copy picks for Claude</button>
<output id="picks-out" aria-live="polite"></output></div>
{PICK_JS}
</body></html>
"""


TRACKER_CSS = """
.stats{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:30px}
.stat{background:var(--cream);border:1px solid var(--gold);border-radius:12px;padding:10px 16px;min-width:110px;
font-family:var(--label);font-weight:800;font-size:12px;letter-spacing:.12em;text-transform:uppercase;
box-shadow:0 8px 18px rgba(59,18,48,.10)}
.stat b{font-family:var(--mono);font-weight:500;font-size:30px;display:block;letter-spacing:0;color:var(--ground)}
.slips{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:26px}
.slip{position:relative;background:var(--blush);border:1.5px solid var(--ink);border-radius:6px;padding:16px 18px 18px;
box-shadow:0 14px 26px rgba(59,18,48,.16);background-image:repeating-linear-gradient(transparent 0 27px,rgba(59,18,48,.10) 27px 28px)}
.slip h3{margin:0 0 2px;padding-right:110px;font-family:var(--display);font-weight:800;font-size:22px;line-height:1.1}
.slip .k{font-family:var(--label);font-weight:800;letter-spacing:.12em;text-transform:uppercase;font-size:10px;color:var(--wine)}
.slip .v{font-family:var(--mono);font-size:14px}
.slip .row{display:flex;justify-content:space-between;gap:10px;margin-top:10px;padding-top:8px;border-top:1px solid var(--gold)}
.ttl{background:var(--ground);color:var(--cream);margin:-16px -18px 12px;padding:7px 18px;border-radius:4px 4px 0 0;
font-family:var(--label);font-weight:800;letter-spacing:.18em;text-transform:uppercase;font-size:11px}
.stamp{position:absolute;top:46px;right:12px;transform:rotate(6deg);border:2px solid currentColor;border-radius:6px;
padding:2px 8px;font-family:var(--label);font-weight:800;letter-spacing:.14em;text-transform:uppercase;font-size:12px;
background:var(--cream)}
.s-pitched,.s-nudged{color:var(--wine)}.s-replied{color:var(--magenta)}.s-booked{color:var(--ground);border-color:var(--gold)}
.s-aired{color:var(--ink);border-color:var(--gold)}.s-passed{color:var(--ink);opacity:.55}
.due{margin-top:12px;background:var(--candy)}
.notes{font-family:var(--display);font-style:italic;color:var(--ink);font-size:16px;margin-top:8px;line-height:1.3}
"""


def tracker_html(rows: list[dict], today: date, due_rows: list[dict], style: dict | None = None) -> str:
    style = style or _default_style()
    lines = style.get("lines", {})
    counts = {k: sum(1 for r in rows if r["status"] == k) for k in ("pitched", "nudged", "replied", "booked", "aired")}
    due_names = {r["show"] for r in due_rows}
    slips = []
    for r in rows:
        st = r["status"] if r["status"] else "pitched"
        link = _link(r.get("link", ""), "Their page")
        due = '<span class="pill due">Nudge due!</span>' if r["show"] in due_names else ""
        notes = f'<div class="notes">{escape(r["notes"])}</div>' if r.get("notes") else ""
        slips.append(f"""<article class="slip"><div class="ttl">While you were out</div>
<span class="stamp s-{escape(st)}">{escape(st)}</span>
<h3>{escape(r["show"])}</h3>{link}
<div class="row"><div><div class="k">Pitched</div><div class="v">{escape(r["date_pitched"] or "-")}</div></div>
<div><div class="k">Nudges</div><div class="v">{escape(str(r["nudges"]))} of 2</div></div>
<div><div class="k">Next nudge</div><div class="v">{escape(r["next_nudge"] or "-")}</div></div></div>
{due}{notes}</article>""")
    body = "".join(slips) or '<p class="empty">No pitches logged yet. Your first one goes here.</p>'
    stats = "".join(f'<div class="stat"><b>{v}</b>{escape(k)}</div>' for k, v in counts.items())
    open_n = sum(1 for r in rows if r["status"] in OPEN_STATUSES)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Podcast Call Log</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{escape(fonts_url(style))}">
<style>{root_css(style)}{BASE_CSS}{TRACKER_CSS}</style></head>
<body><div class="wrap">
<header class="band">
<div class="top lab"><span>{escape(lines.get("masthead") or "The call log")}</span><span class="date">{escape(today.isoformat())}</span><span>{escape(style.get("name") or "")}</span></div>
<h1>Call Log</h1>
</header>
<section class="cover-grid"><div class="cover">
<p class="script">{escape((lines.get("affirm") or "Every send is yours").capitalize())}</p>
<p class="line"><em>{len(due_rows)} due</em> a nudge today</p>
<p class="line">{open_n} still waiting, <em>{counts["booked"]} booked</em></p>
</div><div class="side">{phone_svg(style)}</div></section>
<div class="stats">{stats}</div>
<main class="slips">{body}</main>
<footer class="foot"><span class="yours">Every send is yours. Nothing goes out on its own.</span>
<span class="lab">Rocha Coded. Free tools from the Rocheverse.</span></footer>
</div></body></html>
"""
