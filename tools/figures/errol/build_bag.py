"""Build the small MCAP that the site's Lichtblick replay plays: 45 s of Errol at full rate, sized for GitHub Pages.

Usage: build_bag.py <slice.mcap> <extra.mcap> <tfstatic.mcap> <sensor_mounts.yaml> <out.mcap> [--model-url URL]

  slice.mcap     /ouster/points, PACMod reports, NovAtel INSPVA/BESTPOS and u-blox NavPVT for the window
  extra.mcap     the same window's NavSatFix, IMU, PACMod enabled/global/yaw-rate and /diagnostics topics
  tfstatic.mcap  the recording's /tf_static (only the Ouster's internal os_sensor -> os_lidar / os_imu)
  sensor_mounts.yaml   errol_description's mount positions on base_link (rear axle centre on the ground)

Every topic keeps its recorded timestamps and rate. What changes:
- /ouster/points keeps every frame (10 Hz) but only every RING_STEP-th ring and COL_STEP-th column of the OS1-128,
  drops empty returns and points past RANGE_M, rounds x/y/z to 1/Q m and keeps x, y, z and reflectivity
  (16-bit, as recorded: the layout's colour map looks wrong with any of its bits dropped). Override with ERROL_THIN=ring,col,range_m,q (default 2,3,50.0,32.0).
- /tf_static is rewritten as base_link -> each sensor mount from sensor_mounts.yaml, plus the recorded Ouster
  internal transforms, and repeated each second so a seek always finds it.
- /errol/vehicle_model is added: a foxglove.SceneUpdate (JSON) placing the Lexus model (build_lexus.mjs) on
  base_link by URL, once a second.
- /diagnostics is copied as recorded. For this window it holds only the u-blox driver's fix and rate status
  (checked 18 Nov 2026: no host names or addresses). Check again before using another window.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from mcap.reader import make_reader
from mcap.writer import CompressionType, Writer
from mcap_ros2._dynamic import serialize_dynamic
from mcap_ros2.decoder import DecoderFactory

argv = sys.argv[1:]
model_url = 'data/lexus.glb'
if '--model-url' in argv:
    i = argv.index('--model-url'); model_url = argv[i + 1]; del argv[i:i + 2]
slice_p, extra_p, tf_p, mounts_p, out_p = argv
HERE = Path(__file__).resolve().parent
import os
RING_STEP, COL_STEP, RANGE_M, Q = (float(v) if '.' in v else int(v) for v in os.environ.get('ERROL_THIN', '2,3,50.0,32.0').split(','))

def read_yaml_mounts(path):
    """sensor_mounts.yaml without PyYAML: name -> (parent, xyz, rpy)."""
    out, cur = {}, None
    for line in Path(path).read_text().splitlines():
        s = line.split('#', 1)[0].rstrip()
        if not s.strip() or s.strip() == 'sensors:': continue
        if s.startswith('  ') and not s.startswith('    ') and s.strip().endswith(':'):
            cur = s.strip()[:-1]; out[cur] = {}
        elif cur and ':' in s:
            k, v = (t.strip() for t in s.split(':', 1))
            out[cur][k] = json.loads(v) if v.startswith('[') else v
    return {n: (d['parent'], d['xyz'], d['rpy']) for n, d in out.items()}

def quat(r, p, y):
    cr, sr, cp, sp, cy, sy = (f(a / 2) for a in (r, p, y) for f in (math.cos, math.sin))
    return {'x': sr * cp * cy - cr * sp * sy, 'y': cr * sp * cy + sr * cp * sy,
            'z': cr * cp * sy - sr * sp * cy, 'w': cr * cp * cy + sr * sp * sy}

def stamp(ns): return {'sec': ns // 1_000_000_000, 'nanosec': ns % 1_000_000_000}

out = open(out_p, 'wb')
w = Writer(out, compression=CompressionType.ZSTD, chunk_size=1 << 20)
w.start(profile='ros2', library='errol build_bag.py')
schemas, channels = {}, {}

def channel(topic, schema_name, encoding, schema_data, msg_enc):
    if topic not in channels:
        if schema_name not in schemas:
            schemas[schema_name] = w.register_schema(name=schema_name, encoding=encoding, data=schema_data)
        channels[topic] = w.register_channel(topic=topic, message_encoding=msg_enc, schema_id=schemas[schema_name])
    return channels[topic]

pending = []   # (log_time, channel_id, data, publish_time) - merged and written in time order

# ---------- passthrough topics ----------
with open(slice_p, 'rb') as fh:
    _st = make_reader(fh).get_summary().statistics
    T0, T1 = _st.message_start_time, _st.message_end_time                  # the slice's own window

def copy_raw(path, skip=()):
    with open(path, 'rb') as fh:
        r = make_reader(fh)
        for sc, ch, msg in r.iter_messages(starting_at=T0, ending_at=T1):
            if ch.topic in skip: continue
            cid = channel(ch.topic, sc.name, sc.encoding, sc.data, ch.message_encoding)
            pending.append((msg.log_time, cid, msg.data, msg.publish_time))
copy_raw(slice_p, skip={'/ouster/points'})
copy_raw(extra_p, skip={'/tf_static'})

# ---------- Ouster, thinned ----------
pc_schema, pc_enc = None, None
kept, total = [], 0
with open(slice_p, 'rb') as fh:
    r = make_reader(fh, decoder_factories=[DecoderFactory()])
    for sc, ch, msg, m in r.iter_decoded_messages(topics=['/ouster/points']):
        if pc_enc is None:
            pc_schema = sc; pc_enc = serialize_dynamic(sc.name, sc.data.decode())[sc.name]
        off = {f.name: f.offset for f in m.fields}
        raw = np.frombuffer(bytes(m.data), np.uint8).reshape(m.height, m.width, m.point_step)[::RING_STEP, ::COL_STEP]
        get = lambda name, dt, n: raw[..., off[name]:off[name] + n].copy().view(dt)[..., 0]
        rng = get('range', '<u4', 4) / 1000.0
        ok = (rng > 0.5) & (rng < RANGE_M)
        xyz = np.stack([get(a, '<f4', 4)[ok] for a in 'xyz'], 1)
        xyz = (np.round(xyz * Q) / Q).astype('<f4')
        refl = get('reflectivity', '<u2', 2)[ok]                              # as recorded: the colour map needs all 16 bits
        rec = np.zeros(len(xyz), dtype=[('x', '<f4'), ('y', '<f4'), ('z', '<f4'), ('reflectivity', '<u2')])
        rec['x'], rec['y'], rec['z'], rec['reflectivity'] = xyz[:, 0], xyz[:, 1], xyz[:, 2], refl
        new = {'header': {'stamp': {'sec': m.header.stamp.sec, 'nanosec': m.header.stamp.nanosec}, 'frame_id': m.header.frame_id},
               'height': 1, 'width': len(rec), 'is_bigendian': False, 'point_step': 14, 'row_step': 14 * len(rec), 'is_dense': True,
               'fields': [{'name': n, 'offset': o, 'datatype': d, 'count': 1} for n, o, d in (('x', 0, 7), ('y', 4, 7), ('z', 8, 7), ('reflectivity', 12, 4))],
               'data': rec.tobytes()}
        cid = channel('/ouster/points', sc.name, sc.encoding, sc.data, ch.message_encoding)
        pending.append((msg.log_time, cid, pc_enc(new), msg.publish_time))
        kept.append(len(rec)); total += 1

t0, t1 = T0, T1

# ---------- /tf_static: the real mounts, plus the Ouster's own frames ----------
with open(tf_p, 'rb') as fh:
    r = make_reader(fh, decoder_factories=[DecoderFactory()])
    tf_sc, ouster_tf = None, []
    for sc, ch, msg, m in r.iter_decoded_messages(topics=['/tf_static']):
        tf_sc = sc
        for t in m.transforms:
            tr, q = t.transform.translation, t.transform.rotation
            ouster_tf.append((t.header.frame_id, t.child_frame_id, [tr.x, tr.y, tr.z], {'x': q.x, 'y': q.y, 'z': q.z, 'w': q.w}))
tf_enc = serialize_dynamic(tf_sc.name, tf_sc.data.decode())[tf_sc.name]
mounts = read_yaml_mounts(mounts_p)
frames = [(par, name, xyz, quat(*rpy)) for name, (par, xyz, rpy) in mounts.items()] + ouster_tf
tf_cid = channel('/tf_static', tf_sc.name, tf_sc.encoding, tf_sc.data, 'cdr')

# ---------- /errol/vehicle_model: the Lexus on base_link ----------
scene_schema = (HERE / 'src/foxglove-schemas/SceneUpdate.json').read_bytes()
scene_cid = channel('/errol/vehicle_model', 'foxglove.SceneUpdate', 'jsonschema', scene_schema, 'json')

for ns in range(t0, t1 + 1, 1_000_000_000):
    tf = {'transforms': [{'header': {'stamp': stamp(ns), 'frame_id': par}, 'child_frame_id': child,
                          'transform': {'translation': {'x': x, 'y': y, 'z': z}, 'rotation': q}}
                         for par, child, (x, y, z), q in frames]}
    pending.append((ns, tf_cid, tf_enc(tf), ns))
    ts = {'sec': ns // 1_000_000_000, 'nsec': ns % 1_000_000_000}
    ent = {'timestamp': ts, 'frame_id': 'base_link', 'id': 'errol', 'lifetime': {'sec': 0, 'nsec': 0}, 'frame_locked': True,
           'metadata': [], 'arrows': [], 'cubes': [], 'spheres': [], 'cylinders': [], 'lines': [], 'triangles': [], 'texts': [],
           'models': [{'pose': {'position': {'x': 0, 'y': 0, 'z': 0}, 'orientation': {'x': 0, 'y': 0, 'z': 0, 'w': 1}},
                       'scale': {'x': 1, 'y': 1, 'z': 1}, 'color': {'r': 1, 'g': 1, 'b': 1, 'a': 1}, 'override_color': False,
                       'url': model_url, 'media_type': 'model/gltf-binary', 'data': ''}]}
    pending.append((ns, scene_cid, json.dumps({'deletions': [], 'entities': [ent]}).encode(), ns))

for log_time, cid, data, pub in sorted(pending, key=lambda p: (p[0], p[1])):
    w.add_message(channel_id=cid, log_time=log_time, data=data, publish_time=pub)
w.finish(); out.close()
print(f'{total} Ouster frames, {np.mean(kept):.0f} points each; {len(channels)} topics; '
      f'{(t1 - t0) / 1e9:.1f} s; {Path(out_p).stat().st_size / 1e6:.1f} MB')
