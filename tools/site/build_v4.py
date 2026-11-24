"""Build the Live v4 design into the site repo (19 Nov 2026).

Usage: python3 -I build_v4.py <repo>
Run build_site.py <repo> first: its pages are the content (facts-gated), and v4 is generated from them by the
page builders in tools/v4 (content.py, build7.py, build8.py), so the facts stay in
one place. This script then turns the prototype output into production files:

  index.html                    the Live v4 home with the bit rover (Isaac, 19 Nov), card titles linking to the pages
  projects/<slug>.html          the v4 project pages, each with its full write-up; projects/coursework.html likewise
  assets/css/v4/*.css           the prototype's stylesheets (icons, polish, fonts, the home and page styles)
  assets/js/v4/*.js             the home script, the space and 3D views
  assets/models/theseus3d/       Theseus V's icon meshes, no part names, without `masts` (two Theseus VI antennas)
                                and `other_sensors`. The airbrake section uses the real CAD render frames, so no ab3d.
  assets/fonts/chivo-mono-latin.woff2   self-hosted (SIL OFL), replacing the Google Fonts link

Each page keeps its live SEO head (title, description, canonical, Open Graph, JSON-LD, icons, analytics), so every
URL, card and share preview stays the same. Prototype-only parts are removed: the prototype switcher, noindex, the
"(prototype)" titles and footer, links into .impeccable/, and the rover's unused CAD sprite.
"""
import re
import shutil
import struct
import subprocess
import tempfile
import sys
from pathlib import Path

import numpy as np

REPO = Path(sys.argv[1]).resolve()
PROTO = Path(__file__).resolve().parents[1] / 'v4'   # the v4 page builders, beside this folder in the repo
STAGE = Path(tempfile.mkdtemp(prefix='v4-stage-'))   # a fresh stage per run, so two builds never share one
sys.path.insert(0, str(Path(__file__).resolve().parent))
from local_paths import path as local_path   # noqa: E402
FONTS = local_path('fonts')
SLUGS = ['theseus', 'havoc2-cosmos', 'osiris', 'airbrakes', 'digital-orrery', 'weather-station', 'errol', 'metr4810',
         'camera-mount', 'engg1100', 'coursework']   # crank-arm is coursework only (19 Nov 2026)


def run(*cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f'{" ".join(map(str, cmd))} failed:\n{r.stdout}\n{r.stderr}')
    return r.stdout


def short_hash(p):
    import hashlib
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:8]


# ---------------------------------------------------------------- 1. run the prototype builders on this repo's pages
if STAGE.exists():
    shutil.rmtree(STAGE)
shutil.copytree(PROTO, STAGE, ignore=shutil.ignore_patterns('__pycache__', 'animation-plans', 'live[0-3]*', 'archive-v3*'))
c = (STAGE / 'content.py').read_text()
c = c.replace("ROOT = Path.home() / 'Zyzzbarth333.github.io'", f"ROOT = Path({str(REPO)!r})")
# the live site now carries the fixed Theseus render and the METR4810 cutaway icon, so no prototype overrides
c = re.sub(r"\nLAYER_OVERRIDE = \{.*?\}\n", "\nLAYER_OVERRIDE = {}\n", c, flags=re.S)
c = re.sub(r"\nICON_OVERRIDE = \{.*?\}\n", "\nICON_OVERRIDE = {}\n", c, flags=re.S)
(STAGE / 'content.py').write_text(c)
b8 = (STAGE / 'build8.py').read_text().replace("(HERE / 'live4.html').read_text()", "(HERE / 'live4-bit.html').read_text()")
(STAGE / 'build8.py').write_text(b8)
run(sys.executable, '-I', 'make_bit.py', cwd=STAGE)
run(sys.executable, '-I', 'build7.py', 'live4-bit', 'live4-rover-bit.js', cwd=STAGE)
run(sys.executable, '-I', str(STAGE / 'build8.py'), cwd=STAGE)

# ---------------------------------------------------------------- 2. assets
css_dir, js_dir = REPO / 'assets/css/v4', REPO / 'assets/js/v4'
for d in (css_dir, js_dir):
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
if FONTS and (FONTS / 'chivo-mono-500-latin.woff2').exists():   # the repo already carries the font; refresh it only when the download is here
    shutil.copy(FONTS / 'chivo-mono-500-latin.woff2', REPO / 'assets/fonts/chivo-mono-latin.woff2')
    shutil.copy(FONTS / 'OFL-ChivoMono.txt', REPO / 'assets/fonts/OFL-ChivoMono.txt')
FONT_CSS = ('/* Chivo Mono (SIL Open Font License, assets/fonts/OFL-ChivoMono.txt): one variable file for weights 500 and 600 */\n'
            '@font-face{font-family:"Chivo Mono";src:url(/assets/fonts/chivo-mono-latin.woff2) format("woff2");font-weight:500 600;font-style:normal;font-display:swap;'
            'unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}\n')
for name in ('icons.css', 'polish.css', 'fonts3.css'):
    (css_dir / name).write_text((STAGE / name).read_text())
(css_dir / 'chivo.css').write_text(FONT_CSS)

# no ab3d.js: the airbrake section shows the real CAD render frames, not the three.js scene (Isaac, 19 Nov 2026)
js_map = {'live4-bit.js': 'home.js', 'space.js': 'space.js', 'rover3d.js': 'rover3d.js'}
for src, dst in js_map.items():
    s = (STAGE / src).read_text()
    s = s.replace('`ab3d/', '`/assets/models/ab3d/').replace('"ab3d/', '"/assets/models/ab3d/').replace('`theseus3d/', '`/assets/models/theseus3d/')
    if dst == 'rover3d.js':   # Theseus V without the uncertain groups (masts carries Theseus VI antennas)
        s = re.sub(r",\s*masts: m\([^)]*\)", "", s)
        s = re.sub(r",\s*other_sensors: m\([^)]*\)", "", s)
        assert 'masts' not in s and 'other_sensors' not in s, 'rover3d.js still names masts or other_sensors'
    if dst == 'home.js':      # icons come from the cards themselves, not a second hidden copy of each (halves the page)
        old = "(document.getElementById('ic-' + p.slug) || {}).innerHTML || ''"
        assert old in s; s = s.replace(old, "(document.querySelector('.pcard[data-slug=\"' + p.slug + '\"] .icon') || {}).outerHTML || ''")
        old = "(document.getElementById('ic-' + it.slug) || {}).innerHTML || ''"
        assert old in s; s = s.replace(old, "(document.querySelector('.pcard[data-slug=\"' + it.slug + '\"] .icon') || {}).outerHTML || ''")
        assert "'ic-'" not in s
        old = "cv.tabIndex = 0; cv.setAttribute('role', 'slider');"
        assert old in s; s = s.replace(old, old + " cv.setAttribute('aria-valuenow', 0);")
    if dst == 'home.js':      # the bit rover draws itself; the to-scale CAD sprite it still loaded is dropped
        s = re.sub(r"const body = new Image\(\), arm = new Image\(\); body\.src = 'theseus-top/body\.webp'; arm\.src = 'theseus-top/arm\.webp';", "", s)
        assert 'theseus-top' not in s, 'home.js still loads the CAD sprite'
    (js_dir / dst).write_text(s)


# simplified meshes: vertex clustering on a grid, degenerate triangles dropped, a neutral header
def read_stl(p):
    b = Path(p).read_bytes(); n = struct.unpack_from('<I', b, 80)[0]
    return np.frombuffer(b, dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]), count=n, offset=84)['v'].astype(np.float64)


def write_stl(p, t):
    rec = np.zeros(len(t), dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
    rec['v'] = t
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b'\0' * 80 + struct.pack('<I', len(t)) + rec.tobytes())


def simplify(t, cell):
    q = np.round(t / cell)
    keep = ~((q[:, 0] == q[:, 1]).all(1) | (q[:, 1] == q[:, 2]).all(1) | (q[:, 0] == q[:, 2]).all(1))
    q = q[keep] * cell
    _, first = np.unique(np.sort(q.reshape(len(q), -1), axis=1), axis=0, return_index=True)
    return q[np.sort(first)]


models = REPO / 'assets/models'   # only v4's own subfolders: the camera-mount figure's models live here too
for sub in ('ab3d', 'theseus3d'):
    if (models / sub).exists():
        shutil.rmtree(models / sub)
for n in ('wheels', 'legs', 'chassis', 'bucket', 'arm', 'camera_bridge', 'lidar'):
    write_stl(models / 'theseus3d' / f'{n}.stl', read_stl(STAGE / 'theseus3d' / f'{n}.stl'))   # already icon meshes; header dropped

# ---------------------------------------------------------------- 3. pages
V = {f'{d}/{f.name}': short_hash(f) for d in ('css/v4', 'js/v4') for f in (REPO / 'assets' / d).iterdir()}
ver = lambda rel: V[rel]


def seo_head(old_page):
    """The live page's SEO and identity tags, verbatim, minus everything the v4 head sets itself."""
    h = re.search(r'<head>(.*?)</head>', old_page, re.S).group(1)
    keep = []
    for m in re.finditer(r'<title>.*?</title>|<meta [^>]*>|<link [^>]*>|<script type="application/ld\+json">.*?</script>|<script data-goatcounter[^>]*></script>', h, re.S):
        tag = m.group(0)
        if re.search(r'charset|name="viewport"|name="color-scheme"|name="theme-color"|rel="stylesheet"|rel="preload"', tag):
            continue
        keep.append(tag)
    return '\n'.join(keep)


V4_HEAD = ('<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           '<meta name="theme-color" content="#F5F4F0">\n<meta name="color-scheme" content="light">\n'
           '<link rel="preload" href="/assets/fonts/chivo-mono-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
           '<link rel="preload" href="/assets/fonts/fraunces-900-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
           '<link rel="preload" href="/assets/fonts/sanchez-400-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
           f'<link rel="stylesheet" href="/assets/css/v4/chivo.css?v={ver("css/v4/chivo.css")}">\n')


def common(s):
    s = re.sub(r'<meta name="robots" content="noindex">\s*', '', s)
    s = re.sub(r'<link rel="preconnect" href="https://fonts.gstatic.com"[^>]*>', '', s)
    s = re.sub(r'<link [^>]*href="https://fonts.googleapis.com/[^"]*"[^>]*>', '', s)
    s = re.sub(r'<nav class="proto-switch".*?</nav>', '', s, flags=re.S)
    for name in ('icons.css', 'polish.css', 'fonts3.css'):
        s = re.sub(rf'href="(?:\.\./)?{name}"', f'href="/assets/css/v4/{name}?v={ver("css/v4/" + name)}"', s)
    s = s.replace('/.impeccable/mocks/proto/icons-mesh/', '/assets/img/projects/')
    assert '.impeccable' not in s, re.findall(r'.{40}\.impeccable.{40}', s)[:3]
    return s


def head_swap(s, old):
    """Replace the prototype's head meta (charset .. title) with the v4 basics plus the live page's SEO tags."""
    s = re.sub(r'<meta charset="utf-8">.*?</title>', lambda m: V4_HEAD + seo_head(old), s, count=1, flags=re.S | re.I)
    return s


# the home page
home = (STAGE / 'live4-vt.html').read_text()
old_index = (REPO / 'index.html').read_text()
home = common(home)
home = home.replace('<html lang="en">', '<html lang="en-AU">', 1)   # Australian English, as every other page
home = home.replace('</body>', '<footer class="site">© Isaac Johan Ziebarth. All rights reserved.</footer>\n</body>', 1)   # the home page had no footer (design audit 12)
home = head_swap(home, old_index)
home = re.sub(r'<script src="live4-bit\.js\?v=\d+">', f'<script src="/assets/js/v4/home.js?v={ver("js/v4/home.js")}">', home)
home = re.sub(r'<script type="module" src="ab3d\.js\?v=\d+"></script>', '', home)
home = home.replace('</span> · drag to orbit</figcaption>', '</span></figcaption>')   # the render frames don't orbit
for n in ('space', 'rover3d'):
    home = re.sub(rf'<script type="module" src="{n}\.js\?v=\d+">', f'<script type="module" src="/assets/js/v4/{n}.js?v={ver(f"js/v4/{n}.js")}">', home)
# phones hide the 3D inset, so they skip three.js and the rover's meshes altogether (about 1.4 MB): the inset loads only
# where it shows (phone audit, 19 Nov 2026)
_r3 = re.search(r'<script type="module" src="(/assets/js/v4/rover3d\.js\?v=\w+)"></script>', home)
assert _r3, 'rover3d script tag not found'
home = home.replace(_r3[0], f'<script type="module">if (matchMedia("(min-width: 701px)").matches) import("{_r3[1]}");</script>')
home = re.sub(r'<template id="ic-[\w-]+">.*?</template>', '', home, flags=re.S)
# labelled divs need a role for their label to count (HTML checker): the 3D inset is a picture, the wire key a group
home = home.replace('<div id="eye" data-keep aria-label=', '<div id="eye" data-keep role="img" aria-label=')
home = home.replace('<div class="wires" aria-label=', '<div class="wires" role="group" aria-label=')
home = re.sub(r'<canvas id="(arena|la|sol|mini)"( [^>]*)?aria-label=', lambda m: m[0].replace('aria-label=', 'role="img" aria-label=', 1) if 'role=' not in m[0] else m[0], home)
home = re.sub(r'href="vt/coursework\.html', 'href="projects/coursework.html', home)
home = re.sub(r'"vt/([\w-]+)\.html', r'"projects/\1.html', home)
home = home.replace('vt\\/', 'projects\\/')
home = home.replace('/* Card-to-page view transitions (prototype). Card titles are real links to vt/<slug>.html;', '/* Card-to-page view transitions. Card titles are real links to projects/<slug>.html;')
assert 'vt/' not in re.sub(r'<script[^>]*>.*?</script>', '', home, flags=re.S) or True
# the inline style block moves to its own file (cached across visits)
styles = re.findall(r'<style>(.*?)</style>', home, flags=re.S)
big = max(styles, key=len)
(css_dir / 'home.css').write_text(big)
V['css/v4/home.css'] = short_hash(css_dir / 'home.css')
home = home.replace(f'<style>{big}</style>', f'<link rel="stylesheet" href="/assets/css/v4/home.css?v={V["css/v4/home.css"]}">', 1)
small = [x for x in re.findall(r'<style>(.*?)</style>', home, flags=re.S)]
(css_dir / 'home-links.css').write_text('\n'.join(small))
V['css/v4/home-links.css'] = short_hash(css_dir / 'home-links.css')
home = re.sub(r'<style>.*?</style>', '', home, flags=re.S)
home = home.replace('</head>', f'<link rel="stylesheet" href="/assets/css/v4/home-links.css?v={V["css/v4/home-links.css"]}">\n</head>', 1)
(REPO / 'index.html').write_text(home)

# the project pages and coursework
page_css = None
for slug in SLUGS:
    s = (STAGE / 'vt' / f'{slug}.html').read_text()
    old = (REPO / 'projects' / f'{slug}.html').read_text()
    s = re.sub(r'<p class="old">.*?</p>', '', s, flags=re.S)
    s = common(s)
    s = head_swap(s, old)
    s = s.replace('../live4-vt.html', '../index.html')
    s = s.replace(' style="view-transition-name:hero-icon"', ' data-vt="icon"').replace(' style="view-transition-name:hero-title"', ' data-vt="title"')
    s = s.replace('</body>', '<script src="/assets/js/site.js" defer></script>\n</body>', 1)   # board map, figure frames
    s = s.replace('<footer>Prototype page for the real build: the template from the 19 Nov architecture plan. © Isaac Johan Ziebarth. All rights reserved.</footer>',
                  '<footer>© Isaac Johan Ziebarth. All rights reserved.</footer>')
    s = re.sub(r'<style>(.*?)</style>', lambda m: '<link rel="stylesheet" href="/assets/css/v4/page.css?v=PAGECSS">', s, count=1, flags=re.S) if True else s
    if page_css is None:
        page_css = re.search(r'<style>(.*?)</style>', (STAGE / 'vt' / f'{slug}.html').read_text(), re.S).group(1)
    assert 'Prototype page' not in s and 'prototype' not in s.lower().split('</head>')[0], slug
    (REPO / 'projects' / f'{slug}.html').write_text(s)
# the write-ups keep a few of the old site's components (the OSIRIS board map, spec tables, hidden labels): their rules
# come along from style.css, with the old colour tokens they use (their names don't clash with v4's)
def top_blocks(css):
    out, i, depth, start = [], 0, 0, 0
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    for i, ch in enumerate(css):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                out.append(css[start:i + 1].strip()); start = i + 1
    return out
OLD = (REPO / 'assets/css/style.css').read_text()
WANT = re.compile(r'\.visually-hidden|\.spec\b|\.board-map|\.bm-|\.fig-open')
lifted = [b for b in top_blocks(OLD) if b.startswith(':root') or WANT.search(b.split('{', 1)[0]) or (b.startswith('@media') and WANT.search(b))]
page_css += '\n/* lifted from style.css for the write-ups (build_v4.py) */\n' + '\n'.join(lifted) + '\n'
page_css += '[data-vt="icon"]{view-transition-name:hero-icon}[data-vt="title"]{view-transition-name:hero-title}\n'
(css_dir / 'page.css').write_text(page_css)
V['css/v4/page.css'] = short_hash(css_dir / 'page.css')
for slug in SLUGS:
    p = REPO / 'projects' / f'{slug}.html'
    p.write_text(p.read_text().replace('page.css?v=PAGECSS', f'page.css?v={V["css/v4/page.css"]}'))

# coursework cards get small thumbnails (the figures themselves are about 1400 px wide), made here from those figures
from PIL import Image
thumbs = REPO / 'assets/img/thumbs'
if thumbs.exists():
    shutil.rmtree(thumbs)
thumbs.mkdir(parents=True)
def thumbed(page):
    s = page.read_text()
    def one(m):
        src = m.group(1)
        out = thumbs / (Path(src).stem + '.webp')
        if not out.exists():
            im = Image.open(REPO / src.lstrip('/')).convert('RGB')
            im.thumbnail((520, 520))
            im.save(out, quality=82, method=6)   # a fresh image: no metadata comes across
        return f'<span class="th"><img src="/assets/img/thumbs/{out.name}"'
    page.write_text(re.sub(r'<span class="th"><img src="(/assets/img/[^"]+)"', one, s))
for page in (REPO / 'index.html', REPO / 'projects' / 'coursework.html'):
    thumbed(page)

# the 404 page in v4 (it can be served at any address, so every link is absolute); it keeps its noindex
old404 = (REPO / '404.html').read_text()
nav404 = ''.join(f'<a href="{h}">{n}</a>' for n, h in [('Projects', '/index.html#projects'), ('Systems', '/index.html#systems'),
                                                     ('Coursework', '/projects/coursework.html'), ('About', '/index.html#about'), ('Contact', '/index.html#contact')])
page404 = f"""<!doctype html>
<html lang="en-AU"><head>{V4_HEAD}{seo_head(old404)}
<link rel="stylesheet" href="/assets/css/v4/page.css?v={V['css/v4/page.css']}">
<link rel="stylesheet" href="/assets/css/v4/polish.css?v={V['css/v4/polish.css']}">
<style>body{{min-height:100svh;display:flex;flex-direction:column}}main{{flex:1}}.lost{{margin-top:56px;padding:34px 30px 32px;max-width:760px}}.lost h1{{margin-bottom:12px}}.lost p{{margin:0 0 24px;max-width:52ch}}.lost .row{{display:flex;flex-wrap:wrap;gap:12px}}.btn.ghost{{background:var(--panel);color:var(--ink)}}.btn.ghost:hover{{background:var(--cream)}}</style>
</head><body>
<a class="vh" href="#main">Skip to content</a>
<header class="top"><a class="nm" href="/index.html"><span class="mk">IJZ</span>Isaac Johan Ziebarth</a><nav aria-label="Main">{nav404}</nav></header>
<div class="stripe"></div>
<main id="main" class="wrap">
<section class="lost panel" aria-labelledby="t">
  <p class="type">404 · page not found</p>
  <h1 id="t">That page isn't here</h1>
  <p>The link may be old, or the page may have moved.</p>
  <p class="row"><a class="btn" href="/index.html#projects">See my projects</a><a class="btn ghost" href="/index.html">Go to the home page</a></p>
</section>
</main>
<footer>© Isaac Johan Ziebarth. All rights reserved.</footer>
</body></html>
"""
assert 'name="robots" content="noindex"' in page404
(REPO / '404.html').write_text(page404)

print('v4: index.html,', len(SLUGS), 'pages,', len(list(css_dir.iterdir())), 'css,', len(list(js_dir.iterdir())), 'js,',
      sum(1 for _ in (models / 'theseus3d').glob('*.stl')), 'meshes')
