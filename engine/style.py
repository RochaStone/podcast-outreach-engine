"""Shared Rocha Coded style.json loader. Python 3.10+ stdlib only.

One style file styles every Rocha Coded tool. Lookup order:
  1. an explicit --style path
  2. ./style.json (the user's working folder)
  3. ~/.rocha-coded/style.json
  4. the bundled examples/style.rocha-coded.json

Missing palette and font keys are filled from the bundled example. Words are
never inherited: a user's file without a line gets the tool's plain default,
never Rocha's lines. Colours must be hex, font
names must be plain words, so a style file can never inject CSS or markup.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
BUNDLED = KIT / "examples" / "style.rocha-coded.json"
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?$")
FONT_RE = re.compile(r"^[A-Za-z0-9 ]{1,60}$")


def candidates(explicit: str | None = None, cwd: Path | None = None, home: Path | None = None) -> list[Path]:
    out = [Path(explicit)] if explicit else []
    out.append((cwd or Path.cwd()) / "style.json")
    out.append((home or Path.home()) / ".rocha-coded" / "style.json")
    out.append(BUNDLED)
    return out


def _read(p: Path) -> dict | None:
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


INHERITED = ("palette", "fonts")


def _merge(base: dict, over: dict) -> dict:
    """Fill only palette and fonts from the bundled example; everything else is the user's own."""
    out = {k: dict(base.get(k, {})) for k in INHERITED}
    for k, v in over.items():
        if k in INHERITED and isinstance(v, dict):
            out[k].update({kk: vv for kk, vv in v.items() if vv not in (None, "")})
        elif v not in (None, "", [], {}):
            out[k] = v
    return out


def _clean(style: dict, base: dict) -> dict:
    pal = style.get("palette", {})
    style["palette"] = {k: (v if isinstance(v, str) and HEX_RE.match(v) else base["palette"].get(k, "#111111"))
                        for k, v in pal.items()}
    fonts = style.get("fonts", {})
    style["fonts"] = {k: (v if isinstance(v, str) and FONT_RE.match(v) else base["fonts"].get(k, ""))
                      for k, v in fonts.items()}
    return style


def load_style(explicit: str | None = None, cwd: Path | None = None, home: Path | None = None) -> dict:
    """Return the first readable style, merged over the bundled example. Adds '_source'."""
    base = _read(BUNDLED) or {}
    for p in candidates(explicit, cwd, home):
        data = _read(p) if p.is_file() else None
        if data is not None:
            style = _clean(_merge(base, data), base)
            style["_source"] = str(p) if p != BUNDLED else "bundled example (style.rocha-coded.json)"
            return style
    style = dict(base)
    style["_source"] = "bundled example (style.rocha-coded.json)"
    return style


def invite_lines(style: dict, name: str | None = None) -> list[str]:
    """Three lines for the invitation card. --name replaces who you are invited to."""
    lines = style.get("lines", {}) or {}
    inv = lines.get("invite")
    if isinstance(inv, str):  # shared schema: one string, " / " between lines
        inv = [x.strip() for x in inv.split(" / ")]
    if isinstance(inv, list) and len(inv) == 3 and all(isinstance(x, str) for x in inv):
        out = list(inv)
    else:
        owner = style.get("owner") or style.get("name") or ""
        stamp = lines.get("stamp", "")
        out = [f"YOU ARE INVITED TO {owner.upper()}" if owner else "", lines.get("scrawl", ""),
               f"dress code: {stamp.lower()}" if stamp else ""]
    if name and name.strip():
        out[0] = f"YOU ARE INVITED TO {name.strip().upper()}"
    return out  # an empty first line means: no invitation card
