"""A live replica of Theseus GCS's arena map and autonomy controls, drawn from the real arena_config.yaml
that the GCS's Arena Config Builder wrote for the ARCh 2026 mapping and autonomy task.

Usage: python3 -I build_arena.py ~/theseus-gcs/arena_config.yaml <out.html>

Every shape comes from the config: the arena edge (e-stop), the geofence slow zone, the planner's bounds,
the start pose, the five ArUco placards and the known obstacles. Positions in the config are in the
rover's SLAM frame; the config's own report_transform (90 degrees about the start point) maps them onto
the arena. Cube positions were unknown before the run, so none are drawn. The control strip mirrors the
GCS's Send config, Launch stack and teleop/auto flow in simulation mode: it changes nothing anywhere.
"""
import html
import json
import math
import sys
from pathlib import Path

import yaml

cfg = yaml.safe_load(Path(sys.argv[1]).read_text())['/**']['ros__parameters']
out = Path(sys.argv[2])
A = cfg['arena']
tf = A['report_transform']
ang, ox, oy = tf['angle_rad'], tf['origin_x'], tf['origin_y']
SX, SY = A['size_x'], A['size_y']


def to_arena(x, y):
    c, s = math.cos(ang), math.sin(ang)
    return ox + c * x - s * y, oy + s * x + c * y


def rect_of(b):
    pts = [to_arena(b['x_min'], b['y_min']), to_arena(b['x_max'], b['y_max'])]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)


def svg_y(y):           # arena +Y is up; SVG +y is down
    return SY - y


shapes = []
for label, key, cls in (('Planner bounds: goals stay inside', 'nav_bounds', 'nav'), ('Geofence: the rover slows down', 'geofence_bounds', 'geo')):
    x, y, w, h = rect_of(A[key])
    shapes.append(f'<rect class="z {cls}" data-l="{cls}" x="{x:.2f}" y="{svg_y(y + h):.2f}" width="{w:.2f}" height="{h:.2f}"><title>{label}</title></rect>')

obs = []
rows = []                                       # the same data as a table, for keyboards and screen readers
for name, o in cfg['obstacles']['known_obstacles'].items():
    X, Y = to_arena(o['x'], o['y'])
    rows.append((o['kind'].title(), o['x'], o['y'], f"{o['w']} × {o['h']} m" if o['kind'] == 'lander' else f"radius {o['radius']} m"))
    tip = f"{o['kind'].title()} at SLAM ({o['x']:.2f}, {o['y']:.2f}) m"
    if o['kind'] == 'lander':
        deg = -math.degrees(o['yaw'] + ang)
        obs.append(f'<g class="ob lander" data-l="obs" transform="translate({X:.2f} {svg_y(Y):.2f}) rotate({deg:.1f})" data-tip="{html.escape(tip)}, {o["w"]} × {o["h"]} m">'
                   f'<rect x="{-o["w"] / 2:.2f}" y="{-o["h"] / 2:.2f}" width="{o["w"]}" height="{o["h"]}" rx="0.15"/><text y="0.18">LANDER</text></g>')
    else:
        obs.append(f'<circle class="ob {o["kind"]}" data-l="obs" cx="{X:.2f}" cy="{svg_y(Y):.2f}" r="{o["radius"]}" data-tip="{html.escape(tip)}, radius {o["radius"]} m"/>')

pls = []
for name, p in cfg['placards']['positions'].items():
    X, Y = to_arena(p['x'], p['y'])
    i = name.split('_')[1]
    face = p['yaw'] + ang                       # the direction the placard faces, in the arena frame
    fx, fy = math.cos(face), math.sin(face)
    w = 0.6
    ax, ay = -fy * w / 2, fx * w / 2
    tip = f"Placard {i} (ArUco {cfg['placards']['aruco_dictionary']}) at SLAM ({p['x']:.2f}, {p['y']:.2f}) m, facing {math.degrees(p['yaw']):.0f}°"
    rows.insert(len(pls), (f'Placard {i}', p['x'], p['y'], f"facing {math.degrees(p['yaw']):.0f}°"))
    pls.append(f'<g class="pl" data-l="pl" tabindex="0" role="img" aria-label="{html.escape(tip)}" data-tip="{html.escape(tip)}">'
               f'<line class="pl-face" x1="{X - ax:.2f}" y1="{svg_y(Y - ay):.2f}" x2="{X + ax:.2f}" y2="{svg_y(Y + ay):.2f}"/>'
               f'<line class="pl-yaw" x1="{X:.2f}" y1="{svg_y(Y):.2f}" x2="{X + fx * 1.1:.2f}" y2="{svg_y(Y + fy * 1.1):.2f}"/>'
               f'<text x="{X + 0.45:.2f}" y="{svg_y(Y) - 0.4:.2f}">P{i}</text></g>')

# start pose: SLAM origin, facing SLAM +x
sx, sy = to_arena(0, 0)
hx, hy = math.cos(ang), math.sin(ang)
rows.insert(len(pls), ('Start pose', 0.0, 0.0, 'facing SLAM +x'))
rover = (f'<g class="rover" data-l="start" tabindex="0" role="img" aria-label="Start pose at the SLAM origin, facing SLAM +x" data-tip="Start pose: SLAM origin, arena ({sx:.2f}, {sy:.2f}) m, facing SLAM +x" '
         f'transform="translate({sx:.2f} {svg_y(sy):.2f}) rotate({-math.degrees(ang):.1f})">'
         f'<rect x="-0.55" y="-0.4" width="1.1" height="0.8" rx="0.12"/><path d="M0.15 -0.22 L0.5 0 L0.15 0.22 Z"/>'
         f'<line class="ax" x1="0" y1="0" x2="2.2" y2="0"/><text class="ax-t" x="2.35" y="0.15">x</text>'
         f'<line class="ax" x1="0" y1="0" x2="0" y2="-2.2"/><text class="ax-t" x="-0.15" y="-2.35">y</text></g>')

grid = ''.join(f'<line class="g{"5" if i % 5 == 0 else ""}" x1="{i}" y1="0" x2="{i}" y2="{SY}"/>' for i in range(1, int(SX) + 1)) + \
       ''.join(f'<line class="g{"5" if i % 5 == 0 else ""}" x1="0" y1="{SY - i}" x2="{SX}" y2="{SY - i}"/>' for i in range(1, int(SY) + 1))

neg = lambda t: t.replace('-', '\u2212')   # a real minus sign, as the site's other tables use
table_rows = ''.join(f'<tr><td>{html.escape(n)}</td><td>{neg(f"{x:.2f}")}</td><td>{neg(f"{y:.2f}")}</td><td>{neg(html.escape(d)).replace(' m', '\u00a0m')}</td></tr>' for n, x, y, d in rows)
n_obs = len(cfg['obstacles']['known_obstacles'])
cubes = cfg['cubes']

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Theseus GCS arena map</title>
<!-- Generated by portfolio/figures/theseus/build_arena.py from theseus-gcs/arena_config.yaml. -->
<style>
@font-face {{ font-family: "Chivo Mono"; src: url("../fonts/chivo-mono-latin.woff2") format("woff2"); font-weight: 500 600; font-display: swap; }}
@font-face {{ font-family: "Sanchez"; src: url("../fonts/sanchez-400-latin.woff2") format("woff2"); font-display: swap; }}
/* the site's palette and light theme: paper, panel, ink and the five accents */
:root {{ --paper: #ECEAE4; --paper2: #E1DED5; --panel: #F5F4F0; --ink: #1E2126; --mute: #5D626B; --line: rgb(30 33 38 / 0.2);
        --ind: #2E1499; --red: #BB0700; --yel: #FFC908; --org: #FF5102; --leaf: #3E9B5F;
        --mono: "Chivo Mono", ui-monospace, monospace; --serif: "Sanchez", Georgia, serif; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: transparent; }}
.gcs {{ background: var(--panel); color: var(--ink); font: 500 14px/1.4 var(--mono); border: 1px solid var(--line); overflow: hidden; }}
.bar {{ display: flex; flex-wrap: wrap; align-items: center; gap: 8px 10px; padding: 10px 14px; background: var(--panel); border-bottom: 2px solid var(--ink); }}
.brand {{ font: 600 0.9rem/1 var(--mono); letter-spacing: 1.5px; margin-right: 6px; }}
.pill {{ display: inline-flex; align-items: center; gap: 6px; padding: 4px 9px; border-radius: 999px; background: var(--paper); border: 1px solid var(--line);
        font: 600 0.7rem/1 var(--mono); letter-spacing: 0.5px; text-transform: uppercase; white-space: nowrap; }}
.pill i {{ width: 8px; height: 8px; border-radius: 50%; background: var(--mute); }}
.pill[data-s="ok"] i {{ background: var(--leaf); }}
.pill[data-s="warn"] i {{ background: var(--org); }}
.sim {{ margin-left: auto; font: 500 0.7rem/1 var(--mono); color: var(--mute); letter-spacing: 0.5px; text-transform: uppercase; }}
.body {{ display: grid; grid-template-columns: 1fr 220px; gap: 12px; padding: 12px 14px 14px; }}
.map {{ position: relative; background: #fff; border: 1px solid var(--line); padding: 8px; min-width: 0; }}
.map svg {{ display: block; width: 100%; height: auto; }}
.floor {{ fill: var(--paper); }}
.g {{ stroke: rgb(30 33 38 / 0.08); stroke-width: 0.03; }} .g5 {{ stroke: rgb(30 33 38 / 0.2); stroke-width: 0.05; }}
.edge {{ fill: none; stroke: var(--red); stroke-width: 0.12; }}
.z {{ fill: none; stroke-width: 0.08; stroke-dasharray: 0.4 0.25; }}
.geo {{ stroke: var(--org); }}
.nav {{ stroke: var(--leaf); }}
.crater {{ fill: rgb(93 98 107 / 0.16); stroke: var(--mute); stroke-width: 0.05; stroke-dasharray: 0.2 0.15; }}
.rock {{ fill: var(--mute); }}
.lander rect {{ fill: rgb(30 33 38 / 0.1); stroke: var(--ink); stroke-width: 0.08; }}
.lander text {{ fill: var(--ink); font: 600 0.45px var(--mono); text-anchor: middle; letter-spacing: 0.04px; }}
.pl-face {{ stroke: var(--ind); stroke-width: 0.22; stroke-linecap: round; }}
.pl-yaw {{ stroke: var(--ind); stroke-width: 0.07; }}
.pl text {{ fill: var(--ind); font: 600 0.6px var(--mono); }}
.rover rect {{ fill: var(--yel); stroke: var(--ink); stroke-width: 0.06; }} .rover path {{ fill: var(--ink); }}
.ax {{ stroke: var(--ink); stroke-width: 0.06; }} .ax-t {{ fill: var(--ink); font: 500 0.55px var(--mono); }}
[data-tip] {{ cursor: help; }}
.off {{ display: none; }}
.tip {{ position: absolute; pointer-events: none; padding: 5px 8px; background: var(--panel); border: 1px solid var(--ink); font: 500 0.72rem/1.35 var(--mono); color: var(--ink); max-width: 240px; opacity: 0; transition: opacity 0.12s; }}
.side {{ display: grid; gap: 10px; align-content: start; }}
.card {{ background: #fff; border: 1px solid var(--line); padding: 9px 10px; }}
.card h4 {{ margin: 0 0 7px; font: 600 0.7rem/1 var(--mono); letter-spacing: 1px; text-transform: uppercase; color: var(--mute); }}
.layers label {{ display: flex; align-items: center; gap: 8px; font: 500 0.76rem/1.3 var(--mono); color: var(--ink); cursor: pointer; min-height: 30px; }}
.layers input {{ accent-color: var(--ind); width: 16px; height: 16px; margin: 0; flex: none; }}
.sw {{ width: 14px; height: 4px; border-radius: 2px; flex: none; }}
.steps {{ display: grid; gap: 6px; }}
.steps button {{ font: 600 0.7rem/1 var(--mono); letter-spacing: 0.6px; text-transform: uppercase; text-align: left; color: var(--ink); background: var(--panel);
                border: 1px solid var(--ink); padding: 9px 9px; cursor: pointer; }}
.steps button:disabled {{ color: var(--mute); border-color: var(--line); cursor: not-allowed; }}
.steps button.done {{ border-color: var(--leaf); color: var(--ink); background: rgb(62 155 95 / 0.12); }}
.mode {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; border: 1px solid var(--ink); overflow: hidden; }}
.mode button {{ border: 0; text-align: center; }}
.mode button[aria-pressed="true"] {{ background: var(--ink); color: var(--panel); }}
button:focus-visible, input:focus-visible {{ outline: 2px solid var(--ind); outline-offset: 2px; }}
.fine {{ margin: 0; font: 400 0.82rem/1.5 var(--serif); color: var(--mute); }}
.tbl {{ padding: 0 14px 12px; font: 500 0.78rem/1.45 var(--mono); color: var(--ink); }}
.tbl summary {{ cursor: pointer; padding: 4px 0; font-family: var(--serif); color: var(--mute); }}
.tbl table {{ border-collapse: collapse; margin-top: 6px; font-variant-numeric: tabular-nums; }}
.tbl th, .tbl td {{ padding: 3px 16px 3px 0; border-bottom: 1px solid var(--line); text-align: left; font-weight: 500; }}
.tbl th {{ color: var(--mute); }}
.tbl th:nth-child(2), .tbl td:nth-child(2), .tbl th:nth-child(3), .tbl td:nth-child(3) {{ text-align: right; }}   /* numbers line up */
summary:focus-visible, .pl:focus-visible, .rover:focus-visible {{ outline: 2px solid var(--ind); outline-offset: 2px; }}
@media (max-width: 620px) {{ .body {{ grid-template-columns: 1fr; }} .sim {{ margin-left: 0; }} }}
</style>
</head>
<body>
<div class="gcs">
  <div class="bar">
    <span class="brand">THESEUS GCS</span>
    <span class="pill" id="p-cfg" data-s="warn"><i></i><span>Config not sent</span></span>
    <span class="pill" id="p-stack"><i></i><span>Stack down</span></span>
    <span class="pill" id="p-mode"><i></i><span>Teleop</span></span>
    <span class="sim">Simulation &middot; no rover connected</span>
  </div>
  <div class="body">
    <div class="map">
      <svg viewBox="-0.6 -0.6 {SX + 1.2:.1f} {SY + 1.2:.1f}" role="img" aria-label="Top-down map of the {SX} by {SY} m competition arena with its zones, placards, obstacles and the rover's start pose">
        <rect class="floor" x="0" y="0" width="{SX}" height="{SY}"/>
        {grid}
        <rect class="edge" data-l="edge" x="0" y="0" width="{SX}" height="{SY}"><title>Arena edge: e-stop, motors cut</title></rect>
        {''.join(shapes)}
        {''.join(obs)}
        {''.join(pls)}
        {rover}
      </svg>
      <div class="tip" id="tip"></div>
    </div>
    <div class="side">
      <div class="card layers">
        <h4>Layers</h4>
        <label><input type="checkbox" data-layer="edge" checked><span class="sw" style="background:var(--red)"></span>E-stop edge</label>
        <label><input type="checkbox" data-layer="geo" checked><span class="sw" style="background:var(--org)"></span>Geofence slow zone</label>
        <label><input type="checkbox" data-layer="nav" checked><span class="sw" style="background:var(--leaf)"></span>Planner bounds</label>
        <label><input type="checkbox" data-layer="pl" checked><span class="sw" style="background:var(--ind)"></span>Placards ({len(pls)})</label>
        <label><input type="checkbox" data-layer="obs" checked><span class="sw" style="background:var(--mute)"></span>Obstacles ({n_obs})</label>
        <label><input type="checkbox" data-layer="start" checked><span class="sw" style="background:var(--yel);outline:1px solid var(--ink)"></span>Start pose and SLAM axes</label>
      </div>
      <div class="card">
        <h4>Autonomy</h4>
        <div class="steps">
          <button type="button" id="b-cfg">1 &middot; Send config</button>
          <button type="button" id="b-stack" disabled>2 &middot; Launch stack</button>
          <div class="mode" role="group" aria-label="Drive mode">
            <button type="button" id="b-tele" aria-pressed="true">Teleop</button>
            <button type="button" id="b-auto" aria-pressed="false" disabled>Auto</button>
          </div>
        </div>
      </div>
      <p class="fine">{cubes['count']} cubes ({', '.join(cubes['colors'])}) are placed at random on the day, so the map has none; the rover finds them.</p>
    </div>
  </div>
  <details class="tbl"><summary>Placards, start pose and obstacles as a table</summary>
    <table><thead><tr><th>Item</th><th>SLAM x (m)</th><th>SLAM y (m)</th><th>Size or facing</th></tr></thead><tbody>{table_rows}</tbody></table>
  </details>
</div>
<script>
(function () {{
  var $ = function (id) {{ return document.getElementById(id); }};
  document.querySelectorAll('[data-layer]').forEach(function (cb) {{
    cb.addEventListener('change', function () {{
      document.querySelectorAll('[data-l="' + cb.dataset.layer + '"]').forEach(function (el) {{ el.classList.toggle('off', !cb.checked); }});
    }});
  }});
  var tip = $('tip'), map = document.querySelector('.map');
  function showTip(el, x, y) {{
    var r = map.getBoundingClientRect();
    tip.textContent = el.dataset.tip; tip.style.opacity = 1;
    tip.style.left = Math.max(0, Math.min(x - r.left + 12, r.width - 250)) + 'px'; tip.style.top = (y - r.top + 12) + 'px';
  }}
  function hideTip() {{ tip.style.opacity = 0; }}
  document.querySelectorAll('[data-tip]').forEach(function (el) {{
    el.addEventListener('pointermove', function (e) {{ if (e.pointerType === 'mouse') showTip(el, e.clientX, e.clientY); }});
    el.addEventListener('pointerdown', function (e) {{ e.stopPropagation(); showTip(el, e.clientX, e.clientY); }});   // a tap shows it until the next tap
    el.addEventListener('pointerleave', function (e) {{ if (e.pointerType === 'mouse') hideTip(); }});
    el.addEventListener('focus', function () {{ var b = el.getBoundingClientRect(); showTip(el, b.right, b.top); }});
    el.addEventListener('blur', hideTip);
  }});
  map.addEventListener('pointerdown', hideTip);
  // Map text is sized in metres, so on a phone it shrank to 4 to 6 px. Keep placard and axis labels at 10 px or more;
  // LANDER has to fit inside its 2.4 m box, so where it would be under 8 px it is hidden (the obstacle stays).
  var msvg = map.querySelector('svg');
  function sizeLabels() {{
    var ppm = msvg.getBoundingClientRect().width / msvg.viewBox.baseVal.width; if (!ppm) return;
    msvg.querySelectorAll('.pl text').forEach(function (t) {{ t.style.fontSize = Math.max(0.6, 10 / ppm) + 'px'; }});
    msvg.querySelectorAll('.ax-t').forEach(function (t) {{ t.style.fontSize = Math.max(0.55, 10 / ppm) + 'px'; }});
    var lf = Math.min(0.57, Math.max(0.45, 9 / ppm));
    msvg.querySelectorAll('.lander text').forEach(function (t) {{ t.style.fontSize = lf + 'px'; t.style.display = lf * ppm < 8 ? 'none' : ''; }});
  }}
  sizeLabels(); new ResizeObserver(sizeLabels).observe(msvg);
  function pill(id, s, text) {{ var p = $(id); p.dataset.s = s; p.lastElementChild.textContent = text; }}
  $('b-cfg').addEventListener('click', function () {{
    pill('p-cfg', 'ok', 'Config sent'); this.classList.add('done'); this.textContent = '\u2713 Config sent'; $('b-stack').disabled = false;   // confirmed where the reader clicked
  }});
  $('b-stack').addEventListener('click', function () {{
    var b = this; b.disabled = true; pill('p-stack', 'warn', 'Starting\\u2026');
    b.textContent = 'Starting\u2026';
    setTimeout(function () {{ pill('p-stack', 'ok', 'Stack up'); b.classList.add('done'); b.textContent = '\u2713 Stack up'; $('b-auto').disabled = false; }}, 900);
  }});
  function mode(auto) {{
    $('b-auto').setAttribute('aria-pressed', auto); $('b-tele').setAttribute('aria-pressed', !auto);
    pill('p-mode', auto ? 'ok' : '', auto ? 'Auto' : 'Teleop');
  }}
  $('b-auto').addEventListener('click', function () {{ mode(true); }});
  $('b-tele').addEventListener('click', function () {{ mode(false); }});
}})();
</script>
</body>
</html>
'''
out.write_text(page)
print('wrote', out, len(pls), 'placards,', n_obs, 'obstacles')
