"""The y2k-blog skin: the 2003 blog page. A cream OS-9 window titled hotline.exe with a plum title bar and
three gold buttons, a blog sidebar (about me, currently pitching, mood), a hit counter, a marquee line,
gold pixel hearts and stars on a tiled blush background. The call log is a guestbook."""

from __future__ import annotations

from html import escape

from .common import PICK_JS, link, page, pixel_heart, pixel_star

VISITOR = "000,777"  # her hit counter line: "you are visitor no. 000,777"
MARQ = f"every send is yours ✧ nothing goes out on its own ✧ you are visitor no. {VISITOR} ✧ "


def _tile(style: dict) -> str:
    p = style.get("palette", {})
    g = p.get("gold", "#E9B949").replace("#", "%23")
    c = p.get("paper", "#FFF7F4").replace("#", "%23")
    return ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='28' height='28' "
            f"shape-rendering='crispEdges'><rect x='2' y='2' width='2' height='2' fill='{c}'/>"
            f"<rect x='16' y='16' width='2' height='2' fill='{g}' opacity='.55'/></svg>\")")


CSS = """
body{background:var(--blush);background-image:TILE;font-family:var(--label);font-weight:400}
.win{max-width:1180px;margin:22px auto 110px;background:var(--cream);border:1.5px solid var(--ink);
box-shadow:6px 8px 0 rgba(59,18,48,.22)}
.tb{display:flex;align-items:center;gap:10px;background:var(--ground);color:var(--cream);padding:6px 10px;
border-bottom:1.5px solid var(--ink);background-image:repeating-linear-gradient(0deg,rgba(255,247,244,.10) 0 1px,transparent 1px 3px)}
.tb .ttl{font-family:var(--pixel);font-size:13px;letter-spacing:.04em;flex:1;text-align:center}
.tb .btns{display:flex;gap:6px}.tb .btns i{width:13px;height:13px;background:var(--gold);border:1.5px solid var(--ink);display:block}
.px-lab{font-family:var(--pixel);font-size:12px}
.menu{display:flex;gap:18px;padding:5px 14px;border-bottom:1px solid var(--ink);font-family:var(--pixel);font-size:11px}
.marq{overflow:hidden;white-space:nowrap;border-bottom:1px dashed var(--gold);font-family:var(--mono);font-size:13px;color:var(--wine);
padding:5px 0}
.marq span{display:inline-block;padding-left:14px;animation:marq 30s linear infinite}
@keyframes marq{to{transform:translateX(-50%)}}
.cols{display:grid;grid-template-columns:1fr 290px;gap:0}
.main{padding:22px 24px;border-right:1px solid var(--ink)}
.side{padding:18px 16px;background:var(--blush);display:flex;flex-direction:column;gap:16px}
h1{font-family:var(--display);font-weight:900;font-size:clamp(40px,7vw,72px);line-height:.95;margin:0;color:var(--ground)}
.sub{font-family:var(--script);color:var(--magenta);font-size:clamp(30px,4.4vw,44px);margin:2px 0 8px;line-height:1}
.intro{margin:0 0 20px;font-size:16px}
.post{border:1px solid var(--ink);background:var(--cream);margin:0 0 22px}
.post .ph{display:flex;justify-content:space-between;gap:8px;background:var(--blush);border-bottom:1px solid var(--ink);
padding:4px 10px;font-family:var(--pixel);font-size:11px}
.post .pb{padding:12px 14px;display:flex;flex-direction:column;gap:8px}
.post h2{font-family:var(--display);font-weight:800;font-size:22px;line-height:1.1;margin:0}
.post .by{font-size:13px;color:var(--wine);font-weight:700}
.score{display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px;font-family:var(--mono)}
.score .meter{display:flex;gap:2px}.score .meter i{width:12px;height:12px;border:1px solid var(--ink);background:var(--cream)}
.score .meter i.on{background:var(--candy)}
.mood{font-family:var(--mono);font-size:13px;color:var(--wine)}
.badge{display:inline-block;white-space:nowrap;font-family:var(--pixel);font-size:11px;padding:3px 8px;border:1px solid var(--ink);color:var(--ink)}
.badge.hi{background:var(--candy)}.badge.mid{background:var(--lilac)}.badge.lo{background:var(--cream)}
.why{margin:0;padding-left:20px;font-size:15px;list-style:none}
.why li{position:relative}.why li::before{content:"";position:absolute;left:-16px;top:.5em;width:6px;height:6px;background:var(--gold)}
.links{display:flex;gap:14px;flex-wrap:wrap;font-size:14px;font-weight:700}
.pick{display:flex;align-items:center;gap:8px;font-family:var(--pixel);font-size:12px;cursor:pointer}
.pick input{appearance:none;-webkit-appearance:none;width:20px;height:20px;margin:0;border:1.5px solid var(--ink);
background:var(--cream);display:grid;place-items:center;cursor:pointer}
.pick input:checked{background:var(--candy)}.pick input:checked::after{content:"\\2665";color:var(--ink);font-size:13px}
.pick input:focus-visible{outline:2px solid var(--magenta);outline-offset:2px}
.box{border:1px solid var(--ink);background:var(--cream)}
.box h3{margin:0;padding:4px 8px;background:var(--ground);color:var(--cream);font-family:var(--pixel);font-size:11px;
font-weight:400;letter-spacing:.04em}
.box .bd{padding:10px;font-size:14px}.box ul{margin:0;padding-left:18px}.box p{margin:0 0 4px}
.counter{font-family:var(--mono);text-align:center;font-size:13px}
.counter b{display:inline-block;background:var(--ink);color:var(--gold);padding:2px 6px;letter-spacing:.12em;font-weight:500}
.hearts{display:flex;justify-content:center;gap:10px;align-items:center}
.foot{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;padding:8px 14px;border-top:1px solid var(--ink);
font-family:var(--mono);font-size:12px;background:var(--blush)}
.bar{position:fixed;left:0;right:0;bottom:0;background:var(--cream);color:var(--ink);padding:10px 16px;display:flex;gap:14px;
align-items:center;justify-content:center;flex-wrap:wrap;z-index:5;border-top:1.5px solid var(--ink)}
.bar b{font-family:var(--mono)}
.bar button{font-family:var(--pixel);font-size:12px;background:var(--candy);color:var(--ink);border:1.5px solid var(--ink);
padding:7px 12px;cursor:pointer;box-shadow:2px 2px 0 var(--ink)}
.bar button:focus-visible{outline:2px solid var(--magenta);outline-offset:3px}
.bar output{font-family:var(--mono);font-size:13px;max-width:60ch;overflow-wrap:anywhere}
.gb{display:flex;flex-direction:column;gap:14px}
.sig{border:1px dashed var(--wine);background:var(--cream);padding:10px 12px}
.sig .who{font-family:var(--display);font-weight:800;font-size:19px}
.sig .meta{font-family:var(--mono);font-size:12.5px;color:var(--wine)}
.sig .msg{font-family:var(--display);font-style:italic;margin-top:4px}
.sig.due{border-style:solid;border-color:var(--magenta)}
.sig .due{font-family:var(--pixel);font-size:11px;background:var(--candy);padding:2px 6px;margin-left:6px}
@media (max-width:760px){.cols{grid-template-columns:1fr}.main{border-right:0;border-bottom:1px solid var(--ink);padding:16px}
.win{margin:10px 8px 110px}}
"""


def _window(title: str, style: dict, main: str, side: str, foot_left: str) -> str:
    return f"""<div class="win">
<div class="tb"><span class="btns"><i></i><i></i><i></i></span><span class="ttl">{escape(title)}</span><span class="btns" aria-hidden="true"></span></div>
<div class="menu"><span>file</span><span>edit</span><span>view</span><span>special</span></div>
<div class="marq" aria-hidden="true"><span>{MARQ * 6}</span></div>
<div class="cols"><div class="main">{main}</div><aside class="side">{side}</aside></div>
<div class="foot"><span>{foot_left}</span><span>Rocha Coded. Free tools from the Rocheverse.</span></div>
</div>"""


def _meter(v: int) -> str:
    on = round(v / 10)
    return "".join('<i class="on"></i>' if k < on else "<i></i>" for k in range(10))


def _post(c: dict, date: str) -> str:
    why = "".join(f"<li>{escape(r)}</li>" for r in c["reasons"])
    links = "".join(link(u, lab) for lab, u in c["links"]) or "<span>no public link in the feed</span>"
    by = f'<div class="by">hosted by {escape(c["author"])}</div>' if c["author"] else ""
    parts = " · ".join(f"{escape(lab.lower())} {v}" for lab, v in c["parts"])
    return f"""<article class="post"><div class="ph"><span>entry no.{c["i"]:02d}</span><span>last updated {escape(date)}</span></div>
<div class="pb"><h2>{escape(c["title"])}</h2>{by}
<div class="score"><span class="meter" aria-label="Score {c["score"]} out of 100">{_meter(c["score"])}</span><b>{c["score"]}/100</b>
<span class="badge {c["cls"]}">{escape(c["band"].lower())}</span></div>
<div class="mood">mood: {parts}</div>
<ul class="why">{why}</ul>
<div class="links">{links}</div>
<label class="pick"><input type="checkbox" data-slug="{escape(c["slug"])}" data-title="{escape(c["title"])}"> pitch this one</label>
</div></article>"""


def _side_common(m: dict, style: dict) -> tuple[str, str]:
    gold = style.get("palette", {}).get("gold", "#E9B949")
    hearts = "".join(pixel_heart(gold, 16) if k % 2 == 0 else pixel_star(gold, 13) for k in range(5))
    counter = f'<div class="box"><div class="bd counter">you are visitor no.<br><b>{VISITOR}</b></div></div>'
    return f'<div class="hearts">{hearts}</div>', counter


def shortlist(m: dict, style: dict) -> str:
    l1, l2, l3 = m["invite"]
    about = "".join(f"<p>{escape(x)}</p>" for x in (l1, l2, l3) if x) or f"<p>{escape(m['owner'])}</p>"
    ringing = [c for c in m["cards"] if c["score"] >= 75][:6] or m["cards"][:3]
    pitching = "".join(f"<li>{escape(c['title'])}</li>" for c in ringing) or "<li>nothing yet</li>"
    hearts, counter = _side_common(m, style)
    side = f"""{hearts}
<div class="box"><h3>about me</h3><div class="bd">{about}</div></div>
<div class="box"><h3>currently pitching</h3><div class="bd"><ul>{pitching}</ul></div></div>
<div class="box"><h3>mood</h3><div class="bd">✧ {m["ring"]} ready to ring today</div></div>
{counter}"""
    posts = "".join(_post(c, m["date"]) for c in m["cards"]) or '<p class="empty">no entries yet. run discover, then score.</p>'
    main = f"""<h1>Hotline</h1><p class="sub">Call the girls!</p>
<p class="intro">{m["n"]} shows where {escape(m["niche"])} is the conversation, ranked by fit. Tick the ones you want. You press send.</p>
{posts}"""
    body = _window("hotline.exe", style, main, side, f"{escape(m['masthead'])} · last updated {escape(m['date'])}") + f"""
<div class="bar"><span class="px-lab">picks <b id="picks-n">0</b></span><button id="copy" type="button">copy picks for claude</button>
<output id="picks-out" aria-live="polite"></output></div>
{PICK_JS}"""
    css = CSS.replace("TILE", _tile(style))
    return page("Podcast Hotline", style, css, body, True, f' data-run="{escape(m["run_id"])}" data-motif="y2k-blog"')


def tracker(m: dict, style: dict) -> str:
    sigs = []
    for r in m["rows"]:
        due = '<span class="due">nudge due</span>' if r["due"] else ""
        msg = f'<div class="msg">{escape(r["notes"])}</div>' if r["notes"] else ""
        sigs.append(f"""<div class="sig{' due' if r["due"] else ''}"><div class="who">★ {escape(r["show"])}{due}</div>
<div class="meta">signed {escape(r["date_pitched"])} · status: {escape(r["status"])} · nudges {escape(r["nudges"])}/2 · next nudge {escape(r["next_nudge"])} {link(r["link"], "their page")}</div>{msg}</div>""")
    book = "".join(sigs) or '<p class="empty">the guestbook is empty. your first pitch signs it.</p>'
    hearts, counter = _side_common(m, style)
    stats = "".join(f"<p>{escape(k)}: <b>{v}</b></p>" for k, v in m["counts"].items())
    side = f"""{hearts}
<div class="box"><h3>stats</h3><div class="bd">{stats}</div></div>
<div class="box"><h3>mood</h3><div class="bd">✧ {escape(m["affirm"].lower())}</div></div>
{counter}"""
    main = f"""<h1>Guestbook</h1><p class="sub">{escape(m["affirm"])}</p>
<p class="intro">{m["due_n"]} due a nudge today. {m["open_n"]} still waiting. {m["counts"]["booked"]} booked.</p>
<div class="gb">{book}</div>"""
    body = _window("calllog.exe", style, main, side, f"{escape(m['masthead'])} · last updated {escape(m['date'])}")
    css = CSS.replace("TILE", _tile(style))
    return page("Podcast Call Log", style, css, body, True, ' data-motif="y2k-blog"')
