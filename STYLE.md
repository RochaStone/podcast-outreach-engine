# Make it yours: style.json

One small file sets the look of your pages: colours, fonts, your name and the lines printed on them.
The same file works across every Rocha Coded tool, so you make it once.

## Where it lives
The tool looks in this order and uses the first one it finds:
1. `style.json` in your podcast folder
2. `~/.rocha-coded/style.json` (one file for every Rocha Coded tool)
3. `examples/style.rocha-coded.json`, the bundled example: Rocha's own look

To start, copy `style.example.json` to `style.json` in your folder and fill it in. Or ask Claude to make one with you.

## The keys
| Key | What it is | Example (Rocha's) |
|---|---|---|
| `name` | The name of your world or studio. Top right of every page | `Rocha Coded` |
| `owner` | Your name. Used on the invitation card when there are no invite lines | `Rocha` |
| `handle` | Your social handle | `@rocheverse` |
| `site` | Your website | `https://thrivingera.com` |
| `palette.hero` | Your main colour: the masthead, score dials, buttons | `#FF2D8A` |
| `palette.accent` | Soft partner to the hero: dial track, handset | `#FFB3D1` |
| `palette.paper` | Card colour | `#F6EFE4` |
| `palette.paper_pink` | Page background | `#FFE1EC` |
| `palette.ink` | Text and outlines | `#111111` |
| `palette.marker` | Scrawled lines and "due" marks | `#E0202E` |
| `palette.plum` | Deep accent: links, shadows | `#4A1033` |
| `palette.gold` | Small sparkle details | `#D4A64A` |
| `palette.cool` | A rare cool accent (other tools use it) | `#BFD4EA` |
| `fonts.masthead` | Big headline font | `Playfair Display` |
| `fonts.label` | Small caps labels | `Archivo Narrow` |
| `fonts.body` | Reading text | `Newsreader` |
| `fonts.scrawl` | Handwriting | `Permanent Marker` |
| `fonts.mono` | Typewriter details | `Courier Prime` |
| `motif` | The look other tools draw in. This tool always uses the rotary phone | `rotary` |
| `lines.masthead` | Top left of the shortlist and call log | `THE ROCHEVERSE TIMES` |
| `lines.scrawl` | Second line of the invitation card | `build your founder world` |
| `lines.stamp` | One word: the "dress code" on the invitation card | `LORE` |
| `lines.affirm` | The scrawled line on the call log | `EVERYTHING WORKS OUT FOR ME` |
| `lines.headline`, `lines.todo`, `lines.celebrate` | Used by other Rocha Coded tools | |
| `lines.invite` | Optional. Exactly three lines for the invitation card, used as written | Rocha's invitation |
| `references` | Images or links Claude looks at when you say "make it mine" | screenshots, a Pinterest board |
| `notes` | Your look in a sentence | `Hot-girl editorial.` |

## Rules
- Colours are hex codes like `#1F6F5C`. Anything else is ignored and the example colour is used.
- Fonts are Google Fonts names. If a font isn't on Google Fonts, the page falls back to a similar system font.
- Your words are only ever yours. If you leave a line blank, the page uses plain wording, never Rocha's.
- Missing colours and fonts fall back to the example, so a half-finished file still looks finished.
- The scoring script's `--name` option changes who the invitation is for, without editing the file.
