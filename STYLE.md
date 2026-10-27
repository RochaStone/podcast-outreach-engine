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
| `palette.hero` | Your GROUND colour: the masthead band, rank tabs, score bars, the phone body | `#50163C` |
| `palette.accent` | Your one accent: pills, score dials, the copy button | `#FE9DCA` |
| `palette.paper` | Page and card colour | `#FFF7F4` |
| `palette.paper_pink` | Call log slips, dial tracks | `#FFE3F1` |
| `palette.ink` | Text and outlines | `#3B1230` |
| `palette.marker` | The script line on cream | `#C2246E` |
| `palette.plum` | Deep accent (other tools use it) | `#50163C` |
| `palette.wine` | Text on cream for invitations and links | `#682047` |
| `palette.gold` | Hairlines, the dial ring, the phone details | `#E9B949` |
| `palette.cool` | Alternate pill fill ("worth a ring") | `#B9B3F5` |
| `fonts.masthead` | Big headline font | `Fraunces` |
| `fonts.label` | Labels and buttons | `Bricolage Grotesque` |
| `fonts.body` | Reading text | `Fraunces` |
| `fonts.script` | One signature script line per page | `Pinyon Script` |
| `fonts.scrawl` | Hand marker (other tools use it) | `Permanent Marker` |
| `fonts.mono` | Numbers and dates | `DM Mono` |
| `motif` | The look other tools draw in. This tool always uses the rotary phone | `guest-check` |
| `lines.masthead` | Top left of the shortlist and call log | `THE ROCHEVERSE TIMES` |
| `lines.scrawl` | Second line of the invitation card | `build your founder world` |
| `lines.stamp` | One word: the "dress code" on the invitation card | `LORE` |
| `lines.affirm` | The scrawled line on the call log | `EVERYTHING WORKS OUT FOR ME` |
| `lines.headline`, `lines.todo`, `lines.celebrate` | Used by other Rocha Coded tools | |
| `lines.invite` | Optional. The invitation card as one line, with " / " between its three parts, used as written | `YOU ARE INVITED TO THE ROCHEVERSE / come build your founder world / dress code: lore` |
| `references` | Images or links Claude looks at when you say "make it mine" | screenshots, a Pinterest board |
| `notes` | Your look in a sentence | `Editorial and certain, leaning dark.` |

## Rules
- Colours are hex codes like `#1F6F5C`. Anything else is ignored and the example colour is used.
- Fonts are Google Fonts names. If a font isn't on Google Fonts, the page falls back to a similar system font.
- Your words are only ever yours. If you leave a line blank, the page uses plain wording, never Rocha's.
- Missing colours and fonts fall back to the example, so a half-finished file still looks finished.
- The scoring script's `--name` option changes who the invitation is for, without editing the file.
