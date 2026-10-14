#!/usr/bin/env python3
"""Draw the site's logo files from one description of the mark.

  build.py            writes the SVGs, PNGs and favicon.ico beside this script

The mark is the Two Ds: a white roman capital D with a wine-red one behind it and below, like
a shadow. The owner chose it on 8 October 2026, with the lifted wine red. The letter is drawn
here, not taken from a font. The site's name beside it is set in IM Fell English (Open Font
License), the headings' face since 14 October 2026 (Noto Serif Medium before), and turned into
outlines, so the files need no font where they are shown.

Needs fontTools with brotli (the font is the static site's woff2), rsvg-convert and ImageMagick.
"""
import os
import subprocess

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
WHITE, WINE, BLACK = '#ffffff', '#a12d40', '#000000'
FONT = os.path.join(HERE, '..', '..', 'site', 'assets', 'fonts', 'im-fell-english-regular.woff2')

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


# IM Fell's outlines follow the ink of the old printing they were taken from: thousands of small
# curves. Each contour is traced to points and kept to within LEAST units (a twenty-fifth of a pixel
# at the logo's own size), which takes the file from 87 kB to a few, with no difference to see.
LEAST = 0.04


def contours(recording):
    """The outline as lists of points, its curves traced in short steps."""
    out, pts = [], []
    for op, args in recording.value:
        if op == 'moveTo':
            pts = [args[0]]
        elif op == 'lineTo':
            pts.append(args[0])
        elif op == 'qCurveTo':
            start = pts[-1]
            ctrl, end = list(args[:-1]), args[-1]
            if end is None:
                continue
            # a run of off-curve points stands for curves joined at their midpoints
            on = [start] + [((ctrl[i][0] + ctrl[i + 1][0]) / 2, (ctrl[i][1] + ctrl[i + 1][1]) / 2) for i in range(len(ctrl) - 1)] + [end]
            for i, c in enumerate(ctrl):
                a, b = on[i], on[i + 1]
                for k in range(1, 9):
                    t = k / 8
                    pts.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0],
                                (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]))
        elif op in ('closePath', 'endPath'):
            if pts:
                out.append(pts)
            pts = []
    return out


def simplify(pts, least):
    """Douglas and Peucker: the fewest points within `least` of the traced line."""
    if len(pts) < 3:
        return pts
    (ax, ay), (bx, by) = pts[0], pts[-1]
    dx, dy = bx - ax, by - ay
    length = (dx * dx + dy * dy) ** 0.5
    far, at = -1, 0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        d = abs(dy * px - dx * py + bx * ay - by * ax) / length if length else ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
        if d > far:
            far, at = d, i
    if far <= least:
        return [pts[0], pts[-1]]
    return simplify(pts[:at + 1], least)[:-1] + simplify(pts[at:], least)


def path(contour):
    """A closed contour as compact path data: rounded points, then steps between them."""
    num = lambda v: (('%.2f' % v).rstrip('0').rstrip('.') or '0').replace('-0', '0') if abs(v) < 0.005 else ('%.2f' % v).rstrip('0').rstrip('.')
    pts = [(round(x, 2), round(y, 2)) for x, y in contour]
    out = ['M{} {}'.format(num(pts[0][0]), num(pts[0][1])), 'l']
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        out.append('{} {}'.format(num(x1 - x0), num(y1 - y0)))
    return out[0] + out[1] + ' '.join(out[2:]) + 'z'


def outlined(text, cap_height, tracking):
    """A line of capitals as one path, baseline at y = 0, with its width. No font is needed to show it."""
    font = TTFont(FONT)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = cap_height / font['OS/2'].sCapHeight
    x, parts = 0.0, []
    for ch in text:
        name = cmap[ord(ch)]
        rec = DecomposingRecordingPen(glyphs)
        glyphs[name].draw(TransformPen(rec, (scale, 0, 0, -scale, x, 0)))
        for c in contours(rec):
            if c[0] == c[-1]:
                c = c[:-1]
            parts.append(path(simplify(c + [c[0]], LEAST)[:-1]))
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
