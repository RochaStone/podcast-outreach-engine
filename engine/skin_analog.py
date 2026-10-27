"""The analog skin: paper you could hold. Plum masthead band, the rotary phone, Rolodex cards, While-you-were-out slips."""

from __future__ import annotations

from html import escape

from .common import GRAIN, PICK_JS, coupe_svg, link, page, phone_svg

BASE_CSS = """
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




def _invite(style: dict, lines: list[str]) -> str:
    l1, l2, l3 = (escape(x) for x in lines)
    if not l1:
        return ""
    return (f'<div class="invite">{coupe_svg(style)}<p class="t1">{l1}</p>'
            f'<p class="t2">{l2}</p><p class="t3">{l3}</p></div>')


def _card(c: dict) -> str:
    bars = "".join(f'<div>{escape(lab)}<b>{v}</b><i style="--v:{v}"></i></div>' for lab, v in c["parts"])
    why = "".join(f"<li>{escape(r)}</li>" for r in c["reasons"])
    links = "".join(link(u, lab) for lab, u in c["links"]) or '<span class="by">No public link in the feed</span>'
    by = f'<div class="by">{escape(c["author"])}</div>' if c["author"] else ""
    return f"""<article class="card">
<span class="rank">no.{c["i"]:02d}</span><span class="tab">{c["score"]}/100</span>
<div class="head"><div class="dial" style="--s:{c["score"]}"><b>{c["score"]}</b></div>
<div><h2 class="title">{escape(c["title"])}</h2>{by}</div></div>
<span class="pill p-{c["cls"]}">{escape(c["band"])}</span>
<ul class="why">{why}</ul>
<div class="bars" aria-label="Score parts">{bars}</div>
<div class="links">{links}</div>
<label class="pick"><input type="checkbox" data-slug="{escape(c["slug"])}" data-title="{escape(c["title"])}"> Pitch this one</label>
</article>"""


def shortlist(m: dict, style: dict) -> str:
    cards = "".join(_card(c) for c in m["cards"]) or '<p class="empty">No shows yet. Run discover, then score.</p>'
    body = f"""<div class="wrap">
<header class="band">
<div class="top lab"><span>{escape(m["masthead"])}</span><span class="date">{escape(m["date"])}</span><span>{escape(m["name"])}</span></div>
<h1>Hotline</h1>
</header>
<section class="cover-grid"><div class="cover">
<p class="script">Call the girls!</p>
<p class="line"><em>{m["n"]} shows</em> where {escape(m["niche"])} is the conversation</p>
<p class="line">{m["ring"]} ready to <em>ring today</em>, ranked by fit</p>
<p class="line">Tick the ones you want. <em>You press send.</em></p>
</div><div class="side">{phone_svg(style)}{_invite(style, m["invite"])}</div></section>
<div class="how"><span>fit <b>35%</b></span><span>fresh <b>20%</b></span><span>guests <b>20%</b></span><span>size <b>15%</b></span><span>rhythm <b>10%</b></span></div>
<main class="cards">{cards}</main>
<footer class="foot"><span class="yours">Every send is yours. Nothing goes out on its own.</span>
<span class="lab">Rocha Coded. Free tools from the Rocheverse.</span></footer>
</div>
<div class="bar"><span class="lab">picks <b id="picks-n">0</b></span><button id="copy" type="button">Copy picks for Claude</button>
<output id="picks-out" aria-live="polite"></output></div>
{PICK_JS}"""
    return page("Podcast Hotline", style, BASE_CSS + SHORTLIST_CSS, body, False, f' data-run="{escape(m["run_id"])}" data-motif="analog"')


def tracker(m: dict, style: dict) -> str:
    slips = []
    for r in m["rows"]:
        due = '<span class="pill due">Nudge due!</span>' if r["due"] else ""
        notes = f'<div class="notes">{escape(r["notes"])}</div>' if r["notes"] else ""
        slips.append(f"""<article class="slip"><div class="ttl">While you were out</div>
<span class="stamp s-{escape(r["status"])}">{escape(r["status"])}</span>
<h3>{escape(r["show"])}</h3>{link(r["link"], "Their page")}
<div class="row"><div><div class="k">Pitched</div><div class="v">{escape(r["date_pitched"])}</div></div>
<div><div class="k">Nudges</div><div class="v">{escape(r["nudges"])} of 2</div></div>
<div><div class="k">Next nudge</div><div class="v">{escape(r["next_nudge"])}</div></div></div>
{due}{notes}</article>""")
    rows = "".join(slips) or '<p class="empty">No pitches logged yet. Your first one goes here.</p>'
    stats = "".join(f'<div class="stat"><b>{v}</b>{escape(k)}</div>' for k, v in m["counts"].items())
    body = f"""<div class="wrap">
<header class="band">
<div class="top lab"><span>{escape(m["masthead"])}</span><span class="date">{escape(m["date"])}</span><span>{escape(m["name"])}</span></div>
<h1>Call Log</h1>
</header>
<section class="cover-grid"><div class="cover">
<p class="script">{escape(m["affirm"])}</p>
<p class="line"><em>{m["due_n"]} due</em> a nudge today</p>
<p class="line">{m["open_n"]} still waiting, <em>{m["counts"]["booked"]} booked</em></p>
</div><div class="side">{phone_svg(style)}</div></section>
<div class="stats">{stats}</div>
<main class="slips">{rows}</main>
<footer class="foot"><span class="yours">Every send is yours. Nothing goes out on its own.</span>
<span class="lab">Rocha Coded. Free tools from the Rocheverse.</span></footer>
</div>"""
    return page("Podcast Call Log", style, BASE_CSS + TRACKER_CSS, body, False, ' data-motif="analog"')
