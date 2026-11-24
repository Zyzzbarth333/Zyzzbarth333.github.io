"""HAVOC-2's flight-phase detector as a state diagram, drawn in the site's own figure style.

Usage: python3 -I build_states.py <HAVOC-fc>/firmware/havoc-flight/src <out.html>

Every threshold is read from flight_state.h (constexpr values) and checked against the transitions in
flight_state.cpp, so the drawing cannot drift from the code; a changed constant changes the labels, and a changed
transition fails an assert. Drawn from the firmware at HAVOC-fc 501495c (10 Oct 2026), the detector Isaac redesigned
after the first flight, tuned on that flight's logs and bench captures. It only reports the phase: it fires nothing.
Two hand-placed layouts, as in the COSMOS and Theseus diagrams: left to right from 640 px wide, top to bottom below.
"""
import html
import re
import sys
from pathlib import Path

src, out = Path(sys.argv[1]).expanduser(), Path(sys.argv[2])
H, CPP = (src / 'flight_state.h').read_text(), (src / 'flight_state.cpp').read_text()
K = {m[1]: float(m[2]) for m in re.finditer(r'static constexpr \w+ (\w+) = ([\d.]+)f?;', H)}
need = ['BOOST_ENTER_G', 'BOOST_RUN_SAMPLES', 'BOOST_EXIT_G', 'BOOST_EXIT_SAMPLES', 'APOGEE_VEL_MPS', 'APOGEE_HOLD_MS',
        'LAUNCH_CONFIRM_M', 'LAUNCH_CONFIRM_MS', 'WITHDRAW_STILL_MS', 'STILL_G', 'LAND_VEL_MPS', 'LAND_HOLD_MS']
assert all(n in K for n in need), [n for n in need if n not in K]
# the transitions the labels describe, as the code writes them
for pat in [r'thrust = accel_valid && n > BOOST_ENTER_G', r'boost_run_ >= BOOST_RUN_SAMPLES\)\s*\{\s*phase_ = HAVOC_FLIGHT_BOOST',
            r'n < BOOST_EXIT_G\) \{\s*if \(\+\+exit_run_ >= BOOST_EXIT_SAMPLES\) \{\s*phase_ = HAVOC_FLIGHT_COAST',
            r'launch_confirmed_ && v_mps_ < -APOGEE_VEL_MPS\) \{\s*phase_ = HAVOC_FLIGHT_APOGEE',
            r'now - apogee_ms_ >= APOGEE_HOLD_MS\) phase_ = HAVOC_FLIGHT_DESCENT',
            r'still_since_ms_ >= LAND_HOLD_MS &&[\s\S]{0,120}land_range\(now\) <= LAND_BAND_M\) \{\s*phase_ = HAVOC_FLIGHT_LANDED',
            r'baro_m >= launch_h0_m_ \+ LAUNCH_CONFIRM_M', r'now - launch_ms_ >= LAUNCH_CONFIRM_MS',
            r'still_since_ms_ >= WITHDRAW_STILL_MS\) withdraw_launch', r'LAUNCH_CONFIRM_MS = 1430']:
    assert re.search(pat, CPP + H), pat
f = lambda v: f'{v:g}'
run_ms = K['BOOST_RUN_SAMPLES'] * 20                     # 50 Hz
band = K['LAND_VEL_MPS'] * K['LAND_HOLD_MS'] / 1000

STATES = [('idle', 'Idle', 'on the pad'), ('boost', 'Boost', 'motor burning'), ('coast', 'Coast', 'unpowered'),
          ('apogee', 'Apogee', 'the peak'), ('descent', 'Descent', 'falling'), ('landed', 'Landed', 'on the ground')]
STEP = [  # label lines for each forward transition
    [f'|a| > {f(K["BOOST_ENTER_G"])} g', f'for {f(run_ms)} ms'],
    [f'|a| < {f(K["BOOST_EXIT_G"])} g', f'{f(K["BOOST_EXIT_SAMPLES"])} samples'],
    ['launch confirmed,', f'v < −{f(K["APOGEE_VEL_MPS"])} m/s'],
    [f'after {f(K["APOGEE_HOLD_MS"] / 1000)} s'],
    [f'still {f(K["LAND_HOLD_MS"] / 1000)} s, barometer', f'within {f(band)} m'],
]
BACK = (f'barometer not {f(K["LAUNCH_CONFIRM_M"])} m up within {f(K["LAUNCH_CONFIRM_MS"] / 1000)} s, '
        f'then still {f(K["WITHDRAW_STILL_MS"] / 1000)} s: launch withdrawn')
BACK_N = [f'barometer not {f(K["LAUNCH_CONFIRM_M"])} m up', f'within {f(K["LAUNCH_CONFIRM_MS"] / 1000)} s, then still',
          f'{f(K["WITHDRAW_STILL_MS"] / 1000)} s: withdrawn']
E = lambda s: html.escape(s, quote=True)


class Fig:
    def __init__(self, w, h, cls, pre):
        self.w, self.h, self.cls, self.pre, self.parts = w, h, cls, pre, []

    def text(self, x, y, s, cls, anchor='middle'):
        self.parts.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{E(s)}</text>')

    def box(self, i, x, y, w, h):
        _, name, sub = STATES[i]
        end = i in (0, 5)
        self.parts.append(f'<rect class="box{" end" if end else ""}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2 if end else 4}"/>')
        self.text(x + w / 2, y + h / 2 - 3, name, 'name')
        self.text(x + w / 2, y + h / 2 + 14, sub, 'sub')

    def edge(self, pts, cls='edge', r=6):
        d = f'M{pts[0][0]},{pts[0][1]}'
        for i in range(1, len(pts) - 1):
            (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
            a = min(r, (abs(x1 - x0) + abs(y1 - y0)) / 2, (abs(x2 - x1) + abs(y2 - y1)) / 2)
            sx, sy = (x1 > x0) - (x1 < x0), (y1 > y0) - (y1 < y0)
            tx, ty = (x2 > x1) - (x2 < x1), (y2 > y1) - (y2 < y1)
            d += f' L{x1 - sx * a},{y1 - sy * a} Q{x1},{y1} {x1 + tx * a},{y1 + ty * a}'
        d += f' L{pts[-1][0]},{pts[-1][1]}'
        self.parts.append(f'<path class="{cls}" d="{d}" marker-end="url(#{self.pre}-{"hb" if "back" in cls else "h"})"/>')

    def svg(self, label):
        mk = lambda i, c: (f'<marker id="{self.pre}-{i}" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="9" markerHeight="9" '
                           f'markerUnits="userSpaceOnUse" orient="auto"><path d="M0,1 L10,5 L0,9 z" class="{c}"/></marker>')
        return (f'<svg class="{self.cls}" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{E(label)}">'
                f'<defs>{mk("h", "head")}{mk("hb", "head back")}</defs>' + ''.join(self.parts) + '</svg>')


def wide():
    """One row, left to right; the withdrawal loops back over the top."""
    f = Fig(832, 196, 'wide', 'w')
    BW, BH, Y = 100, 54, 62
    X = [4 + i * 144.8 for i in range(6)]                # 6 boxes of 100 in 832, 4 px margins, 44.8 px gaps
    for i in range(6):
        f.box(i, X[i], Y, BW, BH)
    for i, lines in enumerate(STEP):
        a, b = X[i] + BW, X[i + 1]
        f.edge([(a, Y + BH / 2), (b, Y + BH / 2)])
        cx = (a + b) / 2
        for j, s in enumerate(lines):
            f.text(cx, Y + BH + 30 + 16 * j, s, 'lbl')
        f.parts.append(f'<path class="tick" d="M{cx},{Y + BH / 2 + 5} V{Y + BH + 14}"/>')
    top = 22
    cxb, cxc, cxi = X[1] + BW / 2, X[2] + BW / 2, X[0] + BW / 2
    f.edge([(cxc, Y), (cxc, top), (cxi, top), (cxi, Y)], 'edge back')
    f.parts.append(f'<path class="edge back" d="M{cxb},{Y} V{top}"/>')
    f.text(X[2] + BW + 10, top + 4, BACK, 'lbl', 'start')
    return f


def narrow():
    """Top to bottom; labels to the right of each arrow, the withdrawal up the left."""
    f = Fig(358, 640, 'narrow', 'n')
    BW, BH, X = 132, 50, 44
    Y = [10 + i * 106 for i in range(6)]                 # 56 px between boxes
    for i in range(6):
        f.box(i, X, Y[i], BW, BH)
    cx = X + BW / 2
    for i, lines in enumerate(STEP):
        a, b = Y[i] + BH, Y[i + 1]
        f.edge([(cx, a), (cx, b)])
        for j, s in enumerate(lines):
            f.text(cx + 12, (a + b) / 2 + 5 - 8 * (len(lines) - 1) + 16 * j, s, 'lbl', 'start')
    lx = 20
    f.edge([(X, Y[2] + BH / 2), (lx, Y[2] + BH / 2), (lx, Y[0] + BH / 2), (X, Y[0] + BH / 2)], 'edge back')
    f.parts.append(f'<path class="edge back" d="M{X},{Y[1] + BH / 2} H{lx}"/>')
    for j, s in enumerate(BACK_N):
        f.text(X + BW + 12, Y[0] + 14 + 16 * j, s, 'lbl back', 'start')
    return f


ARIA = ('State diagram of HAVOC-2\'s flight-phase detector: Idle, Boost, Coast, Apogee, Descent and Landed, in that order. '
        + '; '.join(f'{STATES[i][1]} to {STATES[i + 1][1]} when {" ".join(STEP[i])}' for i in range(5))
        + f'. From Boost or Coast back to Idle when the {BACK}.')
items = ''.join(f'<li>{E(STATES[i][1])} to {E(STATES[i + 1][1])}: {E(" ".join(STEP[i]))}</li>' for i in range(5))
items += f'<li>Boost or Coast back to Idle: {E(BACK)}</li>'

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HAVOC-2 flight-phase detector</title>
<!-- Generated by portfolio/figures/havoc2/build_states.py from HAVOC-fc's flight_state.h and flight_state.cpp.
     Do not edit by hand. -->
<style>
@font-face {{ font-family: "Sanchez"; src: url("../fonts/sanchez-400-latin.woff2") format("woff2"); font-display: swap; }}
:root {{ --ink: #2E1499; --muted: #5E4FA8; --surface: #FFFFFF; --back: #BB0700; }}
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
.box.end {{ fill: #F4F2FB; }}
text {{ font-family: "Sanchez", Georgia, serif; }}
.name {{ fill: var(--ink); font-size: 14px; }}
.sub, .lbl {{ fill: var(--muted); font-size: 12.5px; }}
.lbl.back {{ fill: var(--back); }}
svg.wide .lbl:last-of-type {{ fill: var(--back); }}
.edge {{ fill: none; stroke: var(--ink); stroke-width: 1.5; }}
.edge.back {{ stroke: var(--back); stroke-width: 1.25; stroke-dasharray: 5 4; }}
.tick {{ stroke: #CFC8EC; stroke-width: 1; }}
.head {{ fill: var(--ink); }} .head.back {{ fill: var(--back); }}
details {{ font-size: 13px; }}
summary {{ cursor: pointer; color: var(--muted); width: max-content; max-width: 100%; }}
summary:focus-visible {{ outline: 2px solid var(--ink); outline-offset: 3px; border-radius: 2px; }}
details ul {{ margin: 8px 0 2px; padding-left: 1.1em; line-height: 1.5; }}
</style>
</head>
<body>
<div class="wrap">
  {wide().svg(ARIA)}
  {narrow().svg(ARIA)}
  <details><summary>Transitions as a list</summary>
    <ul>{items}</ul>
  </details>
</div>
</body>
</html>
'''
out.write_text(page)
print('wrote', out, {n: K[n] for n in need})
