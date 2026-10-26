"""Tracker for podcast-outreach-engine. Python 3.10+ stdlib only.

The tracker is a plain markdown table you can edit by hand:

| Show | Date pitched | Status | Nudges | Next nudge | Link | Notes |

Statuses: pitched, nudged, replied, booked, aired, passed.
Nudge rhythm: first nudge 7 days after the pitch, second 10 days after that,
then stop. Two nudges is the ceiling. Replied, booked, aired and passed are
never due: the ball is not in your court.
"""

from __future__ import annotations

import re
from datetime import date, timedelta

COLUMNS = ["Show", "Date pitched", "Status", "Nudges", "Next nudge", "Link", "Notes"]
STATUSES = ("pitched", "nudged", "replied", "booked", "aired", "passed")
OPEN_STATUSES = ("pitched", "nudged")
FIRST_NUDGE_DAYS = 7
SECOND_NUDGE_DAYS = 10
MAX_NUDGES = 2

HEADER = """# Podcast tracker

Edit this table by hand any time. Dates are YYYY-MM-DD.
Statuses: pitched, nudged, replied, booked, aired, passed.

"""


def _parse_date(v: str) -> date | None:
    v = (v or "").strip()
    if not v or v == "-":
        return None
    try:
        return date.fromisoformat(v[:10])
    except ValueError:
        return None


def _cell(v: str) -> str:
    return (v or "").replace("|", "/").replace("\n", " ").strip()


def parse(markdown: str) -> list[dict]:
    rows = []
    header = None
    for line in markdown.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        row = {h: (cells[i] if i < len(cells) else "") for i, h in enumerate(header)}
        rows.append({
            "show": row.get("show", ""),
            "date_pitched": row.get("date pitched", ""),
            "status": (row.get("status", "") or "pitched").lower(),
            "nudges": int(row.get("nudges", "0") or 0) if (row.get("nudges", "0") or "0").isdigit() else 0,
            "next_nudge": row.get("next nudge", ""),
            "link": row.get("link", ""),
            "notes": row.get("notes", ""),
        })
    return rows


def dump(rows: list[dict]) -> str:
    out = [HEADER.rstrip("\n") + "\n", "| " + " | ".join(COLUMNS) + " |", "|" + "|".join(["---"] * len(COLUMNS)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(_cell(str(x)) for x in [
            r["show"], r["date_pitched"], r["status"], r["nudges"], r["next_nudge"] or "-", r["link"], r["notes"],
        ]) + " |")
    return "\n".join(out) + "\n"


def next_nudge_for(status: str, nudges: int, from_day: date) -> str:
    if status not in OPEN_STATUSES or nudges >= MAX_NUDGES:
        return "-"
    days = FIRST_NUDGE_DAYS if nudges == 0 else SECOND_NUDGE_DAYS
    return (from_day + timedelta(days=days)).isoformat()


def find(rows: list[dict], show: str) -> dict | None:
    key = show.strip().lower()
    for r in rows:
        if r["show"].strip().lower() == key:
            return r
    return None


def add(rows: list[dict], show: str, day: date, link: str = "", notes: str = "") -> dict:
    if find(rows, show):
        raise ValueError(f"'{show}' is already in the tracker. Use set to change it.")
    r = {"show": show, "date_pitched": day.isoformat(), "status": "pitched", "nudges": 0,
         "next_nudge": next_nudge_for("pitched", 0, day), "link": link, "notes": notes}
    rows.append(r)
    return r


def set_status(rows: list[dict], show: str, status: str, day: date, notes: str | None = None) -> dict:
    status = status.lower()
    if status not in STATUSES:
        raise ValueError(f"status must be one of: {', '.join(STATUSES)}")
    r = find(rows, show)
    if r is None:
        raise ValueError(f"'{show}' is not in the tracker. Use add first.")
    if status == "nudged":
        r["nudges"] = int(r["nudges"]) + 1
    r["status"] = status
    r["next_nudge"] = next_nudge_for(status, int(r["nudges"]), day)
    if notes:
        r["notes"] = notes
    return r


def due(rows: list[dict], today: date) -> list[dict]:
    out = []
    for r in rows:
        if r["status"] not in OPEN_STATUSES or int(r["nudges"]) >= MAX_NUDGES:
            continue
        d = _parse_date(r["next_nudge"])
        if d and d <= today:
            out.append(r)
    return out
