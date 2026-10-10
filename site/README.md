# The static site

The front page, the news and "how to connect" of The Domains of Dread, as a Hugo site with no installed theme. GitHub Pages publishes it from this repository.

| Path | Is |
| --- | --- |
| `hugo.toml` | The settings: title, the five links, the footer notice, and the lines that bring in `../theme` |
| `layouts/` | The templates: the frame of every page, front page, list of posts, post or page, not-found page |
| `assets/css/site.css` | The stylesheet. Colours come from `../theme/tokens.css`, joined in front of it at build time |
| `assets/fonts/` | Noto Serif Medium for headings (SIL Open Font License), cut down to Latin letters |
| `content/` | The pages and posts, in Markdown. What is there now is sample text |

Build with Hugo 0.167.0: `hugo --minify` writes the site to `public/`; `hugo server` shows it at http://localhost:1313.

To remake the font file:

```bash
pyftsubset /usr/share/fonts/noto/NotoSerif-Medium.ttf --unicodes="U+0020-007E,U+00A0-00FF,U+2013,U+2014,U+2018,U+2019,U+201C,U+201D,U+2026" --layout-features='kern,liga,lnum' --flavor=woff2 --output-file=assets/fonts/noto-serif-medium.woff2
```

## Publishing

`../.github/` holds what GitHub runs:

| File | Does |
| --- | --- |
| `.github/workflows/publish.yml` | On every pull request and push: installs the pinned Hugo (checked against its checksum), builds, runs `tools/check_links.py`, checks the front page's weight. On the main branch: publishes to GitHub Pages, and posts a link to Discord for each news post that push added, if a webhook is set |
| `.github/CODEOWNERS` | Who must approve a change |
| `tools/check_links.py` | Every link, picture, stylesheet and font a built page names on the site itself must exist, and no page may carry a script |
