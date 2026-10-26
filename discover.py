#!/usr/bin/env python3
"""Find podcasts your people listen to. Python 3.10+ stdlib only.

  python3 discover.py --niche "pilates, women's health" --audience "new mums" --country GB --limit 60 --out shows/

Searches the Apple Podcasts directory (no key needed) and, if you add free
Podcast Index keys to .env, the Podcast Index too. Dedupes by feed, reads each
public RSS feed politely, and writes shows/shows.json.

It never collects email addresses or social handles. It keeps the show's public
website and a public "be a guest" page when the feed links one.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine.feeds import clean_text, normalize_feed_url, parse_feed, safe_url, slugify  # noqa: E402

USER_AGENT = "podcast-outreach-engine/1.0 (+https://github.com/RochaStone/podcast-outreach-engine)"
ITUNES_URL = "https://itunes.apple.com/search"
PI_URL = "https://api.podcastindex.org/api/1.0/search/byterm"
MAX_FEED_BYTES = 4_000_000


def load_env(paths: list[Path]) -> None:
    """Read KEY=value lines from the first .env found. Real env vars win."""
    for p in paths:
        if p.is_file():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return


CA_BUNDLES = ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt", "/etc/pki/tls/certs/ca-bundle.crt",
              "/usr/local/etc/openssl/cert.pem", "/opt/homebrew/etc/openssl@3/cert.pem")


def ssl_context() -> ssl.SSLContext:
    """Verified TLS always. Some Python installs ship with no CA certificates, so
    fall back to the operating system's bundle. Verification is never switched off."""
    ctx = ssl.create_default_context()
    if ctx.cert_store_stats().get("x509_ca", 0) > 0:
        return ctx
    try:
        import certifi  # optional, used only if already installed
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass
    for path in CA_BUNDLES:
        if Path(path).is_file():
            return ssl.create_default_context(cafile=path)
    return ctx


SSL_CTX = ssl_context()


def http_get(url: str, headers: dict | None = None, timeout: float = 15, max_bytes: int = 2_000_000) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:  # noqa: S310 (http/https only)
        return resp.read(max_bytes)


def terms_from(niche: str, audience: str) -> list[str]:
    n = [t.strip() for t in niche.split(",") if t.strip()]
    a = [t.strip() for t in audience.split(",") if t.strip()]
    terms = list(n)
    for x in a:
        terms.append(x)
        if n:
            terms.append(f"{n[0]} {x}")
    seen, out = set(), []
    for t in terms:
        if t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out


def search_itunes(term: str, country: str, limit: int, timeout: float) -> list[dict]:
    q = urllib.parse.urlencode({"media": "podcast", "entity": "podcast", "term": term,
                                "country": country, "limit": min(200, max(1, limit))})
    data = json.loads(http_get(f"{ITUNES_URL}?{q}", timeout=timeout).decode("utf-8", "replace"))
    out = []
    for r in data.get("results", []):
        feed = safe_url(r.get("feedUrl"))
        if not feed:
            continue
        out.append({
            "title": clean_text(r.get("collectionName") or r.get("trackName"), 200),
            "author": clean_text(r.get("artistName"), 120),
            "feed_url": feed,
            "apple_url": safe_url(r.get("collectionViewUrl")),
            "genres": [g for g in (r.get("genres") or []) if g and g != "Podcasts"][:5],
            "episode_count": r.get("trackCount"),
            "last_episode_date": (r.get("releaseDate") or "")[:10] or None,
            "country": r.get("country", ""),
            "sources": ["apple"],
            "found_by": [term],
        })
    return out


def podcastindex_headers(key: str, secret: str) -> dict:
    """Auth per podcastindex-org docs: sha1(key + secret + unix time)."""
    epoch = str(int(time.time()))
    digest = hashlib.sha1((key + secret + epoch).encode("utf-8")).hexdigest()  # noqa: S324 (their scheme)
    return {"X-Auth-Key": key, "X-Auth-Date": epoch, "Authorization": digest}


def search_podcastindex(term: str, limit: int, key: str, secret: str, timeout: float) -> list[dict]:
    q = urllib.parse.urlencode({"q": term, "max": min(100, max(1, limit)), "clean": "1"})
    data = json.loads(http_get(f"{PI_URL}?{q}", headers=podcastindex_headers(key, secret), timeout=timeout)
                      .decode("utf-8", "replace"))
    out = []
    for f in data.get("feeds", []) or []:
        if f.get("dead"):
            continue
        feed = safe_url(f.get("url") or f.get("originalUrl"))
        if not feed:
            continue
        newest = f.get("newestItemPubdate") or f.get("lastUpdateTime")
        out.append({
            "title": clean_text(f.get("title"), 200),
            "author": clean_text(f.get("author"), 120),
            "feed_url": feed,
            "website": safe_url(f.get("link")),
            "genres": [c for c in (f.get("categories") or {}).values() if c][:5],
            "episode_count": f.get("episodeCount"),
            "last_episode_date": datetime.fromtimestamp(newest, timezone.utc).date().isoformat() if newest else None,
            "language": f.get("language", ""),
            "sources": ["podcastindex"],
            "found_by": [term],
        })
    return out


def merge(into: dict[str, dict], show: dict) -> None:
    key = normalize_feed_url(show["feed_url"])
    if key not in into:
        into[key] = show
        return
    cur = into[key]
    for k, v in show.items():
        if k in ("sources", "found_by"):
            cur[k] = sorted(set(cur.get(k, [])) | set(v))
        elif not cur.get(k) and v:
            cur[k] = v


def enrich_from_feed(show: dict, timeout: float) -> None:
    try:
        raw = http_get(show["feed_url"], headers={"Accept": "application/rss+xml, application/xml, text/xml"},
                       timeout=timeout, max_bytes=MAX_FEED_BYTES)
        facts = parse_feed(raw.decode("utf-8", "replace"))
    except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError, OSError) as e:
        show["feed_ok"] = False
        show["feed_error"] = type(e).__name__
        return
    show["feed_ok"] = True
    for k in ("website", "guest_link", "description", "language", "cadence_days", "guest_ratio", "recent_titles"):
        if facts.get(k) not in (None, "", []):
            show[k] = facts[k]
    if facts.get("episode_count"):
        show["episode_count"] = max(int(show.get("episode_count") or 0), facts["episode_count"])
    if facts.get("last_episode_date"):
        show["last_episode_date"] = max(filter(None, [show.get("last_episode_date"), facts["last_episode_date"]]))
    if not show.get("author") and facts.get("author"):
        show["author"] = facts["author"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Find podcasts for your guest profile.")
    ap.add_argument("--niche", required=True, help="comma-separated topics, e.g. 'pilates, women's health'")
    ap.add_argument("--audience", default="", help="comma-separated listener words, e.g. 'new mums, over 40'")
    ap.add_argument("--country", default="US", help="two-letter store country, e.g. US, GB, AU")
    ap.add_argument("--limit", type=int, default=60, help="max shows to keep (default 60)")
    ap.add_argument("--out", default="shows", help="output folder (default shows/)")
    ap.add_argument("--env", default=None, help="path to a .env file (default ./.env)")
    ap.add_argument("--no-feeds", action="store_true", help="skip reading RSS feeds (faster, less accurate)")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--delay", type=float, default=0.6, help="seconds between requests, to be polite")
    a = ap.parse_args(argv)

    load_env([Path(a.env)] if a.env else [Path.cwd() / ".env"])
    pi_key, pi_secret = os.environ.get("PODCASTINDEX_KEY", ""), os.environ.get("PODCASTINDEX_SECRET", "")
    country = a.country.strip().upper()[:2] or "US"
    terms = terms_from(a.niche, a.audience)
    per_term = max(10, min(50, a.limit))

    found: dict[str, dict] = {}
    errors: list[str] = []
    for t in terms:
        try:
            for s in search_itunes(t, country, per_term, a.timeout):
                merge(found, s)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            errors.append(f"apple '{t}': {type(e).__name__} {getattr(e, 'reason', '')}".strip())
        time.sleep(a.delay)
        if pi_key and pi_secret:
            try:
                for s in search_podcastindex(t, per_term, pi_key, pi_secret, a.timeout):
                    merge(found, s)
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
                errors.append(f"podcastindex '{t}': {type(e).__name__}")
            time.sleep(a.delay)

    shows = list(found.values())
    # Shows found by more searches first, then the ones with more episodes.
    shows.sort(key=lambda s: (-len(s.get("found_by", [])), -(s.get("episode_count") or 0)))
    shows = shows[: a.limit]

    if not a.no_feeds:
        for i, s in enumerate(shows, 1):
            print(f"  reading feed {i}/{len(shows)}: {s['title'][:60]}", file=sys.stderr)
            enrich_from_feed(s, a.timeout)
            time.sleep(a.delay)

    used = set()
    for s in shows:
        base = slugify(s.get("title", "show"))
        slug, n = base, 2
        while slug in used:
            slug, n = f"{base}-{n}", n + 1
        used.add(slug)
        s["slug"] = slug

    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "query": {"niche": a.niche, "audience": a.audience, "country": country, "terms": terms},
        "sources": ["apple"] + (["podcastindex"] if pi_key and pi_secret else []),
        "errors": errors,
        "shows": shows,
    }
    (out_dir / "shows.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Found {len(shows)} shows from {len(terms)} searches. Saved {out_dir / 'shows.json'}")
    if errors:
        print(f"{len(errors)} searches failed: " + "; ".join(errors[:5]), file=sys.stderr)
        if any("SSL" in e or "Certificate" in e for e in errors):
            print("Python could not check website certificates. On a Mac with Python from python.org, open\n"
                  "Applications > Python 3.x > Install Certificates.command once, then run this again.", file=sys.stderr)
    return 0 if shows or not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
