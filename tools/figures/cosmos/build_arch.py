"""Architecture diagram of the COSMOS ground station, drawn in the site's own figure style.

Usage: python3 -I build_arch.py <.archify/architecture-cosmos-*/candidate.json> <out.html>

The candidate file is the code-checked component and link list behind the earlier Archify drawing (from ~/cosmos_gcs).
Every box, line and label here comes from it; the drawing only distils it:
- edge labels that repeat a box's own second line are left off the drawing ("serial" on the weather station and the
  other devices, "ensemble", "records", "reads", "replay", "verifies"); the text list under the figure keeps them all;
- the server's second line is taken from the candidate's own card ("parses its own stream and serves its own
  WebSocket"), and the server-to-page link is drawn with a head at each end, since it carries telemetry one way and
  commands the other.
Two hand-placed layouts: left to right from 640 px wide, top to bottom below that.
"""
import html
import json
import sys
from pathlib import Path

cand, out = json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2])
C = {c['id']: c for c in cand['components']}
L = {k['id']: k for k in cand['connections']}
CARDS = ' '.join(i for c in cand['cards'] for i in c['items'])

SUB = {
    'rocket': C['rocket']['sublabel'], 'radio': None, 'weather': C['weather']['sublabel'],
    'others': C['others']['sublabel'], 'launcher': C['launcher']['sublabel'], 'server': 'parser and WebSocket',
    'sim': C['sim']['sublabel'], 'page': C['page']['sublabel'], 'session': C['session']['sublabel'],
    'replay': C['replay']['sublabel'], 'verify': C['verify']['sublabel'],
}
assert 'parser' in C['server']['sublabel'] and 'serves its own WebSocket' in CARDS
assert C['radio']['sublabel'] == L['radio-server']['label'] == 'serial'
NAME = {k: C[k]['label'] for k in C}
MAIN = {'rocket-radio', 'radio-server', 'server-page'}   # the live telemetry path
EXT = {'rocket', 'radio', 'weather', 'others'}
E = lambda s: html.escape(s, quote=True)


class Fig:
    """One hand-placed drawing. Coordinates are in viewBox px; boxes are (x, y, w, h)."""

    def __init__(self, w, h, cls, pre):
        self.w, self.h, self.cls, self.pre, self.parts, self.drawn, self.links = w, h, cls, pre, [], set(), set()

    def text(self, x, y, s, cls, anchor='middle'):
        self.parts.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{E(s)}</text>')

    def box(self, k, x, y, w, h, sub=None, step=16):
        """sub: the second line split over several lines where a narrow box needs it."""
        self.drawn.add(k)
        cx, cy = x + w / 2, y + h / 2
        lines = sub or ([SUB[k]] if SUB[k] else [])
        assert ' '.join(lines) == (SUB[k] or ''), k
        self.parts.append(f'<rect class="box" x="{x}" y="{y}" width="{w}" height="{h}" rx="4"/>')
        top = cy + 5 - (step + 1) * len(lines) / 2
        self.text(cx, top, NAME[k], 'name')
        for i, s in enumerate(lines):
            self.text(cx, top + 17 + step * i, s, 'sub')

    def ext(self, k, x, y, anchor, lines=None, step=16):
        """A device outside COSMOS: plain text, no box. y is the name's baseline."""
        self.drawn.add(k)
        lines = lines or ([SUB[k]] if SUB[k] else [])
        assert ' '.join(lines) == (SUB[k] or ''), k
        self.text(x, y, NAME[k], 'name', anchor)
        for i, s in enumerate(lines):
            self.text(x, y + step + 1 + step * i, s, 'sub', anchor)

    def edge(self, link, pts, both=False, r=6):
        """An orthogonal line through pts with rounded corners, arrowhead at the last point (and the first if both)."""
        assert link in L, link
        self.links.add(link)
        main = link in MAIN
        d = f'M{pts[0][0]},{pts[0][1]}'
        for i in range(1, len(pts) - 1):
            (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
            a = min(r, (abs(x1 - x0) + abs(y1 - y0)) / 2, (abs(x2 - x1) + abs(y2 - y1)) / 2)
            sx, sy = (x1 > x0) - (x1 < x0), (y1 > y0) - (y1 < y0)
            tx, ty = (x2 > x1) - (x2 < x1), (y2 > y1) - (y2 < y1)
            d += f' L{x1 - sx * a},{y1 - sy * a} Q{x1},{y1} {x1 + tx * a},{y1 + ty * a}'
        d += f' L{pts[-1][0]},{pts[-1][1]}'
        head = f'url(#{self.pre}-{"hm" if main else "h"})'
        start = f' marker-start="url(#{self.pre}-{"tm" if main else "t"})"' if both else ''
        self.parts.append(f'<path class="edge{" main" if main else ""}" d="{d}" marker-end="{head}"{start}/>')

    def svg(self, label):
        assert self.drawn == set(C), set(C) ^ self.drawn
        assert self.links == set(L), set(L) ^ self.links
        mk = lambda i, s, d: (f'<marker id="{self.pre}-{i}" viewBox="0 0 10 10" refX="{10 if d == "e" else 0}" refY="5" '
                              f'markerWidth="{s}" markerHeight="{s}" markerUnits="userSpaceOnUse" orient="auto">'
                              f'<path d="{"M0,1 L10,5 L0,9 z" if d == "e" else "M10,1 L0,5 L10,9 z"}" class="head"/></marker>')
        defs = '<defs>' + mk('h', 8, 'e') + mk('hm', 10, 'e') + mk('t', 8, 's') + mk('tm', 10, 's') + '</defs>'
        return (f'<svg class="{self.cls}" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{E(label)}">'
                + defs + ''.join(self.parts) + '</svg>')


def wide():
    """Left to right: devices, one server per device, then what each server feeds."""
    f = Fig(832, 398, 'wide', 'w')
    D = 176                                     # devices are right-aligned to this x
    X = [226, 436, 618]                         # server, sim and log, page and replay
    W = [150, 150, 184]
    cx = [x + w / 2 for x, w in zip(X, W)]
    BH = 50
    R = [14, 104, 176, 248, 334]                # row tops
    m = [r + BH / 2 for r in R]
    f.ext('rocket', D, 30, 'end', ['flight computer', 'in the rocket'])
    f.box('launcher', X[0], R[0], W[0], BH)
    f.box('server', X[0], R[1], W[0], R[3] + BH - R[1])
    f.edge('rocket-radio', [(150, 72), (150, 115)])
    f.text(144, 98, L['rocket-radio']['label'], 'lbl', 'end')
    f.ext('radio', D, m[1] + 5, 'end')
    f.edge('radio-server', [(D + 6, m[1] - 6), (X[0], m[1] - 6)])
    f.text((D + X[0]) / 2 + 3, m[1] - 13, L['radio-server']['label'], 'lbl')
    f.edge('server-radio', [(X[0], m[1] + 6), (D + 6, m[1] + 6)])
    f.text((D + X[0]) / 2 + 3, m[1] + 22, L['server-radio']['label'], 'lbl')
    f.ext('weather', D, m[2] + 5, 'end')
    f.edge('weather-server', [(D + 6, m[2]), (X[0], m[2])])
    f.ext('others', D, m[3] + 5, 'end', ['HAVOC on USB,', 'GPS tracker'])
    f.edge('others-server', [(D + 6, m[3]), (X[0], m[3])])
    f.edge('launcher-server', [(cx[0], R[0] + BH), (cx[0], R[1])])
    f.text(cx[0] + 6, 88, L['launcher-server']['label'], 'lbl', 'start')
    f.box('sim', X[1], R[1], W[1], BH)
    f.edge('server-sim', [(X[0] + W[0], m[1]), (X[1], m[1])])
    f.text((X[0] + W[0] + X[1]) / 2, m[1] - 8, L['server-sim']['label'], 'lbl')
    f.box('page', X[2], R[2], W[2], BH)
    f.edge('server-page', [(X[0] + W[0], m[2]), (X[2], m[2])], both=True)
    f.text(cx[1], m[2] - 9, L['server-page']['label'], 'lbl')
    f.edge('sim-page', [(X[1] + W[1], m[1]), (cx[2], m[1]), (cx[2], R[2])])
    f.box('session', X[1], R[3], W[1], BH)
    f.edge('server-session', [(X[0] + W[0], m[3]), (X[1], m[3])])
    f.box('replay', X[2], R[3], W[2], BH)
    f.edge('session-replay', [(X[1] + W[1], m[3]), (X[2], m[3])])
    f.edge('replay-page', [(cx[2], R[3]), (cx[2], R[2] + BH)])
    f.box('verify', X[1], R[4], W[1], BH)
    f.edge('session-verify', [(cx[1], R[3] + BH), (cx[1], R[4])])
    return f


def narrow():
    """Top to bottom: the devices run into the full-width server row, and its outputs fan out below it."""
    f = Fig(358, 610, 'narrow', 'n')
    f.ext('rocket', 12, 24, 'start')
    f.edge('rocket-radio', [(34, 48), (34, 76)])
    f.text(40, 66, L['rocket-radio']['label'], 'lbl', 'start')
    f.ext('radio', 12, 96, 'start')
    SB = 296                                    # server row top
    f.edge('radio-server', [(164, 86), (292, 86), (292, SB)])
    f.text(204, 79, L['radio-server']['label'], 'lbl')
    f.edge('server-radio', [(272, SB), (272, 97), (164, 97)])
    f.text(204, 111, L['server-radio']['label'], 'lbl')
    f.ext('weather', 12, 140, 'start')
    f.edge('weather-server', [(124, 135), (248, 135), (248, SB)])
    f.ext('others', 12, 184, 'start')
    f.edge('others-server', [(110, 179), (224, 179), (224, SB)])
    f.box('launcher', 12, 228, 140, 46)
    f.edge('launcher-server', [(82, 274), (82, SB)])
    f.text(88, 290, L['launcher-server']['label'], 'lbl', 'start')
    f.box('server', 12, SB, 334, 46)
    A, B = 384, 468                             # row tops below the server
    f.box('sim', 12, A, 158, 46)
    f.edge('server-sim', [(91, SB + 46), (91, A)])
    f.text(97, 367, L['server-sim']['label'], 'lbl', 'start')
    f.box('session', 188, A, 158, 46)
    f.edge('server-session', [(320, SB + 46), (320, A)])
    f.edge('server-page', [(179, SB + 46), (179, 450), (148, 450), (148, B)], both=True)
    f.text(185, 367, L['server-page']['label'], 'lbl', 'start')
    f.box('page', 12, B, 158, 62, ['flight state,', 'alarms, callouts'])
    f.edge('sim-page', [(91, A + 46), (91, B)])
    f.box('replay', 188, B + 8, 136, 46)
    f.edge('session-replay', [(256, A + 46), (256, B + 8)])
    f.edge('replay-page', [(188, B + 31), (170, B + 31)])
    f.box('verify', 188, 552, 158, 46)
    f.edge('session-verify', [(336, A + 46), (336, 552)])
    return f


ARIA = ("Block diagram of the COSMOS ground station. HAVOC-2's telemetry comes down through the RFD900 ground radio. The "
        "radio, the weather station and the other devices each feed their own cosmos-server over serial, and the radio "
        "takes the uplink back. A launcher spawns and restarts one server per device. Each server sends telemetry to the "
        "React page and takes its commands over its WebSocket, sends weather to the sim service, whose OpenRocket "
        "ensemble goes to the page, and writes hash-chained records to the session log. cosmos-verify checks the log's "
        "hash chain, and cosmos-replay re-serves a session to the page.")

GROUPS = [('Devices', ['rocket', 'radio', 'weather', 'others']),
          ('COSMOS', ['launcher', 'server', 'sim', 'page', 'session', 'replay', 'verify'])]
assert sorted(sum((g for _, g in GROUPS), [])) == sorted(C)
DESC = {k: ', '.join(filter(None, [C[k].get('sublabel'), C[k].get('tag')])) for k in C}
comp = ''.join(f'<li>{E(g)}<ul>' + ''.join(f'<li>{E(NAME[k])}: {E(DESC[k])}</li>' for k in ks) + '</ul></li>'
               for g, ks in GROUPS)
links = []
for k in cand['connections']:
    lab = k['label'] + (', over its WebSocket' if k['id'] == 'server-page' else '')
    links.append(f'<li>{E(NAME[k["from"]])} to {E(NAME[k["to"]])}: {E(lab)}</li>')

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>COSMOS ground station architecture</title>
<!-- Generated by portfolio/figures/cosmos/build_arch.py from the code-checked candidate list in
     .archify/architecture-cosmos-20261112-155253/candidate.json. Do not edit by hand. -->
<style>
@font-face {{ font-family: "Sanchez"; src: url("../fonts/sanchez-400-latin.woff2") format("woff2"); font-display: swap; }}
:root {{ --ink: #2E1499; --muted: #5E4FA8; --surface: #FFFFFF; }}
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
text {{ font-family: "Sanchez", Georgia, serif; }}
.name {{ fill: var(--ink); font-size: 14px; }}
.sub, .lbl {{ fill: var(--muted); font-size: 12.5px; }}
svg.narrow .sub, svg.narrow .lbl {{ font-size: 12px; }}
.edge {{ fill: none; stroke: var(--ink); stroke-width: 1.25; }}
.edge.main {{ stroke-width: 2; }}
.head {{ fill: var(--ink); }}
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
