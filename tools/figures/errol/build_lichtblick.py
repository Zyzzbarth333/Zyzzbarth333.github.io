"""Assemble the site's Lichtblick replay of Errol: the app, Isaac's Foxglove panels and layouts, and the drive.

Usage: build_lichtblick.py <lichtblick-checkout> <foxglove-suite-dir> <errol-drive.mcap> <lexus.glb> <site> [--poster shot.png]

  lichtblick-checkout  ~/.local/share/portfolio-tools/lichtblick, built with `corepack yarn web:build:prod`
                       after applying lichtblick-static-loaders.patch (this folder) to tag v1.31.0
  foxglove-suite-dir   ~/errol/src/foxglove_layouts/errol-foxglove-suite (layouts/ and the built .foxe)
  errol-drive.mcap     from build_bag.py;  lexus.glb from build_lexus.mjs

Writes <site>/lichtblick/, replacing what was there:
  index.html + the app's files (no source maps)   the patched Lichtblick web app (MPL-2.0)
  errol.html                                      launcher: opens the drive with the open-day layout
  static/manifest.json, *.foxe, *.json            panels and layouts the patched app loads with no setup
  data/errol-drive.mcap, data/lexus.glb           the drive and the car model
  LICENSE.txt, SOURCE.md, lichtblick-static-loaders.patch   MPL-2.0 text and where the source is
and <site>/assets/figures/errol-lichtblick.html, the Errol page's lead: a still of the replay with a Start button that
loads Lichtblick in the same frame, so the page itself stays light. --poster takes a 1440 x 922 headless shot of the
running replay (anatomy's drive.mjs) and writes it, cropped below the app bar, to assets/img/projects/errol-lichtblick.webp.
"""
import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

argv = sys.argv[1:]
poster = None
if '--poster' in argv:
    i = argv.index('--poster'); poster = Path(argv[i + 1]).expanduser(); del argv[i:i + 2]
lb, suite, bag, glb, site = (Path(a).expanduser() for a in argv[:5])
HERE = Path(__file__).resolve().parent
out = site / 'lichtblick'
APP_W, APP_H = 1440, 878     # the desktop window the page's frame shows, scaled to fit (ratio 1.64)
LAYOUT_VERSION = 7            # bump when a layout changes: the app only adds layouts whose file name is new

webpack = lb / 'web/.webpack'
if not (webpack / 'index.html').exists():
    sys.exit(f'{webpack} has no index.html: build Lichtblick first')
if out.exists():
    shutil.rmtree(out)
(out / 'static').mkdir(parents=True); (out / 'data').mkdir()

# ---------- the app ----------
def png_without_metadata(b):
    """The PNG with its eXIf, iTXt, tEXt, zTXt and tIME chunks dropped (the site strips all image metadata)."""
    import struct
    out, i = [b[:8]], 8
    while i < len(b):
        n = struct.unpack('>I', b[i:i + 4])[0]; kind = b[i + 4:i + 8]
        if kind not in (b'eXIf', b'iTXt', b'tEXt', b'zTXt', b'tIME'):
            out.append(b[i:i + 12 + n])
        i += 12 + n
    return b''.join(out)

for f in webpack.iterdir():
    if f.is_file() and not f.name.endswith('.map'):
        if f.name == 'index.html':             # the app shell: keep it out of search results
            html = f.read_text()
            if 'name="robots"' not in html:
                html = html.replace('<head>', '<head><meta name="robots" content="noindex">', 1)
            (out / f.name).write_text(html)
        elif f.suffix == '.png':                 # keep the content-hash name the JS refers to; rewrite only the bytes
            (out / f.name).write_bytes(png_without_metadata(f.read_bytes()))
        else:
            shutil.copy2(f, out / f.name)
shutil.copy2(lb / 'LICENSE', out / 'LICENSE.txt')
patch = subprocess.run(['git', '-C', str(lb), 'diff', '--no-color', 'HEAD', '--', 'packages'], capture_output=True, text=True, check=True).stdout
new = subprocess.run(['git', '-C', str(lb), 'diff', '--no-color', '--no-index', '/dev/null', 'packages/suite-web/src/StaticSiteLoaders.ts'],
                     capture_output=True, text=True, cwd=lb).stdout
(HERE / 'lichtblick-static-loaders.patch').write_text(patch + new)
shutil.copy2(HERE / 'lichtblick-static-loaders.patch', out / 'lichtblick-static-loaders.patch')
commit = subprocess.run(['git', '-C', str(lb), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
(out / 'SOURCE.md').write_text(f"""# Lichtblick

This folder is a build of [Lichtblick](https://github.com/lichtblick-suite/lichtblick) v1.31.0 (commit {commit}),
licensed under the Mozilla Public License 2.0 (`LICENSE.txt`). Its source is at that link. The changes, all in
`lichtblick-static-loaders.patch`:

- the app loads panels and layouts shipped beside it in `static/` (new file `StaticSiteLoaders.ts`, and a
  `layoutLoaders` option passed from `WebRoot.tsx` through `SharedRoot` to `StudioApp`);
- an asset URL relative to the page, such as the car model, resolves against the page (`MessagePipeline/store.ts`);
- the left sidebar starts closed, and the launch-preference screen is off (`WorkspaceContextProvider.tsx`, `WebRoot.tsx`).

`static/errol-vehicle-controls.foxe` holds the Errol Vehicle Controls panels (MIT, (c) 2025 The University of
Queensland; `static/LICENSE-errol-vehicle-controls.txt`). `data/lexus.glb` is derived
from the Lexus model in Autoware's sample_vehicle (Apache-2.0).
""")

# ---------- panels ----------
foxe = suite / 'extensions/vehicle-controls/errol-vehicle-controls.foxe'
shutil.copy2(foxe, out / 'static' / foxe.name)
# The .foxe's package.json declares MIT (publisher "UQ") but ships no notice; Isaac named the holder (18 Nov 2026).
(out / 'static' / 'LICENSE-errol-vehicle-controls.txt').write_text("""Errol Vehicle Controls panels (errol-vehicle-controls.foxe)

MIT License

Copyright (c) 2025 The University of Queensland

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")

# ---------- layouts ----------
op = json.loads((suite / 'layouts/errol_foxglove_operation.json').read_text())
def tune(layout):
    """The layout as recorded, with the 3D view following the car and showing its model."""
    cfg = layout['configById']['3D!lidar_monitor']
    cfg['followTf'] = 'base_link'
    cfg['topics']['/errol/vehicle_model'] = {'visible': True}
    cfg['cameraState']['distance'] = 60
    layout['playbackConfig'] = {'speed': 1}
    return layout

operation = tune(copy.deepcopy(op))
open_day = tune(copy.deepcopy(op))
keep = {'3D!lidar_monitor', 'Errol Vehicle Controls.GPS Array Monitor!1jofuhw', 'map!gps_track', 'Errol Vehicle Controls.Vehicle Dashboard!2cohdp8'}
open_day['configById'] = {k: v for k, v in open_day['configById'].items() if k in keep}
# GPS Array Monitor | 3D | Map over Vehicle Dashboard, as in Isaac's open-day layout: 26% | 44% | 30%. The page runs
# the app at APP_W x APP_H and scales it down, so these are desktop proportions (the dashboard clips below ~340 px).
open_day['layout'] = {'first': 'Errol Vehicle Controls.GPS Array Monitor!1jofuhw',
                      'second': {'first': '3D!lidar_monitor',
                                 'second': {'first': 'map!gps_track', 'second': 'Errol Vehicle Controls.Vehicle Dashboard!2cohdp8',
                                            'direction': 'column', 'splitPercentage': 25},
                                 'direction': 'row', 'splitPercentage': 60},
                      'direction': 'row', 'splitPercentage': 26}
layouts = [('Errol open day', f'errol-open-day-v{LAYOUT_VERSION}.json', open_day),
           ('Errol operation', f'errol-operation-v{LAYOUT_VERSION}.json', operation)]
for _, fn, data in layouts:
    (out / 'static' / fn).write_text(json.dumps(data, indent=1))
(out / 'static/manifest.json').write_text(json.dumps(
    {'extensions': [foxe.name], 'layouts': [{'name': n, 'file': f} for n, f, _ in layouts]}, indent=1))

# ---------- data ----------
shutil.copy2(bag, out / 'data/errol-drive.mcap')
shutil.copy2(glb, out / 'data/lexus.glb')
shutil.copy2(suite.parent.parent / 'errol_description/meshes/LICENSE.autoware', out / 'data/LICENSE-autoware.txt')   # Apache 2.0 travels with the model

# ---------- launcher ----------
(out / 'errol.html').write_text("""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Errol replay</title>
<style>body{font:16px/1.5 system-ui,sans-serif;margin:2rem;background:#fff;color:#111}a{color:inherit}</style>
</head>
<body>
<p>Opening the drive in Lichtblick&hellip;</p>
<script>
  const here = new URL('.', location.href);
  const q = new URLSearchParams({ ds: 'remote-file', 'ds.url': new URL('data/errol-drive.mcap', here).href, layout: 'Errol open day' });
  location.replace(new URL('./?' + q, here));
</script>
<noscript><p>The replay runs in Lichtblick, which needs JavaScript.</p></noscript>
</body>
</html>
""")
# ---------- the page's lead: a still and a Start button ----------
img = site / 'assets/img/projects/errol-lichtblick.webp'
if poster:
    from PIL import Image
    im = Image.open(poster).convert('RGB')
    im.crop((0, 44, im.width, im.height)).save(img, quality=82, method=6)      # below the app bar (it shows the URL)
from PIL import Image
w, h = Image.open(img).size
# A 10 s clip of the replay (site-tools/make_clips.py) plays once over the still when the frame comes into view,
# per the site's motion rule: once at most, any input or the Stop button ends it, reduced motion skips it.
vid = site / 'assets/video'
clip_html = clip_js = ''
if (vid / 'errol-replay.mp4').exists():
    v = lambda n: f"../video/{n}?v={(vid / n).stat().st_size}"
    clip_html = f"""  <video class="clip" muted playsinline preload="none" hidden aria-hidden="true" poster="{v('errol-replay-poster.webp')}">
    <source src="{v('errol-replay.webm')}" type="video/webm"><source src="{v('errol-replay.mp4')}" type="video/mp4">
  </video>
  <button class="stop" type="button" hidden>Stop</button>
"""
    clip_js = """
  // Play the clip once on first view; any input or Stop ends it; reduced motion never starts it.
  (() => {
    const v = document.querySelector('.clip'), stop = document.querySelector('.stop');
    if (!v || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const end = () => { v.pause(); v.hidden = true; stop.hidden = true; removeEventListener('keydown', end); removeEventListener('pointerdown', end); };
    const io = new IntersectionObserver((es) => {
      if (!es.some((e) => e.isIntersecting)) return;
      io.disconnect(); v.hidden = false; stop.hidden = false;
      v.play().catch(end);
      addEventListener('keydown', end); addEventListener('pointerdown', end);
    }, { threshold: 0.5 });
    io.observe(document.body);
    v.addEventListener('ended', () => { stop.hidden = true; });      // rests on its last frame
    stop.addEventListener('click', end);
  })();"""
(site / 'assets/figures/errol-lichtblick.html').write_text(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Errol drive replay in Lichtblick</title>
<style>
  html, body {{ margin: 0; height: 100%; background: #000; }}
  .poster {{ position: relative; height: 100%; display: grid; place-items: center; overflow: hidden; }}
  .poster img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: left top; }}
  .poster::after {{ content: ""; position: absolute; inset: 0; background: rgb(0 0 0 / 0.5); }}
  .cta {{ position: relative; z-index: 1; display: grid; justify-items: center; gap: 0.7rem; padding: 1rem; text-align: center;
         font: 400 0.95rem/1.4 system-ui, sans-serif; color: #fff; }}
  .start {{ font: 600 1.05rem/1 system-ui, sans-serif; padding: 0.9rem 1.5rem; border: 0; border-radius: 999px;
           background: #fff; color: #111; cursor: pointer; display: inline-flex; gap: 0.6rem; align-items: center; }}
  .start:hover {{ background: #e8e8e8; }}
  .start:focus-visible {{ outline: 3px solid #fff; outline-offset: 3px; }}
  .start svg {{ width: 0.9em; height: 0.9em; }}
  .cta p {{ margin: 0; max-width: 30rem; text-shadow: 0 1px 2px #000; }}
  .app {{ position: absolute; left: 0; top: 0; width: {APP_W}px; height: {APP_H}px; border: 0; transform-origin: 0 0; }}
  .clip {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: center top; }}
  .stop {{ position: absolute; z-index: 2; top: 0.8rem; right: 0.8rem; font: 600 0.85rem/1 system-ui, sans-serif;
          padding: 0.55rem 0.9rem; border: 1px solid #fff; border-radius: 999px; background: rgb(0 0 0 / 0.6); color: #fff; cursor: pointer; }}
  .stop:focus-visible {{ outline: 3px solid #fff; outline-offset: 2px; }}
</style>
</head>
<body>
<div class="poster">
  <img src="../img/projects/errol-lichtblick.webp?v={img.stat().st_size}" width="{w}" height="{h}"
       alt="Still from the replay: the GPS array status panel, Errol's LiDAR point cloud around the Lexus model, a street map of the campus and the vehicle dashboard at 25 km/h in drive">
{clip_html}  <div class="cta">
    <button class="start" type="button"><svg viewBox="0 0 10 10" aria-hidden="true"><path d="M1 0 9 5 1 10z" fill="currentColor"/></svg>Start the replay</button>
    <p>Loads Lichtblick here, scaled from a desktop window, then streams the 45 s drive ({bag.stat().st_size / 1e6:.0f} MB).</p>
  </div>
</div>
<script>{clip_js}
  // Run Lichtblick at a desktop window size and scale it to the frame, so its panels lay out as they do full size.
  document.querySelector('.start').addEventListener('click', () => {{
    const app = document.createElement('iframe');
    app.className = 'app'; app.title = 'Lichtblick replaying the Errol drive'; app.src = '../../lichtblick/errol.html';
    const fit = () => {{ const k = innerWidth / {APP_W}; app.style.transform = `scale(${{k}})`; app.style.height = `${{innerHeight / k}}px`; }};
    document.body.replaceChildren(app); fit(); addEventListener('resize', fit); app.focus();
  }});
</script>
</body>
</html>
""")

size = sum(f.stat().st_size for f in out.rglob('*') if f.is_file())
print(f'wrote {out} ({sum(1 for _ in out.rglob("*"))} files, {size / 1e6:.1f} MB)')
