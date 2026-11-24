"""Split a KiCad GLB export into binary STLs grouped by material colour, for mesh_render.py.

Usage: python3 -I glb_split.py <board.glb> <out-dir> [--list]
  --list   print each material's colour, triangle count and bounding box, and stop
Rules (edit RULES below) map each material's base colour to an icon style group:
the board body, dark parts, metal parts and light parts. Output is in millimetres with Z up
(glTF is metres, Y up), so it matches the other CAD exports.
"""
import json
import struct
import sys
from pathlib import Path

import numpy as np

COMP = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NCOMP = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def load(path):
    b = Path(path).read_bytes()
    assert b[:4] == b'glTF'
    off, js, binc = 12, None, None
    while off < len(b):
        ln, typ = struct.unpack_from('<II', b, off)
        chunk = b[off + 8:off + 8 + ln]
        if typ == 0x4E4F534A: js = json.loads(chunk)
        elif typ == 0x004E4942: binc = chunk
        off += 8 + ln
    return js, binc


def accessor(js, binc, i):
    a = js['accessors'][i]; v = js['bufferViews'][a['bufferView']]
    dt = COMP[a['componentType']]; n = NCOMP[a['type']]
    start = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = v.get('byteStride', 0)
    item = np.dtype(dt).itemsize * n
    if stride and stride != item:
        raw = np.frombuffer(binc, dtype=np.uint8, count=stride * a['count'], offset=start).reshape(a['count'], stride)[:, :item]
        return np.frombuffer(raw.tobytes(), dtype=dt).reshape(a['count'], n)
    return np.frombuffer(binc, dtype=dt, count=a['count'] * n, offset=start).reshape(a['count'], n)


def node_matrix(nd):
    if 'matrix' in nd:
        return np.array(nd['matrix'], float).reshape(4, 4).T
    M = np.eye(4)
    if 'scale' in nd: M = np.diag(list(nd['scale']) + [1]) @ M
    if 'rotation' in nd:
        x, y, z, w = nd['rotation']
        R = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                      [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                      [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        RM = np.eye(4); RM[:3, :3] = R; M = RM @ M
    if 'translation' in nd:
        T = np.eye(4); T[:3, 3] = nd['translation']; M = T @ M
    return M


def triangles(js, binc):
    """Yield (material index, (n, 3, 3) triangles in mm, Z up) for every mesh primitive in the scene."""
    out = []
    def walk(i, parent):
        nd = js['nodes'][i]; M = parent @ node_matrix(nd)
        if 'mesh' in nd:
            for pr in js['meshes'][nd['mesh']]['primitives']:
                if pr.get('mode', 4) != 4: continue
                P = accessor(js, binc, pr['attributes']['POSITION']).astype(float)
                idx = accessor(js, binc, pr['indices']).reshape(-1) if 'indices' in pr else np.arange(len(P))
                Pw = (np.c_[P, np.ones(len(P))] @ M.T)[:, :3]
                Pw = Pw[:, [0, 2, 1]] * np.array([1, -1, 1]) * 1000.0      # glTF (Y up, metres) -> Z up, mm
                out.append((pr.get('material', -1), Pw[idx.reshape(-1, 3)]))
        for c in nd.get('children', []):
            walk(c, M)
    for r in js['scenes'][js.get('scene', 0)]['nodes']:
        walk(r, np.eye(4))
    return out


def colour(js, m):
    if m < 0: return (1, 1, 1)
    pbr = js['materials'][m].get('pbrMetallicRoughness', {})
    return tuple(pbr.get('baseColorFactor', [1, 1, 1, 1])[:3])


def write_stl(path, tris):
    tris = np.asarray(tris, np.float32)
    with open(path, 'wb') as f:
        f.write(b'\0' * 80); f.write(struct.pack('<I', len(tris)))
        rec = np.zeros(len(tris), dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
        rec['v'] = tris; f.write(rec.tobytes())


def style_of(rgb):
    r, g, b = rgb; lum = 0.3 * r + 0.59 * g + 0.11 * b
    if g > r * 1.3 and g > b and lum < 0.6: return 'board'          # soldermask green
    if lum < 0.22: return 'dark'                                     # black plastic, IC packages
    if r > 0.6 and g > 0.45 and b < 0.35: return 'gold'              # pads, gold pins
    if abs(r - g) < 0.08 and abs(g - b) < 0.08 and lum > 0.55: return 'light'   # silkscreen, white bodies
    return 'metal'


if __name__ == '__main__':
    js, binc = load(sys.argv[1])
    parts = triangles(js, binc)
    if '--list' in sys.argv:
        agg = {}
        for m, t in parts:
            k = (m, tuple(round(c, 2) for c in colour(js, m)))
            agg.setdefault(k, []).append(t)
        for (m, c), ts in sorted(agg.items(), key=lambda kv: -sum(len(t) for t in kv[1])):
            allt = np.concatenate(ts).reshape(-1, 3)
            print(f'mat {m:3d} rgb {c}  tris {sum(len(t) for t in ts):7d}  style {style_of(c):6s}  lo {np.round(allt.min(0), 1)} hi {np.round(allt.max(0), 1)}')
        sys.exit()
    out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    groups = {}
    for m, t in parts:
        groups.setdefault(style_of(colour(js, m)), []).append(t)
    for g, ts in groups.items():
        write_stl(out / f'{g}.stl', np.concatenate(ts))
        print(g, sum(len(t) for t in ts), 'triangles')
