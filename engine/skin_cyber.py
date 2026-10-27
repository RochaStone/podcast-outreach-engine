"""The cyberpunk skin: the girly terminal. A plum switchboard in a cyberdeck bezel with gold screws, soft
scanlines (no glow, no flicker), pixel labels, block bars, a Nokia keypad for the ring-today row and a candy
block cursor. Same data model as every other skin."""

from __future__ import annotations

from html import escape

from .common import PICK_JS, link, page, pixel_heart

T9 = {c: k for k, letters in {"2": "ABC", "3": "DEF", "4": "GHI", "5": "JKL", "6": "MNO", "7": "PQRS", "8": "TUV",
                              "9": "WXYZ"}.items() for c in letters}
T9_LETTERS = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}

CSS = """
body{background:var(--ground);color:var(--cream);font-family:var(--label);
background-image:repeating-linear-gradient(0deg,rgba(255,247,244,.035) 0 1px,transparent 1px 3px)}
a{color:var(--candy)}
.deck{max-width:1180px;margin:18px auto 110px;padding:22px;border:10px solid var(--wine);border-radius:22px;position:relative;
background:var(--ground);box-shadow:0 18px 40px rgba(0,0,0,.35)}
.deck::before,.deck::after,.screws::before,.screws::after{content:"";position:absolute;width:10px;height:10px;border-radius:50%;
background:var(--gold);box-shadow:inset -2px -2px 0 rgba(59,18,48,.45)}
.deck::before{top:-8px;left:-8px}.deck::after{top:-8px;right:-8px}.screws::before{bottom:-8px;left:-8px}
.screws::after{bottom:-8px;right:-8px}
.px-lab{font-family:var(--pixel);font-size:12px;letter-spacing:.06em;text-transform:uppercase}
.status{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:center;padding-bottom:12px;
border-bottom:2px dashed rgba(233,185,73,.55)}
.leds{display:flex;gap:8px;align-items:center}
.led{width:10px;height:10px;border-radius:2px;background:var(--candy)}.led.g{background:var(--gold)}.led.o{background:transparent;
border:2px solid var(--cream);opacity:.5}
.term{font-family:var(--mono);font-size:15px;line-height:1.6;margin:18px 0 22px;overflow-wrap:anywhere}
.term p{margin:0}.term .pr{color:var(--candy)}.term .out{color:var(--cream);opacity:.85}.term .c{color:var(--gold)}
.cursor{display:inline-block;width:.6em;height:1.05em;background:var(--candy);vertical-align:-2px;
animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
h1{font-family:var(--pixel);font-weight:700;font-size:clamp(34px,7vw,64px);margin:6px 0 0;letter-spacing:.02em;line-height:1}
.panels{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:26px}
.panel{background:var(--wine);padding:18px 18px 16px;margin:6px;display:flex;flex-direction:column;gap:10px;
box-shadow:0 -6px 0 0 var(--cream),0 6px 0 0 var(--cream),-6px 0 0 0 var(--cream),6px 0 0 0 var(--cream),
0 0 0 6px var(--ground),0 12px 0 6px rgba(0,0,0,.25)}
.panel .hd{display:flex;justify-content:space-between;gap:8px;color:var(--gold)}
.panel h2{font-family:var(--label);font-weight:800;font-size:20px;line-height:1.15;margin:0;color:var(--cream)}
.panel .by{font-family:var(--mono);font-size:13px;color:var(--candy)}
.blocks{display:flex;gap:3px;align-items:center}
.blocks i{width:16px;height:14px;background:rgba(255,247,244,.14)}.blocks i.on{background:var(--candy)}
.blocks b{font-family:var(--mono);font-weight:500;margin-left:8px;font-size:15px}
.keys{display:flex;gap:6px;flex-wrap:wrap}
.key{min-width:42px;padding:4px 6px 3px;border-radius:12px 12px 16px 16px;text-align:center;line-height:1.05;
font-family:var(--pixel);color:var(--ink);background:var(--candy);border-bottom:3px solid rgba(59,18,48,.45)}
.key b{display:block;font-size:15px}.key small{font-size:9px;letter-spacing:.08em}
.k-mid .key{background:var(--lilac)}.k-lo .key{background:transparent;color:var(--cream);border:1.5px solid var(--cream)}
.keys .say{font-family:var(--pixel);font-size:11px;align-self:center;margin-left:4px;color:var(--cream)}
.why{margin:0;padding:0;list-style:none;font-family:var(--mono);font-size:13.5px;line-height:1.5}
.why li::before{content:"> ";color:var(--gold)}
.mini{display:grid;grid-template-columns:auto 1fr auto;gap:2px 8px;font-family:var(--pixel);font-size:10px;align-items:center}
.mini .blocks i{width:8px;height:8px}.mini span:last-child{font-family:var(--mono)}
.links{display:flex;gap:12px;flex-wrap:wrap;font-family:var(--mono);font-size:13px}
.links a::before{content:"open ";color:var(--gold)}
.pick{display:flex;align-items:center;gap:8px;margin-top:auto;font-family:var(--pixel);font-size:12px;cursor:pointer}
.pick input{appearance:none;-webkit-appearance:none;width:22px;height:22px;margin:0;border:2px solid var(--cream);
background:transparent;display:grid;place-items:center;cursor:pointer}
.pick input:checked{background:var(--candy);border-color:var(--candy)}
.pick input:checked::after{content:"x";font-family:var(--pixel);color:var(--ink);font-size:14px}
.pick input:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.foot{margin-top:30px;padding-top:12px;border-top:2px dashed rgba(233,185,73,.55);display:flex;justify-content:space-between;
gap:12px;flex-wrap:wrap;font-family:var(--mono);font-size:13px}
.bar{position:fixed;left:0;right:0;bottom:0;background:var(--wine);color:var(--cream);padding:10px 16px;display:flex;gap:14px;
align-items:center;justify-content:center;flex-wrap:wrap;z-index:5;border-top:2px solid var(--gold)}
.bar b{font-family:var(--mono)}
.bar button{font-family:var(--pixel);font-size:12px;background:var(--candy);color:var(--ink);border:0;border-radius:4px;
padding:9px 14px;cursor:pointer}
.bar button:focus-visible{outline:2px solid var(--cream);outline-offset:3px}
.bar output{font-family:var(--mono);font-size:13px;max-width:60ch;overflow-wrap:anywhere}
.counters{display:flex;gap:12px;flex-wrap:wrap;margin:0 0 22px}
.ctr{border:2px solid var(--gold);padding:8px 12px;min-width:110px}
.ctr b{display:block;font-family:var(--mono);font-weight:500;font-size:26px;color:var(--candy)}
.log{font-family:var(--mono);font-size:14px;line-height:1.55;display:flex;flex-direction:column;gap:14px}
.entry{background:var(--wine);padding:12px 14px;border-left:6px solid var(--gold)}
.entry.due{border-left-color:var(--candy)}
.entry .st{font-family:var(--pixel);font-size:12px;color:var(--gold)}.entry.due .flag{color:var(--candy);font-family:var(--pixel);font-size:12px}
.entry .nm{font-family:var(--label);font-weight:800;font-size:18px;color:var(--cream)}
.entry .meta{opacity:.85}.entry .note{color:var(--candy)}
@media (max-width:520px){.deck{padding:14px;border-width:7px;margin:10px 8px 110px}.term{font-size:13px}}
"""


def _blocks(v: int, n: int = 10) -> str:
    on = round(v / 100 * n)
    return "".join(f'<i class="on"></i>' if k < on else "<i></i>" for k in range(n))


def _keys(band: str, cls: str) -> str:
    word = (band.split() or ["CALL"])[0].upper()
    keys = "".join(f'<span class="key"><b>{T9[c]}</b><small>{T9_LETTERS[T9[c]]}</small></span>' for c in word if c in T9)
    return f'<div class="keys k-{cls}" aria-label="{escape(band)}">{keys}<span class="say">{escape(band.lower())}</span></div>'


def _status(m: dict, style: dict, title: str) -> str:
    heart = pixel_heart(style.get("palette", {}).get("gold", "#E9B949"), 14)
    return (f'<div class="status"><div class="leds"><span class="led"></span><span class="led g"></span>'
            f'<span class="led o"></span><span class="px-lab">{escape(title)} · {escape(m["name"])}</span></div>'
            f'<span class="px-lab">{escape(m["masthead"])} {heart} {escape(m["date"])}</span></div>')


def _panel(c: dict) -> str:
    why = "".join(f"<li>{escape(r)}</li>" for r in c["reasons"])
    mini = "".join(f'<span>{escape(lab)}</span><span class="blocks">{_blocks(v, 10)}</span><span>{v}</span>'
                   for lab, v in c["parts"])
    links = "".join(link(u, lab.lower()) for lab, u in c["links"]) or "<span>no public link in the feed</span>"
    by = f'<div class="by">{escape(c["author"])}</div>' if c["author"] else ""
    return f"""<article class="panel">
<div class="hd px-lab"><span>line {c["i"]:02d}</span><span>{escape(c["slug"][:24])}</span></div>
<div><h2>{escape(c["title"])}</h2>{by}</div>
<div class="blocks" aria-label="Score {c["score"]} out of 100">{_blocks(c["score"])}<b>{c["score"]}</b></div>
{_keys(c["band"], c["cls"])}
<ul class="why">{why}</ul>
<div class="mini">{mini}</div>
<div class="links">{links}</div>
<label class="pick"><input type="checkbox" data-slug="{escape(c["slug"])}" data-title="{escape(c["title"])}"> queue pitch</label>
</article>"""


def shortlist(m: dict, style: dict) -> str:
    l1, l2, l3 = m["invite"]
    invite = "".join(f'<p class="c"># {escape(x)}</p>' for x in (l1, l2, l3) if x)
    panels = "".join(_panel(c) for c in m["cards"]) or '<p class="empty">no lines yet. run discover, then score.</p>'
    body = f"""<div class="deck"><span class="screws"></span>
{_status(m, style, "switchboard")}
<h1>HOTLINE</h1>
<div class="term">
<p><span class="pr">{escape(m["host"])}:~$</span> dial --niche "{escape(m["niche"])}"</p>
<p class="out">{m["n"]} lines found. {m["ring"]} ready to ring today. ranked by fit.</p>
<p class="out">call the girls! tick the lines you want. you press send.</p>
{invite}
<p><span class="pr">{escape(m["host"])}:~$</span> <span class="cursor"></span></p>
</div>
<main class="panels">{panels}</main>
<footer class="foot"><span>every send is yours. nothing goes out on its own.</span><span>Rocha Coded. Free tools from the Rocheverse.</span></footer>
</div>
<div class="bar"><span class="px-lab">queued <b id="picks-n">0</b></span><button id="copy" type="button">copy picks for claude</button>
<output id="picks-out" aria-live="polite"></output></div>
{PICK_JS}"""
    return page("Podcast Hotline", style, CSS, body, True, f' data-run="{escape(m["run_id"])}" data-motif="cyberpunk"')


def tracker(m: dict, style: dict) -> str:
    entries = []
    for r in m["rows"]:
        flag = ' <span class="flag">◆ nudge due</span>' if r["due"] else ""
        note = f'<div class="note">// {escape(r["notes"])}</div>' if r["notes"] else ""
        entries.append(f"""<div class="entry{' due' if r["due"] else ''}"><span class="st">[{escape(r["status"].upper())}]</span>{flag}
<div class="nm">{escape(r["show"])}</div>
<div class="meta">pitched {escape(r["date_pitched"])} · nudges {escape(r["nudges"])}/2 · next {escape(r["next_nudge"])} {link(r["link"], "open")}</div>{note}</div>""")
    log = "".join(entries) or '<p class="empty">no calls logged yet. your first one goes here.</p>'
    ctrs = "".join(f'<div class="ctr px-lab"><b>{v}</b>{escape(k)}</div>' for k, v in m["counts"].items())
    body = f"""<div class="deck"><span class="screws"></span>
{_status(m, style, "call log")}
<h1>CALL LOG</h1>
<div class="term">
<p><span class="pr">{escape(m["host"])}:~$</span> calllog --due</p>
<p class="out">{m["due_n"]} due a nudge today. {m["open_n"]} still waiting. {m["counts"]["booked"]} booked.</p>
<p class="c"># {escape(m["affirm"].lower())}</p>
<p><span class="pr">{escape(m["host"])}:~$</span> <span class="cursor"></span></p>
</div>
<div class="counters">{ctrs}</div>
<main class="log">{log}</main>
<footer class="foot"><span>every send is yours. nothing goes out on its own.</span><span>Rocha Coded. Free tools from the Rocheverse.</span></footer>
</div>"""
    return page("Podcast Call Log", style, CSS, body, True, ' data-motif="cyberpunk"')
