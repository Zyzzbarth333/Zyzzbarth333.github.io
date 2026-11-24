"""Interactive replay of HAVOC-2's first flight (QRS, 12 Jul 2026) from the cleaned flight data.

Usage: python3 -I build_flight.py <flight>/derived <out.html> [<out-3d.html>]
  The optional second page is the same flight in 3D (flight3d_template.html), from the same data.

Reads trajectory_3d.csv (east/north/altitude in metres relative to the pad: no coordinates), ascent and
descent baro, ascent IMU and the onboard state. The 3D path's segments keep their meaning: ascent from IMU
attitude, a predicted gap where logging stopped while the board rebooted, the GPS-tracked top of the descent,
and a lower descent whose horizontal path is a wind-drift model. The descent log runs on the rebooted board's
own clock; it is placed after a ~9 s logging gap (the figure says so). Velocity comes from the baro stream,
because the onboard STATE velocity is biased low on this flight.
"""
import csv
import json
import sys
from pathlib import Path

d, out = Path(sys.argv[1]), Path(sys.argv[2])
rows = lambda f: list(csv.DictReader(open(d / f)))
GAP = 9.0                                                       # s of descent unrecorded while rebooting

asc = [(float(r['t_s']), float(r['alt_agl_m'])) for r in rows('ascent_baro.csv')]
t_end = asc[-1][0]
dsc_raw = [(float(r['t_s']), float(r['alt_agl_m'])) for r in rows('descent_baro.csv')]
off = t_end + GAP - dsc_raw[0][0]
dsc = [(t + off, a) for t, a in dsc_raw]
imu = [(float(r['t_s']), float(r['accel_mag_g'])) for r in rows('ascent_imu.csv')]
tr = [(float(r['x_east_m']), float(r['y_north_m']), float(r['z_alt_agl_m']), r['segment']) for r in rows('trajectory_3d.csv')]
apo_t, apo_a = max(asc, key=lambda p: p[1])
g0 = 0.0                                                        # keep the flight card's AGL reference (apogee 540 m AGL)
pad = round(min(a for _, a in asc[:5]), 1)                      # the pad's own reading on that reference

def time_for(z, series, rising):
    """First time the baro series crosses altitude z (rising on the way up, falling on the way down)."""
    for (t0, a0), (t1, a1) in zip(series, series[1:]):
        if (rising and a0 <= z <= a1) or (not rising and a0 >= z >= a1):
            return t0 + (t1 - t0) * ((z - a0) / (a1 - a0) if a1 != a0 else 0)
    return series[-1][0] if rising else series[0][0]

pts = []
gap = [p for p in tr if p[3] == 'gap_predicted']
for i, (x, y, z, seg) in enumerate(tr):
    if seg == 'ascent':
        t = time_for(z, [p for p in asc if p[0] <= apo_t + 0.01], True)
    elif seg == 'gap_predicted':
        k = gap.index((x, y, z, seg)) / max(1, len(gap) - 1)
        t = t_end + GAP * k
    else:
        t = time_for(z, dsc, False)
    pts.append([round(x, 1), round(y, 1), round(z - g0, 1), seg, round(t, 2)])
# keep time monotonic along the path
for i in range(1, len(pts)):
    pts[i][4] = max(pts[i][4], pts[i - 1][4])

boost = [p for p in imu if p[1] > 2.0]
data = {
    'asc': [[round(t, 2), round(a - g0, 1)] for t, a in asc],
    'dsc': [[round(t, 2), round(a - g0, 1)] for t, a in dsc],
    'imu': [[round(t, 2), round(g, 2)] for t, g in imu if t <= 4.0],
    'path': pts,
    'events': {'burnout': round(boost[-1][0], 2) if boost else 1.4, 'apogee_t': round(apo_t, 2), 'apogee_m': round(apo_a - g0),
               'peak_g': round(max(g for _, g in imu), 2), 'brownout': round(t_end, 2), 'resume': round(t_end + GAP, 2),
               'land': round(dsc[-1][0], 2), 'pad': pad},
}
html = (Path(__file__).parent / 'flight_template.html').read_text().replace('__DATA__', json.dumps(data, separators=(',', ':')))
out.write_text(html)
if len(sys.argv) > 3:
    Path(sys.argv[3]).write_text((Path(__file__).parent / 'flight3d_template.html').read_text().replace('__DATA__', json.dumps(data, separators=(',', ':'))))
    print('wrote', sys.argv[3])
print('wrote', out, data['events'], len(pts), 'path points')
