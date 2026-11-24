"""Render real CAD meshes as flat-shaded ("toon") icon layers in the Anatomy kit's camera and palette.

Usage: python3 -I mesh_render.py <model.json> <out-dir>

model.json:
  meshes      folder of binary STLs (mm, design frame), one per group
  frame       {"scale": s, "x": [cx, cy, cz, k], "y": [...], "z": [...]}: icon coordinate = s * (c . p + k),
              so each icon axis is a signed combination of the design axes plus an offset
  groups      {name: {"style": paper|dark|accent|yellow|metal|glass, "layer": body|glass}}
  azimuth, elevation, size (viewBox, 300), pad, extra (icon-frame points to keep in view, e.g. the target),
  keypoints   {name: [x, y, z] in the design frame}, projected for the SVG overlays
  out_px      output pixels (600 = 2x the 300 viewBox), supersample (4)
Writes <name>-<layer>.webp layers with transparent backgrounds, and <name>.json with the kit projection
P = {origin, scale, azimuth, elevation} (so build.mjs draws its vector parts in the same camera) and the
projected keypoints in viewBox units.

Projection matches iso-kit.mjs: unit screen point u(p) = UNIT * [x sinA - y cosA, (x cosA + y sinA) sinE - z cosE],
screen = origin + scale * u(p); depth = (x cosA + y sinA) cosE + z sinE (larger is nearer). Light as lathe.mjs.
"""
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

UNIT = math.sqrt(1.6)
LIGHT_UP = 1.2
INK = (46, 20, 153)            # #2E1499 outline
CREASE = (169, 158, 219)       # #A99EDB crease
STYLES = {                     # lit -> dark, four bands
    'paper':  [(255, 255, 255), (244, 242, 251), (233, 229, 247), (221, 215, 242)],
    'dark':   [(91, 75, 176), (75, 59, 168), (59, 44, 143), (46, 31, 122)],
    'accent': [(244, 138, 130), (232, 88, 79), (210, 69, 61), (184, 55, 48)],
    'yellow': [(255, 226, 122), (255, 201, 8), (230, 180, 0), (204, 159, 0)],
    'metal':  [(236, 233, 248), (217, 211, 240), (199, 191, 232), (181, 171, 222)],
    'glass':  [(232, 238, 255), (219, 228, 252), (206, 218, 249), (193, 208, 246)],
}


def read_stl(path):
    b = Path(path).read_bytes()
    n = struct.unpack_from('<I', b, 80)[0]
    if 84 + 50 * n != len(b):
        raise ValueError(f'{path}: not a binary STL of {n} triangles')
    a = np.frombuffer(b, dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]), count=n, offset=84)
    return a['v'].astype(np.float64)


def main():
    cfg = json.loads(Path(sys.argv[1]).read_text())
    out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    name = cfg['name']
    A, E = math.radians(cfg['azimuth']), math.radians(cfg.get('elevation', 30))
    sA, cA, sE, cE = math.sin(A), math.cos(A), math.sin(E), math.cos(E)
    fr = cfg['frame']; s = fr['scale']
    M = np.array([fr['x'][:3], fr['y'][:3], fr['z'][:3]], dtype=float)
    off = np.array([fr['x'][3], fr['y'][3], fr['z'][3]], dtype=float)
    to_icon = lambda p: s * (p @ M.T + off)

    tris, gid, layers, styles = [], [], [], []
    names = list(cfg['groups'])
    for g in list(names):
        raw = read_stl(Path(cfg['meshes']) / f'{g}.stl')
        spec = cfg['groups'][g]
        parts = [(g, spec['style'], raw)]
        hub = spec.get('hub')                    # optional: colour triangles near wheel axes (hubs) differently
        if hub:
            ax = {'x': 0, 'y': 1, 'z': 2}[hub['axis']]; other = [i for i in range(3) if i != ax]
            cen = raw.mean(1)[:, other]
            dist = np.min([np.hypot(*(cen - np.array(c)).T) for c in hub['centers']], axis=0)
            inner = dist < hub['r']
            parts = [(g, spec['style'], raw[~inner]), (g + ':hub', hub['style'], raw[inner])]
        for pname, style, mesh in parts:
            i = len(styles)
            v = to_icon(mesh)
            tris.append(v); gid.append(np.full(len(v), i)); styles.append(style); layers.append(spec.get('layer', 'body'))
    T = np.concatenate(tris); G = np.concatenate(gid)

    def unit_xy(p):
        return UNIT * np.stack([p[..., 0] * sA - p[..., 1] * cA, (p[..., 0] * cA + p[..., 1] * sA) * sE - p[..., 2] * cE], -1)

    pts = np.concatenate([T.reshape(-1, 3), np.array(cfg.get('extra', []), dtype=float).reshape(-1, 3)])
    u = unit_xy(pts)
    size, pad = cfg.get('size', 300), cfg.get('pad', 34)
    (l, t), (r, b) = u.min(0), u.max(0)
    scale = min((size - 2 * pad) / (r - l), (size - 2 * pad) / (b - t))
    origin = [size / 2 - (l + r) / 2 * scale, size / 2 - (t + b) / 2 * scale]
    P = {'origin': origin, 'scale': scale, 'azimuth': cfg['azimuth'], 'elevation': cfg.get('elevation', 30)}

    px, ss = cfg.get('out_px', 600), cfg.get('supersample', 4)
    W = px * ss; f = W / size
    scr = (np.array(origin) + unit_xy(T) * scale) * f                        # (n, 3, 2) supersampled pixels
    dep = (T[..., 0] * cA + T[..., 1] * sA) * cE + T[..., 2] * sE              # (n, 3)
    nrm = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    ln = np.linalg.norm(nrm, axis=1); ok = ln > 1e-12
    nrm[ok] /= ln[ok, None]
    view = np.array([cA * cE, sA * cE, sE])
    nrm[nrm @ view < 0] *= -1                                                # two-sided: face the viewer
    L = np.array([-sA, cA, LIGHT_UP]); L /= np.linalg.norm(L)
    lam = nrm @ L
    band = np.clip(np.digitize(lam, [0.75, 0.45, 0.1][::-1]), 0, 3)          # 0..3, low lam -> 0
    band = 3 - band                                                          # 0 = lit
    order = np.argsort(dep.mean(1))                                          # far to near, for stable ties

    def raster(sel):
        zb = np.full((W, W), -np.inf); idb = np.full((W, W), -1, np.int32); bb = np.zeros((W, W), np.int8)
        for i in order[sel[order]]:
            (x0, y0), (x1, y1), (x2, y2) = scr[i]
            xmin, xmax = int(max(0, math.floor(min(x0, x1, x2)))), int(min(W - 1, math.ceil(max(x0, x1, x2))))
            ymin, ymax = int(max(0, math.floor(min(y0, y1, y2)))), int(min(W - 1, math.ceil(max(y0, y1, y2))))
            if xmin > xmax or ymin > ymax:
                continue
            den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(den) < 1e-9:
                continue
            xs, ys = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
            w0 = ((y1 - y2) * (xs - x2) + (x2 - x1) * (ys - y2)) / den
            w1 = ((y2 - y0) * (xs - x2) + (x0 - x2) * (ys - y2)) / den
            w2 = 1 - w0 - w1
            inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not inside.any():
                continue
            z = w0 * dep[i, 0] + w1 * dep[i, 1] + w2 * dep[i, 2]
            sub = zb[ymin:ymax + 1, xmin:xmax + 1]
            win = inside & (z > sub)
            sub[win] = z[win]
            idb[ymin:ymax + 1, xmin:xmax + 1][win] = G[i]
            bb[ymin:ymax + 1, xmin:xmax + 1][win] = band[i]
        return zb, idb, bb

    def paint(zb, idb, bb, alpha_of):
        img = np.zeros((W, W, 4), np.uint8)
        filled = idb >= 0
        for gi, st in enumerate(styles):
            for k in range(4):
                m = filled & (idb == gi) & (bb == k)
                if m.any():
                    img[m, :3] = STYLES[st][k]; img[m, 3] = alpha_of(gi)
        # outlines: silhouette and group boundaries in ink; depth steps in ink; band changes as light creases
        def edge(a, b_):
            e = np.zeros((W, W), bool)
            e[:, 1:] |= b_(a[:, 1:], a[:, :-1]); e[1:, :] |= b_(a[1:, :], a[:-1, :])
            return e
        ink = edge(idb, lambda p, q: p != q)
        zf = np.where(filled, zb, np.nan)
        step = cfg.get('depth_step', 1.2)
        dz = np.zeros((W, W), bool)
        dz[:, 1:] |= np.abs(zf[:, 1:] - zf[:, :-1]) > step; dz[1:, :] |= np.abs(zf[1:, :] - zf[:-1, :]) > step
        ink |= dz & filled
        crease = edge(bb, lambda p, q: p != q) & ~ink & filled
        r = max(1, ss // 2)
        def grow(m):
            g = m.copy()
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx * dx + dy * dy <= r * r:
                        g |= np.roll(np.roll(m, dy, 0), dx, 1)
            return g
        ink = grow(ink); crease = grow(crease) & ~ink
        img[crease, :3] = CREASE; img[crease, 3] = np.maximum(img[crease, 3], 255)
        img[ink, :3] = INK; img[ink, 3] = 255
        return Image.fromarray(img, 'RGBA').reduce(ss)

    body = np.array([layers[g] == 'body' for g in G])
    zb, idb, bb = raster(body)
    paint(zb, idb, bb, lambda gi: 255).save(out / f'{name}-body.webp', quality=92, method=6)
    # other layers: 'glass' is see-through and hidden behind opaque parts; any other named layer (e.g. a part
    # that lifts out on hover) is drawn whole, on top, so it can move. layer_opts overrides either default.
    opts = cfg.get('layer_opts', {})
    for lname in sorted(set(layers) - {'body'}):
        o = {'alpha': 110, 'occlude': True} if lname == 'glass' else {'alpha': 255, 'occlude': False}
        o.update(opts.get(lname, {}))
        sel = np.array([layers[g] == lname for g in G])
        lz, lid, lb = raster(sel)
        if o['occlude']:
            lid[lz < zb] = -1
        paint(lz, lid, lb, lambda gi, a=o['alpha']: a).save(out / f'{name}-{lname}.webp', quality=92, method=6)

    kp = {k: list(np.round(np.array(origin) + unit_xy(to_icon(np.array(v, float))) * scale, 2)) for k, v in cfg.get('keypoints', {}).items()}
    jpath = Path(sys.argv[3]) if len(sys.argv) > 3 else out / f'{name}.json'
    jpath.write_text(json.dumps({'P': P, 'keypoints': kp, 'size': size, 'layers': sorted(set(layers)), 'groups': names}, indent=1))
    print('wrote', name, 'P scale', round(scale, 3), 'keypoints', kp)


if __name__ == '__main__':
    main()
