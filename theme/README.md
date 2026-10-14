# The site's look

Decided by the owner on 8 October 2026: black primary, white secondary, wine red for accents such as links, in the manner of the early second-edition printed books. Always dark. The logo is the Two Ds: a white roman capital D with a wine-red one behind it like a shadow.

| File | Is |
| --- | --- |
| `tokens.css` | The colours, once, with the reason for each. Every part of the site takes them from here |
| `logo/tdod-mark.svg` | The mark alone, for black and other dark grounds. The space between the letters is cut out |
| `logo/tdod-icon.svg`, `logo/favicon.ico`, `logo/apple-touch-icon.png`, `logo/tdod-icon-*.png` | The mark on its own black square, for browser tabs and home screens |
| `logo/tdod-lockup.svg`, `logo/tdod-lockup-stacked.svg` | The mark with the site's name, in one line and in two |
| `logo/build.py` | Draws all of the above from one description of the mark. Change the mark there and run it |
| `logo/sketches/` | The sketches the logo was chosen from |
| `logo/choices.html` | The page the owner chose on (a private artifact) |
| `../mediawiki/theme/` | The colours and the logo as the wikis' Citizen theme: two wiki pages and the lines for `LocalSettings.php` |

The letter D of the mark is drawn in `build.py`, not taken from a font. The name beside it is set in IM Fell English (SIL Open Font License), the headings' face, and stored as outlines; it was Noto Serif Medium until 14 October 2026.

The same colours and logo are applied in two more places, both built from `tokens.css`:

| Where | Is |
| --- | --- |
| `../site/` | The static site: a Hugo site whose stylesheet is `assets/css/site.css` |
| `../phpbb/styles/tdod/` | The forum style: prosilver turned dark by `build.py`, with the logo and the five links |

Change a colour in `tokens.css`, then build the static site again and run the forum style's `build.py`.
