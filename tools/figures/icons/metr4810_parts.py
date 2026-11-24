"""Group the METR4810 cutter-pod meshes (four frames of the pod boring through three foam blocks) (Fusion ss_boom_gear_drive v195) into icon render groups, in two poses.

Usage: python3 -I metr4810_parts.py <meshes-v195-dir> <out-root>
Writes <out-root>/metr4810/<group>.stl (the pod straight) and <out-root>/metr4810-steer/<group>.stl (the pod yawed
STEER degrees about the hinge bolt's vertical axis, the steering the servo gives it), plus models/metr4810.json and
models/metr4810-steer.json for mesh_render.py. Both configs carry the same `extra` box (both poses and the foam
block), so the two renders share one projection and crossfade in place.

Only Isaac's pod is drawn. The arm plates (Fusion component `teammates_stepper_first_rig`) are the team's and are
left out, as are the two fastener meshes (pod_fasteners, servo_ear_fasteners: 340k triangles of screws that don't
read at icon size). Printed GD parts render as paper, bought metal hardware as metal, the servo and gearmotor dark,
and the cutter head in the accent colour (the one lit part, as on the drawn icon).
"""
import json
import struct
import sys
from pathlib import Path

import numpy as np

SRC, ROOT = Path(sys.argv[1]), Path(sys.argv[2])
HERE = Path(__file__).resolve().parent
HINGE = np.array([-81.5, -0.26])          # M6x40 hinge bolt axis (x, y), mm; the bolt runs along z
STEER = 18.0                              # degrees; +z yaw swings the cutter towards +y (the bend's inside)
S, K = 0.4, [-61.5, -0.26, -4.5]          # icon = S * (flip(p) + K): hinge at icon x 8, pod axis at icon z 15

MOVES = {   # group: (style, files) for parts that steer with the pod
    'pod': ('paper', ['GD09_pod_body', 'GD10_cutter_pod_nose', 'GD17_pod_motor_plate']),
    'lugs': ('metal', ['GD22_pod_upper_lug', 'GD23_pod_lower_lug']),
    'motor': ('dark', ['YG2734_gearmotor']),
    'spindle': ('metal', ['GD15_cutter_spindle', 'dowel_pin_3mm']),
    'cutter': ('accent', ['GD11_cutter_head']),
}
FIXED = {   # parts on the arm side of the hinge, which stay put
    'hinge': ('paper', ['GD02_hinge_journal_block', 'GD21_hinge_upper_bearing_keeper', 'GD25_gear_hood', 'GD03_pinion_15T',
                        'GD24_servo_spacer_front', 'GD24_servo_spacer_rear']),
    'hardware': ('metal', ['606-2RS_bearing_1', '606-2RS_bearing_2', 'M6x40_hinge_bolt', 'M6_hinge_nut',
                           'M6_hinge_washer_column', 'keeper_screws_and_nuts', 'pinion_screw_M3_button']),
    'servo': ('dark', ['MG995_servo']),
}


def read(name):
    b = (SRC / f'{name}.stl').read_bytes()
    n = struct.unpack_from('<I', b, 80)[0]
    a = np.frombuffer(b, dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]), count=n, offset=84)
    return a['v'].astype(np.float64)


def write(path, tris):
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = np.zeros(len(tris), dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
    rec['v'] = tris
    path.write_bytes(b'\0' * 80 + struct.pack('<I', len(tris)) + rec.tobytes())


def yaw(tris, deg):
    t = np.radians(deg); c, s = np.cos(t), np.sin(t)
    out = tris.copy(); xy = out[..., :2] - HINGE
    out[..., 0] = HINGE[0] + c * xy[..., 0] - s * xy[..., 1]
    out[..., 1] = HINGE[1] + s * xy[..., 0] + c * xy[..., 1]
    return out


def to_icon(p):
    return S * (np.stack([-p[..., 0], -p[..., 1], p[..., 2]], -1) + K)


# Pass 1 as it went at the final demonstration (facts.yaml metr4810): through the first end block, then into the bend
# in the middle block, where the steering servo couldn't hold enough angle against the cutting load, so the tunnel runs
# wide of the planned curve and never meets pass 2 (bored in from the far end). Angles are illustrative: none on record.
ADV = [0.0, 88.0, 200.0, 290.0]             # mm the rig has pushed the arm forward (design +x) at each frame
YAW = [0.0, 0.0, 6.0, 10.0]                # degrees the pod managed; the bend needs roughly three times that
poses = {f'metr4810-f{i}': (ADV[i], YAW[i]) for i in range(4)}
corners = []
def push(t, mm):
    out = t.copy(); out[..., 0] += mm; return out
for name, (adv, deg) in poses.items():
    for g, (_, files) in MOVES.items():
        t = push(yaw(np.concatenate([read(f) for f in files]), deg), adv)
        write(ROOT / name / f'{g}.stl', t); corners.append(to_icon(t).reshape(-1, 3))
    for g, (_, files) in FIXED.items():
        t = push(np.concatenate([read(f) for f in files]), adv)
        write(ROOT / name / f'{g}.stl', t); corners.append(to_icon(t).reshape(-1, 3))

# the foam block the vector overlay draws in front of the cutter (icon frame), so it fits in the frame too
tip = to_icon(np.array([[55.19, -0.26, 41.0]]))[0]
BX = float(tip[0]) - 0.6
BW, GAP = 70, 10
block = np.array([[BX - 3 * BW - 2 * GAP, -30, 0], [BX, 14, 29.2]])   # long blocks: a real runway (illustrative sizes)
allp = np.concatenate(corners + [block])
lo, hi = allp.min(0), allp.max(0)
extra = [[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
groups = {g: {'style': st} for g, (st, _) in {**MOVES, **FIXED}.items()}
for name in poses:
    cfg = {'name': name, 'meshes': str(ROOT / name), 'frame': {'scale': S, 'x': [-1, 0, 0, K[0]], 'y': [0, -1, 0, K[1]], 'z': [0, 0, 1, K[2]]},
           'groups': groups, 'azimuth': 300, 'elevation': 52, 'size': 300, 'pad': 18, 'extra': [[round(v, 2) for v in p] for p in extra],
           'keypoints': {'tip': [55.19, -0.26, 41.0], 'hinge_top': [-81.5, -0.26, 63.17]}, 'out_px': 600, 'supersample': 4, 'depth_step': 0.6}
    (HERE / 'models' / f'{name}.json').write_text(json.dumps(cfg, indent=1))
tips = {n: (to_icon(push(yaw(np.array([[[55.19, -0.26, 41.0]] * 3]), d), a))[0, 0]).round(2).tolist() for n, (a, d) in poses.items()}
print('block face x', round(BX, 2), 'icon box', lo.round(1).tolist(), hi.round(1).tolist()); print('cutter tips', tips)
