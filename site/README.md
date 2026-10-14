# The static site

The front page, the news and "how to connect" of The Domains of Dread, as a Hugo site with no installed theme. GitHub Pages publishes it from this repository.

| Path | Is |
| --- | --- |
| `hugo.toml` | The settings: title, the five links, the footer notice, and the lines that bring in `../theme` |
| `layouts/` | The templates: the frame of every page, front page, list of posts, post or page, not-found page |
| `assets/css/site.css` | The stylesheet. Colours come from `../theme/tokens.css`, joined in front of it at build time |
| `assets/fonts/` | IM Fell English for headings and EB Garamond (roman and italic) for the text (the owner, 14 October 2026), under the SIL Open Font License (the `OFL-*.txt` files), cut down to Latin letters. The same files as the forum's and the wikis' |
| `content/` | The pages and posts, in Markdown. What is there now is sample text |

Build with Hugo 0.167.0: `hugo --minify` writes the site to `public/`; `hugo server` shows it at http://localhost:1313.

To remake the EB Garamond files from the font's own variable files (github.com/google/fonts, `ofl/ebgaramond`), weights 400 to 700:

```bash
U="U+0020-007E,U+00A0-017F,U+01CE,U+2010-2027,U+2030-203A,U+2044,U+20AC,U+2122,U+2190-2193,U+2205,U+2212,U+221E"
fonttools varLib.instancer "EBGaramond[wght].ttf" wght=400:700 -o eb.ttf
pyftsubset eb.ttf --unicodes="$U" --layout-features='kern,liga,calt,ccmp,locl,mark,mkmk,smcp,c2sc,onum,lnum,tnum,pnum,case' --flavor=woff2 --output-file=assets/fonts/eb-garamond.woff2
```

The italic the same way from `EBGaramond-Italic[wght].ttf`. IM Fell English is the forum's file (`phpbb/styles/tdod/theme/fonts/` of the website project).

## Publishing

`../.github/` holds what GitHub runs:

| File | Does |
| --- | --- |
| `.github/workflows/publish.yml` | On every pull request and push: installs the pinned Hugo (checked against its checksum), builds, runs `tools/check_links.py`, checks the front page's weight. On the main branch: publishes to GitHub Pages, and posts a link to Discord for each news post that push added, if a webhook is set |
| `.github/CODEOWNERS` | Who must approve a change |
| `tools/check_links.py` | Every link, picture, stylesheet and font a built page names on the site itself must exist, and no page may carry a script |
