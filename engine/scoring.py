"""Scoring for podcast-outreach-engine. Python 3.10+ stdlib only.

Each show gets five sub-scores from 0 to 100, a weighted total, and plain
reasons. Ideas carried over from an earlier private build: the recency ladder,
weights that must add up to one, and keyword matching against the show's own
words. Everything here is rewritten around the guest profile, so the scoring
is about you, never about the person who wrote it.
"""

from __future__ import annotations

import re
from datetime import date, datetime

WEIGHTS = {
    "fit": 0.35,       # their words overlap with who you help and what changes
    "recency": 0.20,   # still publishing
    "guests": 0.20,    # interviews guests at all
    "size": 0.15,      # episode count as a staying-power proxy
    "cadence": 0.10,   # how often they publish
}
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "weights must add up to 1"

REFUSE_PENALTY = 40
REFUSE_CAP = 35      # a show built on a topic you refuse never ranks above "Maybe later"
SOLO_CAP = 50        # titles that look solo: guests may be rare
LOVE_BONUS = 10
THIN_FIT = 50        # below this fit, the total is scaled down so format alone can't carry a show

STOPWORDS = set("""
a about above after again against all also am an and any are as at be because been before being below between both
but by can could did do does doing down during each few for from further get gets got had has have having he her here
hers herself him himself his how i if in into is it its itself just like make makes me more most my myself no nor not
now of off on once only or other our ours ourselves out over own really same she should so some such than that the their
theirs them themselves then there these they this those through to too under until up very was we were what when where
which while who whom why will with would you your yours yourself yourselves want wants help helps people things thing
them every one two three them who's they're i'm i've don't it's way ways get getting go going able
without within again back body years year time times first last next new week weeks day days life still
know need needs feel feels good great best better start started being after before ever never much many
""".split())
# "new" is generic alone but meaningful in a phrase like "new mums", which bigrams keep.

BIGRAM_OK = {"new", "first", "after", "back", "body", "life"}

SECTION_KEYS = {
    "who you are": "who",
    "who you help": "help",
    "what changes for them": "changes",
    "three stories you can tell": "stories",
    "one thing you want listeners to do": "cta",
    "shows you already love": "love",
    "topics you refuse": "refuse",
    "proof you can show": "proof",
    "how you like to be introduced": "intro",
    "where listeners can find you": "find",
}


def parse_profile(markdown: str) -> dict:
    """Read guest-profile.md into a dict keyed by section. Comments are ignored."""
    text = re.sub(r"<!--[\s\S]*?-->", "", markdown)
    out = {v: "" for v in SECTION_KEYS.values()}
    current = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(?:\d+\.\s*)?(.+?)\s*$", line)
        if m:
            heading = m.group(1).strip().lower()
            current = next((v for k, v in SECTION_KEYS.items() if heading.startswith(k)), None)
            continue
        if current:
            out[current] += line + "\n"
    return {k: v.strip() for k, v in out.items()}


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z][a-z'-]{2,}", (text or "").lower())


def _content_words(text: str) -> list[str]:
    return [w.strip("'-") for w in _words(text) if w.strip("'-") not in STOPWORDS or w.strip("'-") in BIGRAM_OK]


def keywords(text: str) -> tuple[set[str], set[str]]:
    """Meaningful single words and two-word phrases from profile text.
    Phrases skip small words, so "return to running" becomes "return running"."""
    ws = _content_words(text)
    uni = {w for w in ws if w not in STOPWORDS and len(w) > 3}
    bi = {f"{a} {b}" for a, b in zip(ws, ws[1:]) if b not in STOPWORDS and _stem(a) != _stem(b)}
    return uni, bi


def _stem(w: str) -> str:
    """Tiny suffix trim, enough for running/runners/run and coach/coaching."""
    for suf in ("ing", "ers", "er", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            w = w[: -len(suf)]
            if len(w) > 3 and w[-1] == w[-2] and w[-1] not in "aeiouls":
                w = w[:-1]
            return w
    return w


def _list_items(text: str) -> list[str]:
    items = []
    for line in (text or "").splitlines():
        line = re.sub(r"^\s*[-*\d.)]+\s*", "", line).strip()
        if line:
            items.extend(p.strip() for p in re.split(r"[,;]", line) if p.strip())
    return items


def show_corpus(show: dict) -> str:
    parts = [show.get("title", ""), show.get("description", ""), " ".join(show.get("genres", []) or []),
             " ".join(show.get("recent_titles", []) or [])]
    return " ".join(parts).lower()


def score_fit(profile: dict, show: dict) -> tuple[int, list[str]]:
    uni, bi = keywords(" ".join([profile.get("help", ""), profile.get("changes", ""), profile.get("who", "")]))
    corpus = show_corpus(show)
    corpus_stems = {_stem(w.strip("'-")) for w in _words(corpus)}
    cw = [_stem(w) for w in _content_words(corpus)]
    corpus_bi = {f"{a} {b}" for a, b in zip(cw, cw[1:])}
    bi_hits = sorted(p for p in bi if " ".join(_stem(x) for x in p.split()) in corpus_bi)
    uni_hits, seen = [], set()
    for w in sorted(uni, key=len):
        st = _stem(w)
        if st in corpus_stems and st not in seen:
            seen.add(st)
            uni_hits.append(w)
    uni_hits.sort()
    points = len(bi_hits) * 20 + len(uni_hits) * 12
    return min(100, points), bi_hits + [w for w in uni_hits if not any(w in p for p in bi_hits)]


def score_recency(last_episode: str | None, today: date) -> int:
    if not last_episode:
        return 0
    try:
        d = datetime.fromisoformat(last_episode[:10]).date()
    except ValueError:
        return 0
    days = (today - d).days
    if days <= 7:
        return 100
    if days <= 14:
        return 85
    if days <= 30:
        return 70
    if days <= 60:
        return 50
    if days <= 90:
        return 30
    return 0


def score_cadence(cadence: float | None) -> int:
    if cadence is None:
        return 30
    if cadence <= 8:
        return 100
    if cadence <= 16:
        return 80
    if cadence <= 35:
        return 60
    if cadence <= 70:
        return 35
    return 15


def score_guests(ratio: float | None) -> int:
    if ratio is None:
        return 30
    return min(100, round(ratio / 0.6 * 100))


def score_size(episodes: int | None) -> int:
    """Episode count as a proxy. Big enough to last, small enough to say yes."""
    n = episodes or 0
    if n < 10:
        return 20
    if n < 50:
        return 70
    if n < 200:
        return 100
    if n < 500:
        return 85
    return 60


def _matches_any(items: list[str], corpus: str) -> list[str]:
    hits = []
    for item in items:
        words = [w for w in _words(item) if w not in STOPWORDS]
        if words and all(re.search(rf"\b{re.escape(w)}", corpus) for w in words):
            hits.append(item)
    return hits


def score_show(show: dict, profile: dict, today: date) -> dict:
    fit, fit_terms = score_fit(profile, show)
    parts = {
        "fit": fit,
        "recency": score_recency(show.get("last_episode_date"), today),
        "guests": score_guests(show.get("guest_ratio")),
        "size": score_size(show.get("episode_count")),
        "cadence": score_cadence(show.get("cadence_days")),
    }
    total = sum(parts[k] * w for k, w in WEIGHTS.items())
    if fit < THIN_FIT:
        total *= 0.6 + 0.4 * fit / THIN_FIT
    reasons = []
    if fit_terms and fit >= THIN_FIT:
        reasons.append("They talk about " + ", ".join(fit_terms[:5]) + ", which is who you help.")
    elif fit_terms:
        reasons.append("Light overlap: " + ", ".join(fit_terms[:3]) + ". Listen to one episode first.")
    else:
        reasons.append("No clear overlap with who you help. Check it before you pitch.")
    if parts["recency"] >= 70:
        reasons.append(f"Fresh episode on {show.get('last_episode_date')}.")
    elif parts["recency"] > 0:
        reasons.append(f"Last episode {show.get('last_episode_date')}, still inside 90 days.")
    else:
        reasons.append("Nothing new in 90 days, it may be resting.")
    r = show.get("guest_ratio")
    if r is not None:
        if r >= 0.5:
            reasons.append(f"Guest show: about {round(r * 100)}% of recent titles are interviews.")
        elif r > 0:
            reasons.append(f"Some guests: about {round(r * 100)}% of recent titles are interviews.")
        else:
            reasons.append("Recent titles look solo, guests may be rare.")
            total = min(total, SOLO_CAP)
    c = show.get("cadence_days")
    if c:
        label = "daily" if c <= 2 else "weekly" if c <= 8 else "fortnightly" if c <= 16 else "monthly" if c <= 35 else "occasional"
        reasons.append(f"Publishes {label}, {show.get('episode_count') or 0} episodes so far.")

    love_hits = _matches_any(_list_items(profile.get("love", "")), (show.get("title") or "").lower())
    if love_hits:
        total += LOVE_BONUS
        reasons.insert(0, "On your love list.")
    refuse_hits = _matches_any(_list_items(profile.get("refuse", "")), show_corpus(show))
    if refuse_hits:
        total = min(total - REFUSE_PENALTY, REFUSE_CAP)
        reasons.append("Touches " + ", ".join(refuse_hits[:3]) + ", which you said no to.")

    score = max(0, min(100, round(total)))
    return {
        **show,
        "score": score,
        "parts": parts,
        "reasons": reasons,
        "refuse_hits": refuse_hits,
        "active_90_days": parts["recency"] > 0,
        "band": band(score),
    }


def band(score: int) -> str:
    if score >= 75:
        return "Ring today"
    if score >= 55:
        return "Worth a ring"
    return "Maybe later"


def score_all(shows: list[dict], profile: dict, today: date) -> list[dict]:
    scored = [score_show(s, profile, today) for s in shows]
    scored.sort(key=lambda s: (-s["score"], s.get("title", "").lower()))
    return scored
