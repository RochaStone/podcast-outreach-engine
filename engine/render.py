"""HTML pages for podcast-outreach-engine: the shortlist and the tracker.

Pink rotary phone motif. Every value from a feed is escaped and every link is
checked to be http(s) before it reaches the page. The pages open from disk in
any browser. Fonts load from Google Fonts when online and fall back to system
serif and sans when offline.
"""

from __future__ import annotations

import json
from datetime import date
from html import escape

from .feeds import safe_url
from .tracker import OPEN_STATUSES

FONTS = ("https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..900;1,6..96,400..900"
         "&family=Archivo+Narrow:wght@500;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400"
         "&family=Permanent+Marker&family=Courier+Prime:wght@400;700&display=swap")

GRAIN = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 0.3 0 0 0 0 0.05 0 0 0 0 0.15 0 0 0 .07 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)'/></svg>\")")

BASE_CSS = """
:root{--hot:#FF2D8A;--candy:#FFB3D1;--paper:#FFE1EC;--cream:#F6EFE4;--ink:#111111;--red:#E0202E;
--plum:#4A1033;--gold:#D4A64A;--blue:#BFD4EA;--white:#FFFFFF;
--didone:'Bodoni Moda','Didot','Bodoni 72',Georgia,serif;--tag:'Archivo Narrow','Arial Narrow',Helvetica,sans-serif;
--body:'Newsreader',Georgia,serif;--marker:'Permanent Marker','Marker Felt','Comic Sans MS',cursive;
--mono:'Courier Prime','Courier New',monospace}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);background-image:GRAIN;color:var(--ink);font-family:var(--body);
font-size:17px;line-height:1.45}
a{color:var(--plum)}
.wrap{max-width:1180px;margin:0 auto;padding:28px 16px 120px}
.tag{font-family:var(--tag);text-transform:uppercase;letter-spacing:.14em;font-weight:700;font-size:12px}
.mast{position:relative;border-bottom:3px solid var(--ink);padding-bottom:18px;margin-bottom:28px;overflow:hidden}
.mast .top{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.mast h1{font-family:var(--didone);font-weight:900;color:var(--hot);margin:4px 0 0;line-height:.82;
font-size:clamp(64px,15vw,190px);letter-spacing:-.02em;text-shadow:3px 3px 0 var(--plum)}
.mast .grid{display:grid;grid-template-columns:1.1fr .9fr;gap:20px;align-items:center}
.cover{display:flex;flex-direction:column;gap:14px}.cover p{margin:0}.cover .scrawl{margin-bottom:14px}
.scrawl{font-family:var(--marker);color:var(--red);font-size:clamp(30px,5vw,54px);transform:rotate(-4deg);
line-height:1;margin:6px 0 4px}
.line{font-family:var(--didone);font-size:clamp(20px,2.6vw,28px);font-weight:600;line-height:1.1;max-width:22ch}
.line em{color:var(--hot);font-style:italic}
.phone{width:100%;max-width:360px;justify-self:center;filter:drop-shadow(6px 10px 0 rgba(74,16,51,.25))}
.foot{margin-top:48px;border-top:3px solid var(--ink);padding-top:14px;display:flex;justify-content:space-between;
gap:12px;flex-wrap:wrap}
.yours{font-family:var(--marker);color:var(--red);font-size:22px}
.side{display:flex;flex-direction:column;align-items:center;gap:18px}
.invite{position:relative;background:var(--cream);border:2.5px solid var(--ink);padding:16px 22px 16px 74px;
transform:rotate(2deg);box-shadow:5px 6px 0 rgba(74,16,51,.35);max-width:380px;text-align:left}
.invite svg{position:absolute;left:16px;top:50%;transform:translateY(-50%);width:44px}
.invite .t1{font-family:var(--didone);font-weight:800;font-size:17px;letter-spacing:.06em;line-height:1.15;margin:0}
.invite .t2{font-family:var(--didone);font-style:italic;font-size:17px;color:var(--hot);margin:4px 0 0}
.invite .t3{font-family:var(--marker);color:var(--red);font-size:17px;margin:4px 0 0}
@media (max-width:760px){.mast .grid{grid-template-columns:1fr}.phone{max-width:240px}}
""".replace("GRAIN", GRAIN)

PHONE_SVG = """<svg class="phone" viewBox="0 0 400 330" role="img" aria-label="A pink rotary phone">
<path d="M60 300 L95 150 Q100 132 120 132 L280 132 Q300 132 305 150 L340 300 Z" fill="#FF2D8A" stroke="#111" stroke-width="5"/>
<path d="M40 112 Q40 70 90 62 L310 62 Q360 70 360 112 L360 124 Q360 140 340 140 L300 140 Q284 140 282 124 L278 104
L122 104 L118 124 Q116 140 100 140 L60 140 Q40 140 40 124 Z" fill="#FFB3D1" stroke="#111" stroke-width="5"/>
<circle cx="200" cy="222" r="70" fill="#F6EFE4" stroke="#111" stroke-width="5"/>
<g fill="#FF2D8A" stroke="#111" stroke-width="3">
<circle cx="200" cy="170" r="11"/><circle cx="236" cy="182" r="11"/><circle cx="252" cy="214" r="11"/>
<circle cx="244" cy="250" r="11"/><circle cx="216" cy="271" r="11"/><circle cx="182" cy="272" r="11"/>
<circle cx="154" cy="252" r="11"/><circle cx="146" cy="216" r="11"/><circle cx="162" cy="183" r="11"/></g>
<circle cx="200" cy="222" r="24" fill="#FFE1EC" stroke="#111" stroke-width="4"/>
<path d="M262 262 L282 282" stroke="#D4A64A" stroke-width="7" stroke-linecap="round"/>
<path d="M330 140 C 390 170, 380 250, 340 300" fill="none" stroke="#111" stroke-width="4" stroke-dasharray="2 9" stroke-linecap="round"/>
</svg>"""

SHORTLIST_CSS = """
.how{display:flex;gap:18px;flex-wrap:wrap;margin:0 0 22px;align-items:center}
.how span{background:var(--white);border:2px solid var(--ink);padding:4px 10px;box-shadow:3px 3px 0 var(--ink)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:34px 26px}
.card{position:relative;background:var(--cream);border:2.5px solid var(--ink);border-radius:18px 18px 14px 14px;
padding:22px 20px 46px;box-shadow:6px 8px 0 rgba(17,17,17,.85);display:flex;flex-direction:column;gap:10px}
.card:nth-child(3n+2){transform:rotate(.6deg)}.card:nth-child(3n){transform:rotate(-.5deg)}
.card::before,.card::after{content:"";position:absolute;bottom:-3px;width:34px;height:20px;background:var(--paper);
border:2.5px solid var(--ink);border-bottom:none;border-radius:16px 16px 0 0}
.card::before{left:calc(50% - 64px)}.card::after{left:calc(50% + 30px)}
.tab{position:absolute;top:-19px;right:22px;background:var(--hot);color:var(--white);border:2.5px solid var(--ink);
border-bottom:none;border-radius:10px 10px 0 0;padding:2px 14px 3px;font-family:var(--mono);font-weight:700}
.rank{position:absolute;top:-19px;left:22px;background:var(--ink);color:var(--paper);border-radius:10px 10px 0 0;
padding:2px 12px 3px;font-family:var(--mono);font-weight:700}
.head{display:flex;gap:14px;align-items:center}
.dial{flex:0 0 auto;width:74px;height:74px;border-radius:50%;border:2.5px solid var(--ink);
background:conic-gradient(var(--hot) calc(var(--s)*1%),var(--candy) 0);display:grid;place-items:center}
.dial b{width:48px;height:48px;border-radius:50%;background:var(--cream);border:2px solid var(--ink);display:grid;
place-items:center;font-family:var(--didone);font-size:22px;font-weight:900}
.title{font-family:var(--didone);font-weight:800;font-size:22px;line-height:1.08;margin:0}
.by{font-family:var(--tag);font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--plum);margin-top:4px}
.band{align-self:flex-start;font-family:var(--tag);font-weight:700;text-transform:uppercase;letter-spacing:.12em;
font-size:12px;padding:3px 9px;border:2px solid currentColor;transform:rotate(-2deg)}
.b-hi{color:var(--red)}.b-mid{color:var(--plum)}.b-lo{color:#6b5a62}
.why{margin:0;padding-left:18px}.why li{margin:2px 0}
.bars{display:grid;grid-template-columns:repeat(5,1fr);gap:6px;font-family:var(--mono);font-size:11px;text-align:center;line-height:1.2}.bars b{font-size:13px}
.bars i{display:block;height:6px;background:var(--candy);border:1px solid var(--ink);margin-top:3px;position:relative}
.bars i::after{content:"";position:absolute;inset:0 auto 0 0;width:calc(var(--v)*1%);background:var(--hot)}
.links{display:flex;gap:12px;flex-wrap:wrap;font-family:var(--tag);font-weight:700;text-transform:uppercase;
letter-spacing:.08em;font-size:13px}
.pick{display:flex;align-items:center;gap:10px;margin-top:auto;font-family:var(--marker);font-size:20px;
color:var(--red);cursor:pointer;user-select:none}
.pick input{appearance:none;-webkit-appearance:none;width:26px;height:26px;border:2.5px solid var(--ink);
background:var(--white);border-radius:4px;display:grid;place-items:center;margin:0;cursor:pointer}
.pick input:checked{background:var(--hot)}
.pick input:checked::after{content:"\\2713";color:var(--white);font-weight:900;font-size:18px;font-family:var(--body)}
.pick input:focus-visible{outline:3px solid var(--plum);outline-offset:2px}
.bar{position:fixed;left:0;right:0;bottom:0;background:var(--ink);color:var(--paper);padding:12px 16px;display:flex;
gap:14px;align-items:center;justify-content:center;flex-wrap:wrap;z-index:5}
.bar button{font-family:var(--tag);font-weight:700;text-transform:uppercase;letter-spacing:.12em;background:var(--hot);
color:var(--white);border:2px solid var(--paper);padding:8px 16px;cursor:pointer;font-size:14px}
.bar output{font-family:var(--mono);font-size:13px;max-width:60ch;overflow-wrap:anywhere}
.empty{font-family:var(--didone);font-size:26px}
"""


def _band_class(score: int) -> str:
    return "b-hi" if score >= 75 else "b-mid" if score >= 55 else "b-lo"


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
<span class="rank">No.{i:02d}</span><span class="tab">{score}/100</span>
<div class="head"><div class="dial" style="--s:{score}"><b>{score}</b></div>
<div><h2 class="title">{escape(s.get("title", "Untitled"))}</h2>{by}</div></div>
<span class="band {_band_class(score)}">{escape(s.get("band", ""))}</span>
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


COUPE_SVG = """<svg viewBox="0 0 44 60" aria-hidden="true"><path d="M4 8 Q22 30 40 8 Z" fill="#FFB3D1" stroke="#111" stroke-width="2.5"/>
<path d="M22 22 L22 50 M12 54 L32 54" stroke="#111" stroke-width="2.5" stroke-linecap="round"/>
<circle cx="31" cy="5" r="2.5" fill="#D4A64A"/><circle cx="36" cy="12" r="1.8" fill="#D4A64A"/></svg>"""

HOUSE_INVITE = "THE ROCHEVERSE"


def invite_card(name: str | None) -> str:
    """Her invitation line, verbatim. The user's name replaces THE ROCHEVERSE in their own outputs."""
    who = escape((name or "").strip().upper()) or HOUSE_INVITE
    return (f'<div class="invite">{COUPE_SVG}<p class="t1">YOU ARE INVITED TO {who}</p>'
            '<p class="t2">come build your founder world</p><p class="t3">dress code: lore</p></div>')


def shortlist_html(scored: list[dict], meta: dict) -> str:
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
<link rel="stylesheet" href="{FONTS}">
<style>{BASE_CSS}{SHORTLIST_CSS}</style></head>
<body data-run="{run_id}"><div class="wrap">
<header class="mast">
<div class="top"><span class="tag">The podcast issue</span><span class="tag">{escape(today)}</span><span class="tag">Rocha Coded</span></div>
<h1>Hotline</h1>
<div class="grid"><div class="cover">
<p class="scrawl">Call the girls!</p>
<p class="line"><em>{n} shows</em> where {escape(niche)} is the conversation</p>
<p class="line">{ring} ready to <em>ring today</em>, ranked by fit</p>
<p class="line">Tick the ones you want. <em>You press send.</em></p>
</div><div class="side">{PHONE_SVG}{invite_card(meta.get("name"))}</div></div>
</header>
<div class="how tag"><span>Fit 35%</span><span>Fresh 20%</span><span>Guests 20%</span><span>Size 15%</span><span>Rhythm 10%</span></div>
<main class="cards">{cards}</main>
<footer class="foot"><span class="yours">Every send is yours. Nothing goes out on its own.</span>
<span class="tag">Rocha Coded. Free tools from the Rocheverse.</span></footer>
</div>
<div class="bar"><span class="tag">Picks: <b id="picks-n">0</b></span><button id="copy" type="button">Copy picks for Claude</button>
<output id="picks-out" aria-live="polite"></output></div>
{PICK_JS}
</body></html>
"""


TRACKER_CSS = """
.stats{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:26px}
.stat{background:var(--white);border:2.5px solid var(--ink);box-shadow:4px 4px 0 var(--ink);padding:8px 14px;
font-family:var(--tag);text-transform:uppercase;letter-spacing:.1em;font-weight:700}
.stat b{font-family:var(--didone);font-size:30px;display:block;letter-spacing:0;color:var(--hot)}
.slips{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:24px}
.slip{position:relative;background:var(--white);border:2.5px solid var(--ink);padding:16px 18px 18px;
box-shadow:5px 7px 0 rgba(17,17,17,.85);background-image:repeating-linear-gradient(transparent 0 27px,var(--candy) 27px 28px)}
.slip h3{margin:0 0 2px;padding-right:112px;font-family:var(--didone);font-size:22px;line-height:1.1}
.slip .k{font-family:var(--tag);text-transform:uppercase;letter-spacing:.12em;font-size:11px;color:var(--plum)}
.slip .v{font-family:var(--mono);font-size:15px}
.slip .row{display:flex;justify-content:space-between;gap:10px;margin-top:8px}
.ttl{background:var(--hot);color:var(--white);margin:-16px -18px 12px;padding:6px 18px;font-family:var(--tag);
font-weight:700;letter-spacing:.2em;text-transform:uppercase;font-size:13px}
.stamp{position:absolute;top:44px;right:12px;transform:rotate(8deg);border:3px solid currentColor;padding:2px 8px;
font-family:var(--tag);font-weight:700;letter-spacing:.14em;text-transform:uppercase;font-size:14px;background:rgba(255,255,255,.7)}
.s-pitched,.s-nudged{color:var(--plum)}.s-replied{color:var(--hot)}.s-booked{color:var(--red)}.s-aired{color:var(--gold)}
.s-passed{color:#7a6a70}
.due{display:inline-block;margin-top:10px;font-family:var(--marker);color:var(--red);font-size:20px;transform:rotate(-2deg)}
.notes{font-family:var(--marker);color:var(--ink);font-size:17px;margin-top:8px;line-height:1.2}
"""


def tracker_html(rows: list[dict], today: date, due_rows: list[dict]) -> str:
    counts = {k: sum(1 for r in rows if r["status"] == k) for k in ("pitched", "nudged", "replied", "booked", "aired")}
    due_names = {r["show"] for r in due_rows}
    slips = []
    for r in rows:
        st = r["status"] if r["status"] else "pitched"
        link = _link(r.get("link", ""), "Their page")
        due = '<span class="due">Nudge due!</span>' if r["show"] in due_names else ""
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
<link rel="stylesheet" href="{FONTS}">
<style>{BASE_CSS}{TRACKER_CSS}.mast h1{{font-size:clamp(56px,12vw,150px)}}</style></head>
<body><div class="wrap">
<header class="mast">
<div class="top"><span class="tag">The call log</span><span class="tag">{escape(today.isoformat())}</span><span class="tag">Rocha Coded</span></div>
<h1>Call Log</h1>
<div class="grid"><div class="cover">
<p class="scrawl">Everything works out for me</p>
<p class="line"><em>{len(due_rows)} due</em> a nudge today</p>
<p class="line">{open_n} still waiting, <em>{counts["booked"]} booked</em></p>
</div>{PHONE_SVG}</div>
</header>
<div class="stats">{stats}</div>
<main class="slips">{body}</main>
<footer class="foot"><span class="yours">Every send is yours. Nothing goes out on its own.</span>
<span class="tag">Rocha Coded. Free tools from the Rocheverse.</span></footer>
</div></body></html>
"""
