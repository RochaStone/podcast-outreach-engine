#!/usr/bin/env python3
"""Makes every image in the README from the tool itself. Python 3.10+ stdlib and headless Chrome.

  python3 scripts/make-readme-images.py

- docs/img/hero-y2k.png   the fictional example shortlist in the y2k-blog skin (hotline.exe)
- docs/img/triptych.png   the same shortlist in analog | cyberpunk | y2k-blog, side by side
- docs/img/step-01..05.svg, divider.svg, heart.svg   tiny pixel badges and rules for the README

Chrome is found at the usual Mac path, on PATH (google-chrome, chromium), or from the CHROME variable.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT))

from engine.common import pixel_heart  # noqa: E402
from engine.render import MOTIFS, shortlist_html  # noqa: E402
from engine.scoring import parse_profile, score_all  # noqa: E402
from engine.style import BUNDLED, load_style  # noqa: E402

IMG = KIT / "docs" / "img"
DIGITS = {"0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111",
          "4": "101101111001001", "5": "111100111001111"}


def find_chrome() -> str:
    cands = [os.environ.get("CHROME", ""), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             shutil.which("google-chrome") or "", shutil.which("chromium") or "", shutil.which("chromium-browser") or ""]
    for c in cands:
        if c and Path(c).exists():
            return c
    sys.exit("Headless Chrome was not found. Install Google Chrome, or set CHROME to its path.")


def shoot(chrome: str, url: str, out: Path, w: int, h: int) -> None:
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    "--virtual-time-budget=6000", f"--window-size={w},{h}", f"--screenshot={out}", url],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)


def badge(n: str, ground: str, cream: str) -> str:
    rects = []
    for k, ch in enumerate(n):
        bits = DIGITS[ch]
        for i, b in enumerate(bits):
            if b == "1":
                rects.append(f'<rect x="{2 + k * 5 + i % 3}" y="{2 + i // 3}" width="1" height="1"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 13 9" width="39" height="27" shape-rendering="crispEdges">'
            f'<title>step {n}</title><rect width="13" height="9" fill="{ground}"/><g fill="{cream}">{"".join(rects)}</g></svg>\n')


def divider(gold: str) -> str:
    dots = "".join(f'<rect x="{x}" y="0" width="2" height="1"/>' for x in range(0, 160, 4))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 1" width="480" height="3" shape-rendering="crispEdges">'
            f'<g fill="{gold}">{dots}</g></svg>\n')


def main() -> int:
    chrome = find_chrome()
    style = load_style(str(BUNDLED))
    pal = style["palette"]
    shows = json.loads((KIT / "tests" / "fixtures" / "shows.json").read_text(encoding="utf-8"))["shows"]
    profile = parse_profile((KIT / "examples" / "guest-profile.md").read_text(encoding="utf-8"))
    scored = score_all(shows, profile, date(2026, 10, 26))
    meta = {"date": "2026-10-26", "niche": "postnatal running"}
    IMG.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        for m in MOTIFS:
            (t / f"{m}.html").write_text(shortlist_html(scored, meta, style, m), encoding="utf-8")
        shoot(chrome, (t / "y2k-blog.html").as_uri(), IMG / "hero-y2k.png", 1240, 1300)
        cells = "".join(
            f'<figure><div class="f"><iframe src="{m}.html" scrolling="no"></iframe></div><figcaption>{m}</figcaption></figure>'
            for m in MOTIFS)
        (t / "triptych.html").write_text(f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Silkscreen&display=swap">
<style>body{{margin:0;background:{pal['paper']};display:flex;gap:16px;padding:16px;font-family:Silkscreen,monospace}}
figure{{margin:0;width:400px}}.f{{width:400px;height:520px;overflow:hidden;border:1.5px solid {pal['ink']}}}
iframe{{width:1240px;height:1612px;border:0;transform:scale(.3226);transform-origin:0 0}}
figcaption{{text-align:center;color:{pal['ink']};font-size:14px;padding-top:8px;text-transform:uppercase}}</style></head>
<body>{cells}</body></html>""", encoding="utf-8")
        shoot(chrome, (t / "triptych.html").as_uri(), IMG / "triptych.png", 1248, 590)

    for i in range(1, 6):
        (IMG / f"step-0{i}.svg").write_text(badge(f"0{i}", pal["hero"], pal["paper"]), encoding="utf-8")
    (IMG / "divider.svg").write_text(divider(pal["gold"]), encoding="utf-8")
    heart = pixel_heart(pal["gold"], 18).replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    (IMG / "heart.svg").write_text(heart + "\n", encoding="utf-8")
    for p in sorted(IMG.iterdir()):
        print(f"  {p.relative_to(KIT)}  {p.stat().st_size // 1024 or 1} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
