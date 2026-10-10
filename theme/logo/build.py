#!/usr/bin/env python3
"""Draw the site's logo files from one description of the mark.

  build.py            writes the SVGs, PNGs and favicon.ico beside this script

The mark is the Two Ds: a white roman capital D with a wine-red one behind it and below, like
a shadow. The owner chose it on 8 October 2026, with the lifted wine red. The letter is drawn
here, not taken from a font. The site's name beside it is set in Noto Serif Medium (Open Font
License) and turned into outlines, so the files need no font where they are shown.

Needs fontTools, rsvg-convert and ImageMagick, and Noto Serif installed.
"""
import os
import subprocess

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
WHITE, WINE, BLACK = '#ffffff', '#a12d40', '#000000'
FONT = '/usr/share/fonts/noto/NotoSerif-Medium.ttf'

# A roman capital D on a 100-unit square: bracketed serifs on the stem, a bowl thin where it
# joins the stem and full at its side.
D_OUT = 'M6 10H46C72 10 90 27 90 50S72 90 46 90H6V85C11 85 14 83 14 79V21C14 17 11 15 6 15Z'
D_IN = 'M29 16V84H44C62 84 74 70 74 50S62 16 44 16Z'
SCALE = 0.46                      # the letter's size inside the 64-unit mark
FRONT = (1.7, 3.0)                # where the white letter sits
BACK = (18.2, 15.0)               # where the wine one sits
GAP = 5.0                         # the clear space kept round the white letter, in mark units


def mark(prefix=''):
    """The mark's drawing, 64 units square, on no ground: the gap is cut out of the wine letter."""
    place = lambda at: 'translate({} {}) scale({})'.format(at[0], at[1], SCALE)
    return ('<defs><mask id="{p}gap" maskUnits="userSpaceOnUse" x="0" y="0" width="64" height="64">'
            '<rect width="64" height="64" fill="#fff"/>'
            '<path transform="{f}" d="{o}" fill="#000" stroke="#000" stroke-width="{w}" stroke-linejoin="round"/></mask></defs>'
            '<g mask="url(#{p}gap)"><path transform="{b}" fill="{wine}" fill-rule="evenodd" d="{o}{i}"/></g>'
            '<path transform="{f}" fill="{white}" fill-rule="evenodd" d="{o}{i}"/>').format(
                p=prefix, f=place(FRONT), b=place(BACK), o=D_OUT, i=D_IN, w=round(GAP / SCALE, 2), wine=WINE, white=WHITE)


def svg(width, height, body, label='The Domains of Dread'):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {} {}" role="img" aria-label="{}">'
            '<title>{}</title>{}</svg>\n').format(width, height, label, label, body)


def outlined(text, cap_height, tracking):
    """A line of capitals as one path, baseline at y = 0, with its width. No font is needed to show it."""
    font = TTFont(FONT)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = cap_height / font['OS/2'].sCapHeight
    x, parts = 0.0, []
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(glyphs, ntos=lambda v: ('%.2f' % v).rstrip('0').rstrip('.'))
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, x, 0)))
        parts.append(pen.getCommands())
        x += glyphs[name].width * scale + tracking
    return ''.join(parts), x - tracking


def write(name, text):
    with open(os.path.join(HERE, name), 'w', encoding='utf-8') as f:
        f.write(text)


def png(src, size, out, ground=None):
    cmd = ['rsvg-convert', '-w', str(size), '-h', str(size)] + (['-b', ground] if ground else []) + [os.path.join(HERE, src), '-o', os.path.join(HERE, out)]
    subprocess.run(cmd, check=True)


def main():
    # the mark alone, for black and other dark grounds
    write('tdod-mark.svg', svg(64, 64, mark()))
    # the mark on its own black ground, for browser tabs and app icons, which may sit on anything
    write('tdod-icon.svg', svg(64, 64, '<rect width="64" height="64" fill="{}"/><g transform="translate(4.5 4.5) scale(0.86)">{}</g>'.format(BLACK, mark())))
    # the mark with the site's name, in one line and stacked
    cap = 13.0
    line, width = outlined('THE DOMAINS OF DREAD', cap, 2.2)
    write('tdod-lockup.svg', svg(round(64 + 14 + width + 4), 64,
          mark() + '<path transform="translate(78 {})" fill="{}" d="{}"/>'.format(32 + cap / 2, WHITE, line)))
    top, wt = outlined('THE DOMAINS', 15.0, 2.6)
    bottom, wb = outlined('OF DREAD', 15.0, 2.6)
    w = max(wt, wb)
    # the two lines and the rule between them sit evenly about the mark's middle: the space above
    # the rule is the space below it
    cap2, rule, gap = 15.0, 1.2, 4.4
    write('tdod-lockup-stacked.svg', svg(round(64 + 14 + w + 4), 64,
          mark() + '<path transform="translate(78 {ya})" fill="{c}" d="{a}"/><path transform="translate(78 {yb})" fill="{c}" d="{b}"/>'
          '<path d="M78 32h{w}" stroke="{wine}" stroke-width="{r}"/>'.format(
              c=WHITE, a=top, b=bottom, w=round(w, 1), wine=WINE, r=rule,
              ya=32 - rule / 2 - gap, yb=32 + rule / 2 + gap + cap2)))
    for size in (16, 32, 48, 135, 180, 192, 512):
        png('tdod-icon.svg', size, 'tdod-icon-{}.png'.format(size))
    os.replace(os.path.join(HERE, 'tdod-icon-180.png'), os.path.join(HERE, 'apple-touch-icon.png'))
    subprocess.run(['magick'] + [os.path.join(HERE, 'tdod-icon-{}.png'.format(s)) for s in (16, 32, 48)] + [os.path.join(HERE, 'favicon.ico')], check=True)
    for s in (16, 48):
        os.remove(os.path.join(HERE, 'tdod-icon-{}.png'.format(s)))
    print('wrote', ', '.join(sorted(f for f in os.listdir(HERE) if f.startswith(('tdod-', 'favicon', 'apple-')))))


if __name__ == '__main__':
    main()
