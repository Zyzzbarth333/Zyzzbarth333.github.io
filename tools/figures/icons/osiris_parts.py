"""Build OSIRIS V0 icon meshes: the real board from KiCad (via glb_split), plus the two 1x20 sockets and a
WeAct/DFRobot Black Pill (STM32F411, V3.0) modelled from its datasheet, seated in the sockets.

Usage: python3 -I osiris_parts.py <osiris-v0.glb> <out-dir>
Frame: KiCad millimetres with Y flipped (as glb_split writes), Z up, board top at z = 1.6.
Sockets: the board's footprints at KiCad (141.11, 75.87) and (158.89, 75.87), 20 pins down +y at 2.54 mm.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import glb_split as gs  # noqa: E402

glb, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)


def box(x0, y0, z0, x1, y1, z1):
    """12 triangles of an axis-aligned box."""
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], float)
    f = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return v[np.array(f)]


def cyl(cx, cy, z0, z1, r, n=16):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False); tris = []
    for i in range(n):
        p0 = [cx + r * np.cos(a[i]), cy + r * np.sin(a[i])]; p1 = [cx + r * np.cos(a[(i + 1) % n]), cy + r * np.sin(a[(i + 1) % n])]
        tris += [[[cx, cy, z1], [*p0, z1], [*p1, z1]], [[cx, cy, z0], [*p1, z0], [*p0, z0]],
                 [[*p0, z0], [*p1, z0], [*p1, z1]], [[*p0, z0], [*p1, z1], [*p0, z1]]]
    return np.array(tris, float)


# 1. the real board, grouped by material colour; bottom-side items dropped
js, binc = gs.load(glb)
groups = {'board': [], 'parts_dark': [], 'parts_light': []}
for m, t in gs.triangles(js, binc):
    t = t[t[:, :, 2].max(1) > 0.05]                      # drop the underside (bottom copper, mask, silk)
    if not len(t): continue
    st = gs.style_of(gs.colour(js, m))
    lo_z = t[:, :, 2].min()
    if st in ('board', 'gold') or (t[:, :, 2].max() <= 1.75):   # mask, copper, pads, top silk: the flat board
        groups['board'].append(t)
    elif st == 'dark':
        groups['parts_dark'].append(t)
    else:
        groups['parts_light'].append(t)

# 2. sockets: two 1x20 vertical 2.54 mm female headers, 8.5 mm tall
S_X = [141.11, 158.89]; Y0 = -75.87; PITCH = 2.54; N = 20
y_hi, y_lo = Y0 + 1.27, Y0 - (N - 1) * PITCH - 1.27
sock = [box(x - 1.27, y_lo, 1.6, x + 1.27, y_hi, 1.6 + 8.5) for x in S_X]

# 3. the Black Pill, seated: its pins in the sockets, a 2.5 mm header spacer, a 1.6 mm black board
bz0 = 1.6 + 8.5 + 2.5; bz1 = bz0 + 1.6
cx, cy = (S_X[0] + S_X[1]) / 2, Y0 - (N - 1) * PITCH / 2        # 150.0, -100.0
L, W = 52.8, 20.8
bp = {'bp_board': [box(cx - W / 2, cy - L / 2, bz0, cx + W / 2, cy + L / 2, bz1)],
      'bp_dark': [], 'bp_metal': []}
for x in S_X:                                                     # header spacers and pin tips
    bp['bp_dark'].append(box(x - 1.27, y_lo, 1.6 + 8.5, x + 1.27, y_hi, bz0))
    for k in range(N):
        y = Y0 - k * PITCH
        bp['bp_metal'].append(box(x - 0.32, y - 0.32, bz1, x + 0.32, y + 0.32, bz1 + 0.9))
top = cy + L / 2                                                  # USB-C end (towards the board's top edge)
bp['bp_metal'].append(box(cx - 4.5, top - 7.3, bz1, cx + 4.5, top + 0.8, bz1 + 3.2))          # USB-C shell
bp['bp_dark'].append(box(cx - 3.5, cy - 3.5, bz1, cx + 3.5, cy + 3.5, bz1 + 0.9))             # STM32F411 (QFN48, 7 mm)
bp['bp_metal'].append(box(cx - 1.6, cy - 9.0, bz1, cx + 1.6, cy - 6.5, bz1 + 0.8))            # 25 MHz crystal
bp['bp_metal'].append(box(cx + 4.0, cy - 9.2, bz1, cx + 7.2, cy - 7.7, bz1 + 0.7))            # 32.768 kHz crystal
for bx in (cx - 6.2, cx + 6.2):                                   # BOOT0 and NRST by the USB end
    bp['bp_dark'].append(box(bx - 2.0, top - 13.5, bz1, bx + 2.0, top - 10.5, bz1 + 1.2))
    bp['bp_metal'].append(cyl(bx, top - 12.0, bz1 + 1.2, bz1 + 1.7, 0.8))
bp['bp_dark'].append(box(cx - 2.0, cy + 7.0, bz1, cx + 2.0, cy + 10.0, bz1 + 1.2))            # KEY button
bp['bp_metal'].append(cyl(cx, cy + 8.5, bz1 + 1.2, bz1 + 1.7, 0.8))
bp['bp_dark'].append(box(cx - 5.2, cy - L / 2 - 2.5, bz0 + 0.2, cx + 5.2, cy - L / 2 + 0.2, bz0 + 2.7))   # SWD right-angle header
for k in range(4):
    x = cx - 3.81 + k * 2.54
    bp['bp_metal'].append(box(x - 0.32, cy - L / 2 - 6.5, bz0 + 1.1, x + 0.32, cy - L / 2 - 2.5, bz0 + 1.7))

def write(name, parts):
    if parts: gs.write_stl(out / f'{name}.stl', np.concatenate(parts)); print(name, sum(len(p) for p in parts))
for k, v in groups.items(): write(k, v)
write('sockets', sock)
for k, v in bp.items(): write(k, v)
print('module centre', cx, cy, 'top', round(bz1, 2))
