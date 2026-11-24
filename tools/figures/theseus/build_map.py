"""Top-down map of the ARCh 2026 arena from Theseus V's own FAST-LIO2 map, with the autonomous run's path.

Usage: python3 -I build_map.py src/theseus-arena-cloud.bin <theseus-autonomy repo> <arena_config.yaml> <out-dir>
Writes <out-dir>/theseus-map.html (the figure page) and <out-dir>/theseus-map-cloud.webp (the point layer).

Sources, and how they are joined:
- The cloud: 150,000 points of the arena map in theseus-autonomy's docs/assets/results/arena_viewer.html
  (13 bytes a point: x, y, z float32 in metres, intensity uint8). The export that made the viewer subtracted the
  cloud mean and did not store it, so the cloud is placed on the arena by a 2D fit: a rotation and shift that
  match its crater rims to the ground-truth scan drawn in arena_mission_overview.png (the overlay was checked by eye:
  the box structure and the crater rims line up to a few tenths of a metre). FIT below holds the result.
- The path: the run kept 6 SLAM keyposes. Their ground-truth positions are read from the markers in
  arena_mission_overview.png; converted back with the repo's arena_slam_to_ply_transform.json they match the
  hardware-run analysis to about 0.05 m. The path is drawn as straight lines between them, so it is simplified.
- The cube detections: the two detection markers in the same figure.
- The arena: arena_to_ply_transform.json takes ground-truth (PLY) positions to the competition config's frame,
  and the config's report_transform takes that frame onto the arena, the same frame as the GCS replica figure.
"""
import json
import sys
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

cloud_bin, repo, cfg_path, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])

FIT = (-17.75, 10.13, 1.33)          # cloud -> ground truth: rotation (deg), shift (m); see the docstring
KEYPOSES = [(6.60, -7.23), (10.55, -8.03), (11.97, -4.22), (9.66, -0.77), (10.37, 3.18), (14.10, 4.58)]   # ground truth, m
CUBES = [('Blue cube', (14.04, -5.66)), ('Green cube', (15.23, 2.02))]

raw = np.fromfile(cloud_bin, dtype=np.uint8).reshape(-1, 13)
xyz = raw[:, :12].copy().view('<f4').reshape(-1, 3).astype(float)

a2p = json.loads((repo / 'docs/assets/results/arena_to_ply_transform.json').read_text())
RA, tA = np.array(a2p['arena_to_ply_R']), np.array(a2p['arena_to_ply_t'])
cfg = yaml.safe_load(cfg_path.read_text())['/**']['ros__parameters']['arena']
tf = cfg['report_transform']
SX, SY = cfg['size_x'], cfg['size_y']


def to_arena(ply):
    """Ground-truth (PLY) metres -> arena metres, origin at the arena corner, y up (the GCS replica's frame)."""
    c = (np.atleast_2d(ply) - tA) @ RA                                    # config (planned SLAM) frame
    ca, sa = np.cos(tf['angle_rad']), np.sin(tf['angle_rad'])
    return np.c_[tf['origin_x'] + ca * c[:, 0] - sa * c[:, 1], tf['origin_y'] + sa * c[:, 0] + ca * c[:, 1]]


r = np.deg2rad(FIT[0])
Rf = np.array([[np.cos(r), -np.sin(r)], [np.sin(r), np.cos(r)]])
P = to_arena(xyz[:, :2] @ Rf.T + FIT[1:])
z = xyz[:, 2]

# view: the arena plus a margin of its surroundings
M = 2.0
VX0, VX1, VY0, VY1 = -M, SX + M, -M, SY + M
keep = (P[:, 0] > VX0) & (P[:, 0] < VX1) & (P[:, 1] > VY0) & (P[:, 1] < VY1)
P, z = P[keep], z[keep]

# height above the local ground (the floor tilts by ~0.6 m across the map): 10th percentile per 1.5 m cell, smoothed
G = 1.5
gx, gy = ((P[:, 0] - VX0) // G).astype(int), ((P[:, 1] - VY0) // G).astype(int)
nx, ny = gx.max() + 1, gy.max() + 1
ground = np.full((ny, nx), np.nan)
for (i, j) in set(zip(gy.tolist(), gx.tolist())):
    sel = (gy == i) & (gx == j)
    if sel.sum() >= 8:
        ground[i, j] = np.percentile(z[sel], 10)
fill = np.nanmedian(ground)
g = np.where(np.isnan(ground), fill, ground)
pad = np.pad(g, 1, mode='edge')
g = sum(pad[1 + di:1 + di + ny, 1 + dj:1 + dj + nx] for di in (-1, 0, 1) for dj in (-1, 0, 1)) / 9
h = z - g[gy, gx]

# point layer: light lavender on the floor to the site's ink on rims, walls and fences; low points first
PPM = 48                                       # output pixels per metre (about 2x the figure's display size)
SS = 2                                         # supersampling
W, H = int((VX1 - VX0) * PPM), int((VY1 - VY0) * PPM)
lo, hi = np.array([214, 208, 238]), np.array([46, 20, 153])
k = np.clip((h + 0.05) / 0.85, 0, 1) ** 0.8
rgb = (lo + (hi - lo) * k[:, None]).astype(np.uint8)
order = np.argsort(h)
canvas = np.full((H * SS, W * SS, 3), 255, np.uint8)
px = ((P[:, 0] - VX0) * PPM * SS).astype(int)
py = ((VY1 - P[:, 1]) * PPM * SS).astype(int)
rad = 2                                        # dot radius in supersampled pixels (~0.04 m)
for dy in range(-rad, rad + 1):
    for dx in range(-rad, rad + 1):
        if dx * dx + dy * dy > rad * rad + 1:
            continue
        xx, yy = px[order] + dx, py[order] + dy
        ok = (xx >= 0) & (xx < W * SS) & (yy >= 0) & (yy < H * SS)
        canvas[yy[ok], xx[ok]] = rgb[order][ok]
img = Image.fromarray(canvas).resize((W, H), Image.LANCZOS)
img.save(out / 'theseus-map-cloud.webp', quality=82, method=6)
import hashlib
CLOUD_V = hashlib.sha256((out / 'theseus-map-cloud.webp').read_bytes()).hexdigest()[:8]   # cache-busting tag

# overlay, in arena metres (SVG y down)
sx = lambda x: x - VX0
sy = lambda y: VY1 - y
kp = to_arena(np.array(KEYPOSES))
path = ' '.join(f'{"M" if i == 0 else "L"}{sx(x):.2f} {sy(y):.2f}' for i, (x, y) in enumerate(kp))
cubes = [(n, to_arena(np.array(p))[0]) for n, p in CUBES]


def diamond(x, y, s=0.42):
    return f'M{sx(x):.2f} {sy(y) - s:.2f} L{sx(x) + s:.2f} {sy(y):.2f} L{sx(x):.2f} {sy(y) + s:.2f} L{sx(x) - s:.2f} {sy(y):.2f} Z'


(x0, y0), (x5, y5) = kp[0], kp[-1]
cube_svg = ''.join(
    f'<g><title>{n} detected, arena ({x:.1f}, {y:.1f}) m</title><path class="cube" d="{diamond(x, y)}"/>'
    f'<text class="lab" x="{sx(x) + 0.7:.2f}" y="{sy(y) + 0.3:.2f}">{n}</text></g>' for n, (x, y) in cubes)
rows = ''.join(f'<tr><td>{"Start" if i == 0 else "End" if i == len(kp) - 1 else i}</td><td>{x:.1f}</td><td>{y:.1f}</td></tr>'
               for i, (x, y) in enumerate(kp))
rows += ''.join(f'<tr><td>{n}</td><td>{x:.1f}</td><td>{y:.1f}</td></tr>' for n, (x, y) in cubes)
VW, VH = VX1 - VX0, VY1 - VY0

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Theseus V arena map</title>
<!-- Generated by portfolio/figures/theseus/build_map.py from the rover's FAST-LIO2 arena map and the run's keyposes. -->
<style>
@font-face {{ font-family: "Sanchez"; src: url("../fonts/sanchez-400-latin.woff2") format("woff2"); font-display: swap; }}
:root {{ --ink: #2E1499; --muted: #5E4FA8; --grid: #ECE9F6; --path: #E8590C; --surface: #FFFFFF; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: var(--surface); color: var(--ink); font: 14px/1.45 "Sanchez", Georgia, serif; }}
.wrap {{ padding: 14px 16px 12px; display: grid; gap: 8px; }}
svg {{ display: block; width: 100%; height: auto; }}
.edge {{ fill: none; stroke: var(--ink); stroke-width: 1.5px; vector-effect: non-scaling-stroke; }}
.path {{ fill: none; stroke: var(--path); stroke-width: 2.5px; stroke-linejoin: round; vector-effect: non-scaling-stroke; }}
.ring {{ fill: var(--surface); stroke: var(--path); stroke-width: 2px; vector-effect: non-scaling-stroke; }}
.end {{ fill: var(--path); stroke: var(--surface); stroke-width: 1.5px; vector-effect: non-scaling-stroke; }}
.cube {{ fill: var(--surface); stroke: var(--ink); stroke-width: 1.5px; vector-effect: non-scaling-stroke; }}
.lab {{ fill: var(--ink); font-size: 0.78px; paint-order: stroke; stroke: rgb(255 255 255 / 0.9); stroke-width: 0.22px; stroke-linejoin: round; }}
.muted {{ fill: var(--muted); }}
.bar {{ stroke: var(--ink); stroke-width: 1.5px; vector-effect: non-scaling-stroke; }}
details {{ font-size: 13px; }}
summary {{ cursor: pointer; color: var(--muted); }}
table {{ border-collapse: collapse; margin-top: 6px; }}
th, td {{ text-align: left; padding: 3px 16px 3px 0; border-bottom: 1px solid var(--grid); font-weight: 400; font-variant-numeric: tabular-nums; }}
th:nth-child(n+2), td:nth-child(n+2) {{ text-align: right; }}   /* numbers line up */
th {{ color: var(--muted); }}
@media (max-width: 520px) {{ .wrap {{ padding: 10px; }} .lab {{ font-size: 1.25px; stroke-width: 0.3px; }} }}
</style>
</head>
<body>
<div class="wrap">
  <svg viewBox="0 0 {VW:.2f} {VH:.2f}" role="img" aria-label="Top-down LiDAR map of the {SX} by {SY} m arena, with the rover's autonomous path from start to end and the two cubes it detected">
    <image href="theseus-map-cloud.webp?v={CLOUD_V}" x="0" y="0" width="{VW:.2f}" height="{VH:.2f}" preserveAspectRatio="none"/>
    <rect class="edge" x="{sx(0):.2f}" y="{sy(SY):.2f}" width="{SX}" height="{SY}"><title>Arena edge, {SX} by {SY} m</title></rect>
    <text class="lab muted" x="{sx(0) + 0.4:.2f}" y="{sy(SY) + 1.1:.2f}">Arena edge</text>
    <path class="path" d="{path}"><title>Autonomous path: straight lines between the run's 6 SLAM keyposes</title></path>
    <circle class="ring" cx="{sx(x0):.2f}" cy="{sy(y0):.2f}" r="0.38"><title>Start, arena ({x0:.1f}, {y0:.1f}) m</title></circle>
    <text class="lab" x="{sx(x0) + 0.65:.2f}" y="{sy(y0) + 1.15:.2f}">Start</text>
    <rect class="end" x="{sx(x5) - 0.36:.2f}" y="{sy(y5) - 0.36:.2f}" width="0.72" height="0.72"><title>End, arena ({x5:.1f}, {y5:.1f}) m</title></rect>
    <text class="lab" x="{sx(x5) - 0.5:.2f}" y="{sy(y5) - 0.75:.2f}" text-anchor="end">End</text>
    {cube_svg}
    <g transform="translate({sx(SX) - 5:.2f} {sy(0) + 1.15:.2f})">
      <line class="bar" x1="0" y1="0" x2="5" y2="0"/><line class="bar" x1="0" y1="-0.25" x2="0" y2="0.25"/><line class="bar" x1="5" y1="-0.25" x2="5" y2="0.25"/>
      <text class="lab" x="-0.45" y="0" text-anchor="end" dominant-baseline="middle">5 m</text>
    </g>
  </svg>
  <details><summary>Path and detections as a table</summary>
    <table><thead><tr><th>Point</th><th>x (m)</th><th>y (m)</th></tr></thead><tbody>{rows}</tbody></table>
  </details>
</div>
</body>
</html>
'''
(out / 'theseus-map.html').write_text(page)
print('wrote', out / 'theseus-map.html', f'{W}x{H}', round((out / "theseus-map-cloud.webp").stat().st_size / 1024), 'KB',
      'start', kp[0].round(2), 'end', kp[-1].round(2))
