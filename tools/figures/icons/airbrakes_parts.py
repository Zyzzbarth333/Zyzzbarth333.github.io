"""Group Isaac's FHC-1 airbrake module meshes for the airbrakes card icon (read-only on ~/airbrakes).

Usage: python3 -I airbrakes_parts.py <airbrakes>/cad/out/parts <out-dir>
Reads the per-part STLs that cad/airbrake_module.py exports (mm, module frame: z along the axis, forward ring at low z)
and writes binary STLs for mesh_render.py:
  body.stl    the bay body and the aft plate          rings.stl  the forward and aft interface rings
  flaps_<d>.stl  all four flaps opened d degrees, for d in ANGLES
The parts folder holds flap 1 closed, at azimuth flap_az0 (79 deg). Each flap opens about its own hinge: an axis along
the local tangent through (r_h, z_h) = (69 mm, the hinge pin's centre), turned by +delta so the aft edge swings out,
exactly as airbrake_module.py does (flap0.rotate(hinge_axis, delta_deg)). Flaps 2-4 are flap 1 turned 90 deg about z.
"""
import struct
import sys
from pathlib import Path

import numpy as np

parts, out = Path(sys.argv[1]).expanduser(), Path(sys.argv[2]).expanduser()
out.mkdir(parents=True, exist_ok=True)
ANGLES = [0, 16, 32, 48, 64, 80]
R_H, AZ0 = 69.0, 79.0


def read(name):
    b = (parts / f'{name}.stl').read_bytes()
    n = struct.unpack('<I', b[80:84])[0]
    return np.frombuffer(b[84:84 + n * 50], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))['v'].astype(float)


def write(name, tris):
    tris = np.asarray(tris, np.float32)
    rec = np.zeros(len(tris), dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
    rec['v'] = tris
    with open(out / f'{name}.stl', 'wb') as f:
        f.write(b'\0' * 80); f.write(struct.pack('<I', len(tris))); f.write(rec.tobytes())
    print(name, len(tris), 'triangles')


def rot_axis(points, origin, axis, deg):
    """Rodrigues rotation of points about the line through origin along axis (right hand)."""
    k = np.asarray(axis, float); k /= np.linalg.norm(k)
    t = np.radians(deg); p = points - origin
    return origin + p * np.cos(t) + np.cross(k, p) * np.sin(t) + np.outer(p @ k, k) * (1 - np.cos(t))


pin = read('hinge_pin_1a').reshape(-1, 3)
z_h = float((pin[:, 2].min() + pin[:, 2].max()) / 2)            # the hinge pin sits on the axis
a0 = np.radians(AZ0)
origin = np.array([R_H * np.cos(a0), R_H * np.sin(a0), z_h])
tangent = np.array([-np.sin(a0), np.cos(a0), 0.0])
flap = read('flap_1')

write('body', np.concatenate([read('bay_body'), read('aft_plate')]))
write('rings', np.concatenate([read('IF_fwd_ring_R3'), read('IF_aft_ring_R4')]))
for d in ANGLES:
    f1 = rot_axis(flap.reshape(-1, 3), origin, tangent, d).reshape(-1, 3, 3)
    four = []
    for k in range(4):
        c, s = np.cos(np.radians(90 * k)), np.sin(np.radians(90 * k))
        Rz = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        four.append(f1 @ Rz.T)
    write(f'flaps_{d}', np.concatenate(four))
print('hinge z', round(z_h, 2))
