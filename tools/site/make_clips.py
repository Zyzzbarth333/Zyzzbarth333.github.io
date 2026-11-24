"""Turn a headless capture into the site's and README's short clips.

Usage:
  python3 -I make_clips.py errol <capture-dir> <site>    the Lichtblick replay, 10 s from 10:15:46 AEST
  python3 -I make_clips.py havoc2 <capture-dir> <site>   the HAVOC-2 flight figure's "Replay the flight", 13.5 s

A capture dir holds f0000.png, f0001.png ... from the Anatomy kit's drive.mjs and times.txt, one
`eval:` line per frame giving that frame's time. drive.mjs can't keep a steady frame rate, so each capture plays
slower than real time and stamps every shot; this script takes the nearest shot to each 1/15 s step, which makes
the clip run in real time.

- errol: run lichtblick/errol.html at 1440 x 922, set Lichtblick's speed to 0.2x, press Play, then repeat
  ["eval", <the time input's value>] and ["shot", fNNNN.png, "body"] about 420 times. Frames are cropped to the
  panels (no app bar, which shows the URL; no playback bar, which shows the capture speed).
  Writes assets/video/errol-replay.{mp4,webm} (1200 px, H.264 and VP9), errol-replay-poster.webp (its first
  frame) and .github/readme/errol-replay.webp (640 px, animated).
- havoc2: run assets/figures/havoc2-flight.html at 1200 x 630 (--theme light), hide the table and replay controls,
  ["slow", 0.5], record performance.now() and click #replay, then repeat ["eval", "performance.now() - p0"] and
  ["shot", ...] about 480 times. Writes .github/readme/havoc2-replay.webp (800 px, animated).

Needs ffmpeg with libx264, libvpx-vp9 and libwebp_anim (Ubuntu's ffmpeg 8.0 has all three). No metadata is
written (-map_metadata -1; animated WebP from ffmpeg carries none).
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

kind, cap, site = sys.argv[1], Path(sys.argv[2]).expanduser(), Path(sys.argv[3]).expanduser()
FPS = 15
lines = (cap / 'times.txt').read_text().splitlines()
if kind == 'errol':
    ts = [(lambda m: int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]))(re.search(r'(\d+):(\d+):(\d+\.\d+)', l)) for l in lines]
    t0, dur, crop, sizes = 10 * 3600 + 15 * 60 + 46.0, 10.0, (0, 44, 1440, 844), {'site': (1200, 666), 'readme': (640, 356)}
elif kind == 'havoc2':
    ts = [float(l.split()[1]) / 1000 for l in lines]
    t0, dur, crop, sizes = 0.0, 13.5, (0, 0, 1200, 620), {'readme': (800, 414)}
else:
    sys.exit('kind is errol or havoc2')


def ff(*a):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *a], check=True)


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp); gap = 0.0
    for name in sizes: (tmp / name).mkdir()
    for k in range(int(FPS * dur)):
        tk = t0 + k / FPS
        i = min(range(len(ts)), key=lambda j: abs(ts[j] - tk)); gap = max(gap, abs(ts[i] - tk))
        shot = Image.open(cap / f'f{i:04d}.png').convert('RGB')
        im = Image.new('RGB', (crop[2] - crop[0], crop[3] - crop[1]), (255, 255, 255))
        im.paste(shot.crop(crop))
        for name, wh in sizes.items():
            im.resize(wh, Image.LANCZOS).save(tmp / name / f's{k:04d}.png')
    print(f'{k + 1} frames at {FPS} fps; nearest shot at most {gap * 1000:.0f} ms off')
    readme = site / '.github/readme'
    ff('-framerate', str(FPS), '-i', str(tmp / 'readme/s%04d.png'), '-c:v', 'libwebp_anim', '-lossless', '0',
       '-q:v', '60' if kind == 'errol' else '75', '-loop', '0', '-an', str(readme / f'{kind}-replay.webp'))
    if 'site' in sizes:
        vid = site / 'assets/video'; vid.mkdir(exist_ok=True)
        src = str(tmp / 'site/s%04d.png')
        ff('-framerate', str(FPS), '-i', src, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '27', '-preset', 'slow',
           '-movflags', '+faststart', '-an', '-map_metadata', '-1', str(vid / f'{kind}-replay.mp4'))
        ff('-framerate', str(FPS), '-i', src, '-c:v', 'libvpx-vp9', '-b:v', '2000k', '-maxrate', '2600k', '-deadline', 'good',
           '-cpu-used', '2', '-row-mt', '1', '-an', '-map_metadata', '-1', str(vid / f'{kind}-replay.webm'))
        Image.open(tmp / 'site/s0000.png').save(vid / f'{kind}-replay-poster.webp', quality=80)
for p in sorted([*site.glob(f'assets/video/{kind}-replay*'), *site.glob(f'.github/readme/{kind}-replay*')]):
    print(f'{p.relative_to(site)}  {p.stat().st_size / 1e6:.2f} MB')
