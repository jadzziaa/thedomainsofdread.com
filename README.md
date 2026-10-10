# The Domains of Dread: the website's front page

The static site at [thedomainsofdread.com](https://thedomainsofdread.com/): the front page, the news, and how to connect. The [forum](https://forum.thedomainsofdread.com/) and the [wiki](https://wiki.thedomainsofdread.com/) are separate.

| Folder | Holds |
| --- | --- |
| `site/` | The Hugo site: `content/` is the pages and posts in Markdown, `layouts/` the templates, `assets/` the stylesheet and the heading font. See `site/README.md` |
| `theme/` | The colours (`tokens.css`) and the logo, which the forum and the wikis use too. See `theme/README.md` |
| `.github/` | The workflow that builds and publishes, and who must approve a change |

## To post news

Add a Markdown file to `site/content/news/`, named with its date, like `2026-10-10-the-site-opens.md`, with a title, date, author and one-line description at the top as the existing posts have. Open a pull request; the site is built and checked, and merging publishes it within a few minutes.

## To build it yourself

Hugo 0.167.0 (the version is pinned in the workflow):

```bash
hugo server --source site
```

The Domains of Dread is unofficial Fan Content permitted under the Fan Content Policy. Not approved/endorsed by Wizards. Portions of the materials used are property of Wizards of the Coast. ©Wizards of the Coast LLC.
