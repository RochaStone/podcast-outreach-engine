# Testing

Run everything from the kit folder:

```sh
python3 -m unittest -v
```

## What the tests cover
- **Feed reading** (`tests/test_feeds.py`): a fixture RSS feed is parsed for title, website, last episode, cadence,
  episode count and guest ratio. Owner and editor email fields are never kept, and email addresses in descriptions
  are redacted. Broken XML falls back to a forgiving parser. The guest-title heuristic is checked on real-style titles.
- **Scoring** (`tests/test_scoring.py`): profile parsing, fit by keyword and phrase overlap, the recency ladder,
  guest format, size and cadence bands, the solo-show cap, the love-list lift and the refused-topic cap.
- **Tracker** (`tests/test_tracker.py`): first nudge at 7 days, second at 10 more, stop at two, closed statuses never
  due, markdown round trip and hand edits. Rendered pages escape feed text and drop non-http links.
- **Style** (`tests/test_style.py`): the style.json lookup order, broken files falling through, bad colours and
  font names rejected, Rocha's words never inherited into another style, and a second style changing the shortlist
  masthead text, the hero colour, the fonts and the invitation card, plus the call log.
- **Looks** (`tests/test_motifs.py`): the shortlist and the call log in analog, cyberpunk and y2k-blog, each with its
  signature (the rotary phone, the terminal prompt and keypad, the hotline.exe window and hit counter, the guestbook),
  the same facts in every look, escaping in every look, no glow, the pixel font only where it belongs, motif aliases,
  and the --motif override.
- **Discovery** (`tests/test_discover_live.py`): search terms, dedupe across sources, the Podcast Index auth header
  shape, and one live Apple Podcasts query that is skipped automatically when the network is unavailable.

## Results, 26 Oct 2026 (macOS, Python 3.12.8)
- `python3 -m unittest`: 56 tests, all passed. The live Apple Podcasts query ran and passed (not skipped).
- Live end to end: `discover.py --niche "postnatal running, postpartum fitness" --audience "new mums" --country GB
  --limit 25` found 25 real shows from 4 searches in 72 seconds, read all 25 feeds, stored zero email addresses.
  `score.py` ranked them with the fictional example profile and drew the shortlist page.
- None of the 25 real feeds linked a "be a guest" page, so cards fell back to the show website. Expect this often.
- All three looks were rendered with headless Chrome and checked by eye at desktop width and at 390px phone width
  (inside a 390px frame, since headless Chrome will not open a window that narrow). `scripts/make-readme-images.py`
  makes the README pictures.

## Not tested
- **Podcast Index search** with real keys. The auth header follows their published scheme and the request shape
  matches their docs, but no live call was made.
- **Claude Cowork.** The skill was not run inside a Cowork sandbox. Network access there depends on the user's settings.
- **Gmail or Outlook drafts.** The skill tells Claude to create drafts only; no connector was exercised.
- **Windows.** Untested. The scripts are standard library Python and should run.

## A known Mac quirk
Python installed from python.org can ship without certificates, which makes every web request fail. `discover.py`
falls back to the system certificate bundle (verification stays on) and, if that also fails, tells the user to run
Applications > Python 3.x > Install Certificates.command once. This was hit and fixed during testing.
