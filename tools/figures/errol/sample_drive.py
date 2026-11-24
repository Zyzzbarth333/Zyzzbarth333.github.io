"""Coarse profile of a drive from an MCAP bag without reading all of it: the INS every few seconds, plus /tf_static
and /ouster/metadata. Prints JSON lines. Usage: sample_drive.py <bag.mcap> [step_s]"""
import sys, json, math
from mcap.reader import make_reader
from mcap_ros2.decoder import DecoderFactory
path, step = sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
with open(path, 'rb') as f:
    r = make_reader(f, decoder_factories=[DecoderFactory()])
    s = r.get_summary(); ch = s.chunk_indexes
    t0 = min(c.message_start_time for c in ch); t1 = max(c.message_end_time for c in ch)
    for sch, chn, msg, m in r.iter_decoded_messages(topics=['/tf_static']):
        for tr in m.transforms:
            t = tr.transform.translation; q = tr.transform.rotation
            print(json.dumps({'tf': [tr.header.frame_id, tr.child_frame_id, round(t.x, 3), round(t.y, 3), round(t.z, 3), round(q.x, 4), round(q.y, 4), round(q.z, 4), round(q.w, 4)]}))
    for sch, chn, msg, m in r.iter_decoded_messages(topics=['/ouster/metadata']):
        md = json.loads(m.data); bi = md.get('sensor_info', {}) or {}
        print(json.dumps({'ouster': {k: md.get(k) or bi.get(k) for k in ('prod_line', 'build_rev')}, 'mode': (md.get('config_params') or md.get('lidar_mode') or {}).get('lidar_mode') if isinstance(md.get('config_params'), dict) else md.get('lidar_mode')}))
    t = t0
    while t < t1:
        got = None
        for sch, chn, msg, m in r.iter_decoded_messages(topics=['/novatel/oem7/inspva'], start_time=t, end_time=t + int(0.2e9)):
            got = m; break
        if got:
            v = math.hypot(got.north_velocity, got.east_velocity)
            print(json.dumps({'t': round((t - t0) / 1e9, 1), 'lat': round(got.latitude, 6), 'lon': round(got.longitude, 6), 'v': round(v, 2), 'az': round(got.azimuth, 1)}))
        t += int(step * 1e9)
