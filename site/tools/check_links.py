#!/usr/bin/env python3
"""Checks a built site: check_links.py PUBLIC_FOLDER

Every link, picture, stylesheet and font a page names on the site itself must exist in the built
folder, and no page may carry a script, except one inline script on the not-found page (404.html),
which sends old wiki addresses on to the wiki because GitHub Pages cannot redirect. robots.txt must
name the sitemap, and the sitemap must list every page but the not-found page, redirect stubs and
the news list's later pages (/news/page/2/...). Links to other sites are listed and not fetched: the build
must not fail because someone else's server is slow.
"""
import html.parser
import os
import re
import sys
import urllib.parse

root = os.path.abspath(sys.argv[1])
problems, outside, pages, listed = [], set(), 0, set()


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.scripts, self.script_files, self.redirect = [], 0, 0, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'script':
            self.scripts += 1
            if a.get('src'):
                self.script_files += 1
        if tag == 'meta' and (a.get('http-equiv') or '').lower() == 'refresh':
            self.redirect = True
        for key in ('href', 'src'):
            if a.get(key):
                self.links.append(a[key])


def exists(page, link):
    u = urllib.parse.urlsplit(link)
    if u.scheme in ('http', 'https') or link.startswith('//'):
        outside.add(link)
        return True
    if u.scheme or not u.path:                         # mailto:, #fragment
        return True
    path = urllib.parse.unquote(u.path)
    target = os.path.join(root, path.lstrip('/')) if path.startswith('/') else os.path.join(os.path.dirname(page), path)
    return os.path.isfile(target) or os.path.isfile(os.path.join(target, 'index.html'))


for folder, _, files in os.walk(root):
    for name in files:
        path = os.path.join(folder, name)
        rel = os.path.relpath(path, root)
        if name.endswith('.html'):
            pages += 1
            p = Page()
            p.feed(open(path, encoding='utf-8').read())
            if rel == '404.html':
                if p.scripts > 1 or p.script_files:
                    problems.append('{}: carries more than its one inline script'.format(rel))
            elif p.scripts:
                problems.append('{}: carries a script'.format(rel))
            if name == 'index.html' and not p.redirect and not re.search(r'(^|/)page/\d+$', os.path.dirname(rel)):   # pager pages are not in Hugo's sitemap
                listed.add('/' + os.path.dirname(rel).replace(os.sep, '/') + ('/' if os.path.dirname(rel) else ''))
            problems += ['{}: nothing at {}'.format(rel, link) for link in p.links if not exists(path, link)]
        elif name.endswith('.css'):
            for link in re.findall(r'url\(\s*["\']?([^"\')]+)', open(path, encoding='utf-8').read()):
                if not link.startswith('data:') and not exists(path, link):
                    problems.append('{}: nothing at {}'.format(rel, link))

robots = os.path.join(root, 'robots.txt')
sitemap = os.path.join(root, 'sitemap.xml')
if not os.path.isfile(robots) or not re.search(r'^Sitemap: https?://\S+/sitemap\.xml$', open(robots, encoding='utf-8').read(), re.M):
    problems.append('robots.txt: no Sitemap: line')
if not os.path.isfile(sitemap):
    problems.append('sitemap.xml: missing')
else:
    in_map = {urllib.parse.urlsplit(u).path for u in re.findall(r'<loc>([^<]+)</loc>', open(sitemap, encoding='utf-8').read())}
    problems += ['sitemap.xml: does not list {}'.format(u) for u in sorted(listed - in_map)]
    problems += ['sitemap.xml: lists {}, which was not built'.format(u) for u in sorted(in_map - listed)]

print('{} pages; {} links to other sites, not fetched'.format(pages, len(outside)))
for p in problems:
    print('  ' + p)
sys.exit(1 if problems else 0)
