#!/usr/bin/env python3
"""Checks a built site: check_links.py PUBLIC_FOLDER

Every link, picture, stylesheet and font a page names on the site itself must exist in the built
folder, and no page may carry a script. Links to other sites are listed and not fetched: the build
must not fail because someone else's server is slow.
"""
import html.parser
import os
import re
import sys
import urllib.parse

root = os.path.abspath(sys.argv[1])
problems, outside, pages = [], set(), 0


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.scripts = [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'script':
            self.scripts += 1
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
            if p.scripts:
                problems.append('{}: carries a script'.format(rel))
            problems += ['{}: nothing at {}'.format(rel, link) for link in p.links if not exists(path, link)]
        elif name.endswith('.css'):
            for link in re.findall(r'url\(\s*["\']?([^"\')]+)', open(path, encoding='utf-8').read()):
                if not link.startswith('data:') and not exists(path, link):
                    problems.append('{}: nothing at {}'.format(rel, link))

print('{} pages; {} links to other sites, not fetched'.format(pages, len(outside)))
for p in problems:
    print('  ' + p)
sys.exit(1 if problems else 0)
