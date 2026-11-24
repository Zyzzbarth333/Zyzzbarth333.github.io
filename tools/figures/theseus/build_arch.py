"""Architecture diagram of the Theseus V autonomy stack, drawn in the site's own figure style.

Usage: python3 -I build_arch.py <.archify/architecture-theseus-*/candidate.json> <out.html>

The candidate file is the code-checked component and link list behind the earlier Archify drawing (from
~/theseus-autonomy). Every box, line and label here comes from it; the drawing only distils it:
- the Orange Pi 5 Plus is the one boundary drawn; YOLO + ArUco carries its computer (the Jetson) as its second line;
- edge labels that repeat a box's own second line are left off the drawing ("points, IMU", "scans", "map",
  "frontiers", "video"); the text list under the figure keeps every label;
- the detections link "cubes, placards" is drawn as its two topics (the supervisor subscribes to cube markers and
  to /aruco_markers separately): cubes in ink, forked to the supervisor and Nav2 (the candidate's detect-nav2 link),
  and placards in the one red accent, stopped short, because at ARCh 2026 they did not reach the supervisor.
Two hand-placed layouts: left to right from 640 px wide, top to bottom below that.
"""
import html
import json
import sys
from pathlib import Path

cand, out = json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2])
C = {c['id']: c for c in cand['components']}
L = {k['id']: k for k in cand['connections']}
REGION = next(b for b in cand['boundaries'] if b['label'].startswith('Orange Pi'))
JETSON = next(b for b in cand['boundaries'] if b['label'].startswith('Jetson'))

# Second lines, distilled from each component's own sublabel (or the boundary it sits in).
SUB = {
    'lidar': C['lidar']['sublabel'], 'fastlio': 'odometry', 'kiss': C['kiss']['sublabel'],
    'frontier': C['frontier']['sublabel'], 'supervisor': C['supervisor']['sublabel'], 'nav2': None,
    'safety': 'slow, then stop', 'bridge': 'UDP', 'pi': C['pi']['tag'], 'mcu': C['mcu']['sublabel'],
    'operator': C['operator']['sublabel'], 'detect': JETSON['label'], 'cameras': 'centre, left, right',
}
# Every distilled line must be a piece of the candidate's own words.
SOURCE = {k: ' '.join(filter(None, [C[k].get('sublabel'), C[k].get('tag')])) for k in C}
SOURCE['detect'] += ' ' + JETSON['label']
for k, s in SUB.items():
    assert s is None or s in SOURCE[k], (k, s)
assert set(REGION['wraps']) == {'fastlio', 'kiss', 'frontier', 'supervisor', 'nav2', 'safety', 'bridge'}
CUBES, PLACARDS = L['detect-supervisor']['label'].split(', ')
assert (CUBES, PLACARDS) == ('cubes', 'placards') and L['detect-nav2']['label'] == CUBES
NAME = {k: C[k]['label'] for k in C}
MAIN = {'lidar-fastlio', 'fastlio-kiss', 'kiss-frontier', 'frontier-supervisor', 'supervisor-nav2',
        'nav2-safety', 'safety-bridge', 'bridge-pi', 'pi-mcu'}   # the path the caption follows
E = lambda s: html.escape(s, quote=True)


class Fig:
    """One hand-placed drawing. Coordinates are in viewBox px; boxes are (x, y, w, h)."""

    def __init__(self, w, h, cls, pre):
        self.w, self.h, self.cls, self.pre, self.parts, self.drawn, self.links = w, h, cls, pre, [], set(), set()

    def text(self, x, y, s, cls, anchor='middle'):
        self.parts.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{E(s)}</text>')

    def box(self, k, x, y, w, h):
        self.drawn.add(k)
        cx, cy = x + w / 2, y + h / 2
        self.parts.append(f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" rx="4"/>')
        if SUB[k]:
            self.text(cx, cy - 3, NAME[k], 'name')
            self.text(cx, cy + 14, SUB[k], 'sub')
        else:
            self.text(cx, cy + 5, NAME[k], 'name')

    def ext(self, k, x, y, anchor, step):
        """A part outside the software (hardware or the operator's browser): plain text, no box. y is the name's baseline."""
        self.drawn.add(k)
        self.text(x, y, NAME[k], 'name', anchor)
        if SUB[k]:
            self.text(x, y + step, SUB[k], 'sub', anchor)

    def region(self, x, y, w, h, lx, ly, anchor):
        self.parts.insert(0, f'<rect class="region" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>')
        self.text(lx, ly, REGION['label'], 'rlabel', anchor)

    def edge(self, link, pts, head=True, cls=None, r=6):
        """An orthogonal line through pts with rounded corners, arrowhead at the last point."""
        assert link in L, link
        self.links.add(link)
        cls = cls or ('edge main' if link in MAIN else 'edge')
        d = f'M{pts[0][0]},{pts[0][1]}'
        for i in range(1, len(pts) - 1):
            (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
            a = min(r, (abs(x1 - x0) + abs(y1 - y0)) / 2, (abs(x2 - x1) + abs(y2 - y1)) / 2)
            sx, sy = (x1 > x0) - (x1 < x0), (y1 > y0) - (y1 < y0)
            tx, ty = (x2 > x1) - (x2 < x1), (y2 > y1) - (y2 < y1)
            d += f' L{x1 - sx * a},{y1 - sy * a} Q{x1},{y1} {x1 + tx * a},{y1 + ty * a}'
        d += f' L{pts[-1][0]},{pts[-1][1]}'
        mark = f' marker-end="url(#{self.pre}-{"hm" if "main" in cls else "h"})"' if head else ''
        self.parts.append(f'<path class="{cls}" d="{d}"{mark}/>')

    def dot(self, x, y):
        self.parts.append(f'<circle class="joint" cx="{x}" cy="{y}" r="3"/>')

    def stop(self, x1, y1, x2, y2):
        self.parts.append(f'<line class="stop" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')

    def svg(self, label):
        assert self.drawn == set(C), set(C) ^ self.drawn
        assert self.links == set(L), set(L) ^ self.links
        defs = (f'<defs><marker id="{self.pre}-h" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" '
                f'markerUnits="userSpaceOnUse" orient="auto"><path d="M0,1 L10,5 L0,9 z" class="head"/></marker>'
                f'<marker id="{self.pre}-hm" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="10" markerHeight="10" '
                f'markerUnits="userSpaceOnUse" orient="auto"><path d="M0,1 L10,5 L0,9 z" class="head"/></marker></defs>')
        return (f'<svg class="{self.cls}" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{E(label)}">'
                + defs + ''.join(self.parts) + '</svg>')


def wide():
    """Left to right in three rows: mapping, then mission and motion, then vision and the rover side."""
    f = Fig(832, 470, 'wide', 'w')
    X = [28, 240, 452, 664]                     # four columns of 140 px boxes
    BW, BH = 140, 50
    cx = [x + BW / 2 for x in X]
    R1, R2, R3 = 96, 202, 340                   # row tops
    f.region(16, 80, 800, 196, 804, 100, 'end')
    f.ext('lidar', cx[0], 26, 'middle', 17)
    for k, c, r in [('fastlio', 0, R1), ('kiss', 1, R1), ('frontier', 2, R1),
                    ('supervisor', 0, R2), ('nav2', 1, R2), ('safety', 2, R2), ('bridge', 3, R2),
                    ('detect', 1, R3), ('pi', 3, R3)]:
        f.box(k, X[c], r, BW, BH)
    m1, m2, m3 = R1 + BH / 2, R2 + BH / 2, R3 + BH / 2
    f.edge('lidar-fastlio', [(cx[0], 52), (cx[0], R1)])
    f.edge('fastlio-kiss', [(X[0] + BW, m1), (X[1], m1)])
    f.edge('kiss-frontier', [(X[1] + BW, m1), (X[2], m1)])
    f.edge('frontier-supervisor', [(cx[2], R1 + BH), (cx[2], 174), (cx[0], 174), (cx[0], R2)])
    f.edge('supervisor-nav2', [(X[0] + BW, m2), (X[1], m2)])
    f.text((X[0] + BW + X[1]) / 2, m2 - 8, L['supervisor-nav2']['label'], 'lbl')
    f.edge('nav2-safety', [(X[1] + BW, m2), (X[2], m2)])
    f.text((X[1] + BW + X[2]) / 2, m2 - 8, L['nav2-safety']['label'], 'lbl')
    f.edge('safety-bridge', [(X[2] + BW, m2), (X[3], m2)])
    # the rover bridge and the rover server talk both ways over UDP
    f.edge('bridge-pi', [(700, R2 + BH), (700, R3)])
    f.text(694, 302, L['bridge-pi']['label'], 'lbl', 'end')
    f.edge('pi-bridge', [(724, R3), (724, R2 + BH)])
    f.text(730, 302, L['pi-bridge']['label'], 'lbl', 'start')
    f.edge('pi-mcu', [(cx[3], R3 + BH), (cx[3], 420)])
    f.text(cx[3] + 6, 410, L['pi-mcu']['label'], 'lbl', 'start')
    f.ext('mcu', cx[3], 440, 'middle', 17)
    f.ext('operator', 574, m3 + 5, 'end', 17)
    f.edge('operator-pi', [(580, m3), (X[3], m3)])
    f.text(622, m3 - 8, L['operator-pi']['label'], 'lbl')
    f.ext('cameras', 172, m3 + 5, 'end', 17)
    f.edge('cameras-detect', [(178, m3), (X[1], m3)])
    # detections: cubes reach the supervisor and Nav2; placards stop short (red)
    f.edge('detect-nav2', [(cx[1], R3), (cx[1], R2 + BH)])
    f.edge('detect-supervisor', [(cx[1], 300), (128, 300), (128, R2 + BH)])
    f.dot(cx[1], 300)
    f.text(cx[1] + 6, 326, CUBES, 'lbl', 'start')
    f.edge('detect-supervisor', [(270, R3), (270, 316), (68, 316), (68, 290)], head=False, cls='edge fault')
    f.stop(60, 290, 76, 290)
    f.text(150, 333, PLACARDS, 'lbl fault-lbl')
    return f


def narrow():
    """Top to bottom: the Orange Pi chain down the left, the sensors, the Jetson and the browser joining from the right."""
    f = Fig(358, 694, 'narrow', 'n')
    X, BW, BH = 22, 130, 46
    cx = X + BW / 2
    RX, RW = 231, 115                           # right-hand column
    rc = RX + RW / 2
    tops = {'fastlio': 34, 'kiss': 100, 'frontier': 166, 'supervisor': 232, 'nav2': 312, 'safety': 392, 'bridge': 458}
    f.region(12, 8, 150, 508, 22, 25, 'start')
    for k, t in tops.items():
        f.box(k, X, t, BW, BH)
    mid = {k: t + BH / 2 for k, t in tops.items()}
    chain = list(tops)
    for a, b in zip(chain, chain[1:]):
        f.edge(f'{a}-{b}', [(cx, tops[a] + BH), (cx, tops[b])])
    f.text(cx + 6, mid['supervisor'] + BH / 2 + 21, L['supervisor-nav2']['label'], 'lbl', 'start')
    f.text(cx + 6, mid['nav2'] + BH / 2 + 21, L['nav2-safety']['label'], 'lbl', 'start')
    f.ext('lidar', RX + 3, mid['fastlio'] + 4, 'start', 16)
    f.edge('lidar-fastlio', [(RX - 3, mid['fastlio']), (X + BW, mid['fastlio'])])
    f.ext('cameras', rc, 188, 'middle', 16)
    f.edge('cameras-detect', [(rc, 212), (rc, tops['supervisor'])])
    f.box('detect', RX, tops['supervisor'], RW, BH)
    ys = mid['supervisor']
    f.edge('detect-supervisor', [(RX, ys - 8), (172, ys - 8)], head=False, cls='edge fault')
    f.stop(172, ys - 15, 172, ys - 1)
    f.text(202, ys - 15, PLACARDS, 'lbl fault-lbl')
    f.edge('detect-supervisor', [(RX, ys + 10), (X + BW, ys + 10)])
    f.edge('detect-nav2', [(194, ys + 10), (194, mid['nav2']), (X + BW, mid['nav2'])])
    f.dot(194, ys + 10)
    f.text(200, 307, CUBES, 'lbl', 'start')
    S = 572                                     # rover server top
    f.edge('bridge-pi', [(98, tops['bridge'] + BH), (98, S)])
    f.text(92, 546, L['bridge-pi']['label'], 'lbl', 'end')
    f.edge('pi-bridge', [(122, S), (122, tops['bridge'] + BH)])
    f.text(128, 546, L['pi-bridge']['label'], 'lbl', 'start')
    f.box('pi', X, S, BW, BH)
    f.edge('pi-mcu', [(cx, S + BH), (cx, 648)])
    f.text(cx + 6, 637, L['pi-mcu']['label'], 'lbl', 'start')
    f.ext('mcu', cx, 666, 'middle', 16)
    f.ext('operator', 346, 666, 'end', 16)
    f.edge('operator-pi', [(290, 652), (290, S + BH / 2), (X + BW, S + BH / 2)])
    f.text(221, S + BH / 2 - 7, L['operator-pi']['label'], 'lbl')
    return f


ARIA = ("Block diagram of the Theseus V autonomy stack. The Livox MID-360 LiDAR feeds FAST-LIO2 odometry on the Orange Pi "
        "5 Plus, then KISS-SLAM's 2D occupancy map and the frontier detector, which feeds the 10-state supervisor. The "
        "supervisor sends goals to Nav2, and Nav2's velocity passes the geofence and the rover bridge to the rover server's "
        "velocity gate, then over USB serial to the Picos. The rover server sends the arena and autonomy enable back to the "
        "bridge, and the operator's Theseus GCS page connects to it over WebSocket. YOLO and ArUco detection on the Jetson "
        "Xavier NX, fed by 3 of 5 IP cameras, sends cubes to the supervisor and to Nav2. Its placard detections, drawn in "
        "red, did not reach the supervisor at ARCh 2026.")

# The text view: every component and every link, with the candidate's own labels.
WHERE = [('On the Orange Pi 5 Plus', REGION['wraps']), ('On the Jetson Xavier NX', ['detect']),
         ("On the rover's Raspberry Pi", ['pi']), ('Hardware and the browser', ['lidar', 'cameras', 'mcu', 'operator'])]
assert sorted(sum((w for _, w in WHERE), [])) == sorted(C)
DESC = {k: C[k].get('sublabel') for k in C} | {'pi': C['pi']['tag']}   # the Pi itself is the group heading
comp = ''.join(f'<li>{E(w)}<ul>' + ''.join(f'<li>{E(NAME[k])}: {E(DESC[k])}</li>' for k in ks) + '</ul></li>'
               for w, ks in WHERE)
links = []
for k in cand['connections']:
    lab = k['label']
    if k['id'] == 'detect-supervisor':
        lab = f'{CUBES}; {PLACARDS}, which did not reach the supervisor at ARCh 2026'
    links.append(f'<li>{E(NAME[k["from"]])} to {E(NAME[k["to"]])}: {E(lab)}</li>')

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Theseus V autonomy architecture</title>
<!-- Generated by portfolio/figures/theseus/build_arch.py from the code-checked candidate list in
     .archify/architecture-theseus-20261112-155253/candidate.json. Do not edit by hand. -->
<style>
@font-face {{ font-family: "Sanchez"; src: url("../fonts/sanchez-400-latin.woff2") format("woff2"); font-display: swap; }}
:root {{ --ink: #2E1499; --muted: #5E4FA8; --line: rgb(46 20 153 / 0.3); --red: #BB0700; --surface: #FFFFFF; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: var(--surface); color: var(--ink); font: 14px/1.45 "Sanchez", Georgia, serif; }}
::selection {{ background: #ECE9F6; color: var(--ink); }}
.wrap {{ padding: 12px 0 10px; display: grid; gap: 10px; }}
details {{ padding: 0 16px; }}
svg {{ display: block; width: 100%; height: auto; overflow: visible; }}
svg.narrow {{ display: none; max-width: 440px; margin: 0 auto; }}
@media (max-width: 639.98px) {{
  svg.wide {{ display: none; }}
  svg.narrow {{ display: block; }}
  details {{ padding: 0 12px; }}
}}
.box {{ fill: var(--surface); stroke: var(--ink); stroke-width: 1.25; }}
.region {{ fill: none; stroke: var(--line); stroke-width: 1; }}
text {{ font-family: "Sanchez", Georgia, serif; }}
.name {{ fill: var(--ink); font-size: 14px; }}
.sub, .lbl, .rlabel {{ fill: var(--muted); font-size: 12.5px; }}
svg.narrow .sub, svg.narrow .lbl, svg.narrow .rlabel {{ font-size: 12px; }}
.edge {{ fill: none; stroke: var(--ink); stroke-width: 1.25; }}
.edge.main {{ stroke-width: 2; }}
.head, .joint {{ fill: var(--ink); }}
.edge.fault {{ stroke: var(--red); stroke-width: 1.75; }}
.stop {{ stroke: var(--red); stroke-width: 2.5; }}
.fault-lbl {{ fill: var(--red); }}
details {{ font-size: 13px; }}
summary {{ cursor: pointer; color: var(--muted); width: max-content; max-width: 100%; }}
summary:focus-visible {{ outline: 2px solid var(--ink); outline-offset: 3px; border-radius: 2px; }}
details p {{ margin: 10px 0 2px; color: var(--muted); }}
details ul {{ margin: 0; padding-left: 1.1em; line-height: 1.5; }}
details ul ul {{ margin-bottom: 4px; }}
</style>
</head>
<body>
<div class="wrap">
  {wide().svg(ARIA)}
  {narrow().svg(ARIA)}
  <details><summary>Components and links as a list</summary>
    <p>Components</p>
    <ul>{comp}</ul>
    <p>Links</p>
    <ul>{''.join(links)}</ul>
  </details>
</div>
</body>
</html>
'''
out.write_text(page)
print('wrote', out, f'{len(C)} components, {len(L)} links')
