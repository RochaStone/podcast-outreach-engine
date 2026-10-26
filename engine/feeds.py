"""Feed reading for podcast-outreach-engine. Python 3.10+ stdlib only.

Reads a podcast RSS feed and keeps only what helps you decide whether to pitch:
the show's public website, a public "be a guest" page if the feed links one,
the last episode date, how often it publishes, how many episodes it has, and
whether its episode titles look like guest interviews.

Privacy rule: owner email fields (itunes:owner, itunes:email, managingEditor,
webMaster) are never read, and any email address found in a description is
redacted before it is saved. This tool never collects contact details.
"""

from __future__ import annotations

import re
import statistics
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.parse import urlparse

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.I)
TAG_RE = re.compile(r"<[^>]+>")

# Words in a link that suggest a public page for guest requests.
GUEST_LINK_WORDS = (
    "be-a-guest", "beaguest", "be_a_guest", "guest-application", "guest-form",
    "apply-to-be", "become-a-guest", "pitch-the-show", "pitch-us", "pitch",
    "guest", "booking", "apply",
)

# Title patterns that suggest an interview episode.
GUEST_TITLE_PATTERNS = [
    re.compile(r"\b(?i:with)\s+[A-Z][\w'.-]+", re.U),
    re.compile(r"\b(ft|feat|featuring)\b\.?", re.I),
    re.compile(r"\bw/\s*[A-Z]", re.U),
    re.compile(r"\binterview", re.I),
    re.compile(r"\bguest\b", re.I),
    re.compile(r"\bjoined by\b", re.I),
    re.compile(r"\bin conversation\b", re.I),
    re.compile(r"\bmeet\s+[A-Z][a-z]+", re.U),
    # "Ep 12: Jane Doe on pricing" or "Jane Doe: how she built it"
    re.compile(r"(^|[:|\-]\s*)[A-Z][a-z]+(?:\s[A-Z][a-z'-]+){1,2}\s+(on|:)\s", re.U),
    re.compile(r"\|\s*[A-Z][a-z]+\s[A-Z][a-z'-]+\s*$", re.U),
]

ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"


def clean_text(text: str | None, limit: int = 600) -> str:
    """Strip HTML, unescape entities, redact email addresses, collapse space."""
    if not text:
        return ""
    t = unescape(TAG_RE.sub(" ", text))
    t = EMAIL_RE.sub("[email removed]", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:limit]


def normalize_feed_url(url: str | None) -> str:
    """Key used to dedupe the same feed found through two sources."""
    if not url:
        return ""
    u = url.strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    return u.rstrip("/")


def slugify(text: str, max_len: int = 60) -> str:
    s = unescape(text or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s[:max_len].rstrip("-")) or "show"


def safe_url(url: str | None) -> str:
    """Only http(s) URLs survive. Anything else becomes an empty string."""
    if not url:
        return ""
    u = url.strip()
    p = urlparse(u)
    if p.scheme in ("http", "https") and p.netloc:
        return u
    return ""


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    v = value.strip()
    try:
        d = parsedate_to_datetime(v)
    except (TypeError, ValueError, IndexError):
        d = None
    if d is None:
        try:
            d = datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d


def looks_like_guest_episode(title: str) -> bool:
    t = (title or "").strip()
    return any(p.search(t) for p in GUEST_TITLE_PATTERNS)


def guest_ratio(titles: list[str]) -> float | None:
    titles = [t for t in titles if t]
    if not titles:
        return None
    hits = sum(1 for t in titles if looks_like_guest_episode(t))
    return round(hits / len(titles), 2)


def cadence_days(dates: list[datetime]) -> float | None:
    """Median gap in days between the most recent episodes."""
    ds = sorted((d for d in dates if d), reverse=True)[:11]
    if len(ds) < 2:
        return None
    gaps = [(ds[i] - ds[i + 1]).total_seconds() / 86400 for i in range(len(ds) - 1)]
    gaps = [g for g in gaps if g >= 0]
    if not gaps:
        return None
    return round(statistics.median(gaps), 1)


def find_guest_link(website: str, texts: list[str]) -> str:
    """A public guest page linked by the show itself, or an empty string."""
    candidates = []
    for t in texts:
        for m in URL_RE.findall(t or ""):
            candidates.append(m.rstrip(".,;"))
    if website:
        candidates.append(website)
    for word in GUEST_LINK_WORDS:
        for c in candidates:
            path = urlparse(c).path.lower() + "?" + urlparse(c).query.lower()
            if word in path and safe_url(c):
                return c
    return ""


def _local(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _child_text(el, name: str, ns: str | None = None) -> str | None:
    for c in el:
        tag = c.tag
        if ns and tag == f"{{{ns}}}{name}":
            return c.text
        if not ns and _local(tag) == name and "}" not in tag:
            return c.text
    return None


def _parse_with_etree(xml_text: str) -> dict | None:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None
    channel = root.find("channel")
    if channel is None:
        return None
    items = channel.findall("item")
    episodes = []
    for it in items:
        episodes.append({
            "title": (_child_text(it, "title") or "").strip(),
            "date": _child_text(it, "pubDate"),
            "description": _child_text(it, "description") or _child_text(it, "summary", ITUNES_NS) or "",
        })
    # The channel <link> is the show's public website. itunes:owner is skipped on purpose.
    return {
        "title": (_child_text(channel, "title") or "").strip(),
        "website": (_child_text(channel, "link") or "").strip(),
        "description": _child_text(channel, "description") or _child_text(channel, "summary", ITUNES_NS) or "",
        "author": (_child_text(channel, "author", ITUNES_NS) or "").strip(),
        "language": (_child_text(channel, "language") or "").strip(),
        "episodes": episodes,
    }


def _rx_tag(block: str, tag: str) -> str | None:
    m = re.search(rf"<{tag}[^>]*>\s*<!\[CDATA\[([\s\S]*?)\]\]>\s*</{tag}>", block, re.I)
    if m:
        return m.group(1).strip()
    m = re.search(rf"<{tag}[^>]*>([\s\S]*?)</{tag}>", block, re.I)
    return m.group(1).strip() if m else None


def _parse_with_regex(xml_text: str) -> dict:
    """Fallback for feeds that are not well-formed XML."""
    head = xml_text.split("<item", 1)[0]
    episodes = []
    for m in re.finditer(r"<item[\s>]([\s\S]*?)</item>", xml_text, re.I):
        b = m.group(1)
        episodes.append({
            "title": unescape(_rx_tag(b, "title") or "").strip(),
            "date": _rx_tag(b, "pubDate"),
            "description": _rx_tag(b, "description") or "",
        })
    return {
        "title": unescape(_rx_tag(head, "title") or "").strip(),
        "website": (_rx_tag(head, "link") or "").strip(),
        "description": _rx_tag(head, "description") or _rx_tag(head, "itunes:summary") or "",
        "author": unescape(_rx_tag(head, "itunes:author") or "").strip(),
        "language": (_rx_tag(head, "language") or "").strip(),
        "episodes": episodes,
    }


def parse_feed(xml_text: str, max_titles: int = 10) -> dict:
    """Turn RSS text into the facts the scorer needs."""
    raw = _parse_with_etree(xml_text) or _parse_with_regex(xml_text)
    eps = raw["episodes"]
    dated = [(parse_date(e["date"]), e) for e in eps]
    dates = [d for d, _ in dated if d]
    recent = sorted(dated, key=lambda x: x[0] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    titles = [clean_text(e["title"], 200) for _, e in recent[:max_titles]]
    website = safe_url(raw["website"])
    desc = raw["description"] or ""
    link_texts = [desc] + [e["description"] for _, e in recent[:3]]
    return {
        "title": clean_text(raw["title"], 200),
        "author": clean_text(raw["author"], 120),
        "website": website,
        "guest_link": find_guest_link(website, link_texts),
        "description": clean_text(desc),
        "language": raw["language"][:10],
        "episode_count": len(eps),
        "last_episode_date": max(dates).date().isoformat() if dates else None,
        "cadence_days": cadence_days(dates),
        "guest_ratio": guest_ratio(titles),
        "recent_titles": titles,
    }
