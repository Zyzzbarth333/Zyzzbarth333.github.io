"""Pull a compact replay track out of COSMOS's synthetic demo session (cosmos_gcs/demo/sessions/...).

Usage: python3 -I extract.py <telemetry.jsonl (decoded from telemetry.jsonl.zst)> <out.json>
Keeps flight state (phase, AGL altitude, velocity), battery, sensor health, GPS fix and satellite count,
radio link counts and per-frame CRC results. GPS latitude and longitude are dropped on purpose.
Times are seconds from the first frame, from the board clock.
"""
import json
import sys

src, out = sys.argv[1], sys.argv[2]
state, hb, gps, frames = [], [], [], []
t0 = None
for line in open(src):
    p = json.loads(line)['payload']
    d = p.get('data') or {}
    ms = d.get('timestamp_ms')
    if ms is None:
        frames.append([None, 0])
        continue
    t = ms / 1000
    if t0 is None:
        t0 = t
    t = round(t - t0, 2)
    frames.append([t, 1 if p.get('crc_ok', True) else 0])
    pk = p['packet']
    if pk == 'HAVOC_STATE' and p.get('crc_ok', True):
        state.append([t, d['phase_name'], round(d['altitude_agl_m'], 1), round(d['velocity_mps'], 1), round(d['accel_mag_g'], 2), round(d['apogee_agl_m'], 1)])
    elif pk == 'HAVOC_HEARTBEAT' and p.get('crc_ok', True):
        ok = all(d.get(k, True) for k in ('imu_ok', 'h3lis_ok', 'onboard_mag_ok', 'regulator_ok', 'ms5607_ok', 'sd_card_ok'))
        hb.append([t, d['battery_mv'], 1 if ok else 0])
    elif pk == 'HAVOC_TELEMETRY_GPS' and p.get('crc_ok', True):
        gps.append([t, 1 if d.get('has_fix') else 0, d.get('sats_in_use', 0)])
# frames without a board time take the time of the frame before them
last = 0
for f in frames:
    if f[0] is None:
        f[0] = last
    last = f[0]
json.dump({'state': state, 'hb': hb, 'gps': gps, 'frames': frames}, open(out, 'w'), separators=(',', ':'))
print(len(state), 'state rows,', len(frames), 'frames,', sum(1 for f in frames if not f[1]), 'CRC failures')
