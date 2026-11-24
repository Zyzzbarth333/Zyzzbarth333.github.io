"""Make the 1200 x 630 share cards (og:image) for the project pages: the project's own card art, its kicker, title and
result on the site's paper, under the five-colour stripe (SEO audit, 19 Nov 2026: most pages shared the headshot or a
wrong-shaped photo).

Usage: python3 -I make_share.py <repo>   (needs PORTFOLIO_CONTACT_EMAIL like build_site.py; run before build_site.py)
Writes assets/img/projects/<slug>-share.jpg for every published project except HAVOC-2, which keeps its own card (a
shot of its flight figure). Headless Chrome renders each card from a page written into the repo root for the moment
(so the card art's assets/... links resolve), then removes it; the JPEG is saved with no metadata.
"""
import ast
import html
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

REPO = Path(sys.argv[1]).resolve()
HERE = Path(__file__).resolve().parent
sys.argv = [sys.argv[0], str(REPO)]
sys.path.insert(0, str(HERE))
import build_site as B   # noqa: E402  (PROJECTS, titles and kickers)

PROTO = HERE.parent / 'v4' / 'content.py'
RESULT = ast.literal_eval(re.search(r'^RESULT = (\{.*?\})\n', PROTO.read_text(), re.S | re.M).group(1))
E = html.escape
CHROME = 'google-chrome'
SKIP = {'havoc2-cosmos'}
CSS = ''.join(f'<link rel="stylesheet" href="{h}">' for h in ('assets/css/v4/chivo.css', 'assets/css/iso-kit.css', 'assets/css/v4/icons.css'))
PAGE = """<!doctype html><html lang="en-AU"><head><meta charset="utf-8">{css}<style>
@font-face{{font-family:Fraunces;src:url(assets/fonts/fraunces-900-latin.woff2) format('woff2');font-weight:900}}
@font-face{{font-family:Sanchez;src:url(assets/fonts/sanchez-400-latin.woff2) format('woff2')}}
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#ECEAE4;color:#1E2126}}
.stripe{{display:flex;height:12px}}.stripe i{{flex:1}}
.wrap{{display:grid;grid-template-columns:540px 1fr;height:618px}}
.art{{display:grid;place-items:center;border-right:2px solid #1E2126;background:#F5F4F0}}
.art .card{{width:470px;height:470px;padding:0;border:0;background:none;box-shadow:none}}
.art .icon{{display:block;width:470px;height:470px}}.art svg{{width:100%;height:100%}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px;width:470px}}.grid img{{width:100%;aspect-ratio:4/3;object-fit:cover;border:2px solid #1E2126;background:#fff}}
.txt{{padding:64px 56px 48px;display:flex;flex-direction:column}}
.k{{font:600 20px/1.3 'Chivo Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:#5D626B;margin:0 0 22px}}
h1{{font:900 {size}px/1.04 Fraunces,serif;margin:0;letter-spacing:-.01em}}
.r{{font:400 30px/1.3 Sanchez,serif;color:#2E1499;margin:26px 0 0}}
.who{{margin-top:auto;font:600 20px 'Chivo Mono',monospace;color:#1E2126;border-top:2px solid #1E2126;padding-top:18px}}
</style></head><body><div class="stripe"><i style="background:#FFC908"></i><i style="background:#FF5102"></i><i style="background:#BB0700"></i><i style="background:#2E1499"></i><i style="background:#3E9B5F"></i></div>
<div class="wrap"><div class="art">{art}</div><div class="txt"><p class="k">{kicker}</p><h1>{title}</h1>{result}<div class="who">Isaac Johan Ziebarth · zyzzbarth333.github.io</div></div></div></body></html>"""


def art(p):
    if p.get('coursework'):   # four of the coursework figures
        thumbs = ['scramjet-margin-isp', 'cold-gas-thrust', 'furuta-step-response', 'gyro-pendulum-stateflow']   # the clearest at this size
        return '<div class="grid">' + ''.join(f'<img src="assets/img/thumbs/{t}.webp" alt="">' for t in thumbs) + '</div>'
    svg = (REPO / 'assets/img' / p['card']).read_text()
    return f'<div class="card"><span class="icon iso">{svg}</span></div>'


def main():
    tmp = REPO / '_share-card.html'
    made = []
    try:
        for p in B.PROJECTS:
            if p.get('draft') or p['slug'] in SKIP or (not p.get('card') and not p.get('coursework')):
                continue
            title = p['title']
            res = RESULT.get(p['slug'], '')
            if res.lower() in title.lower():   # a result that only repeats the title says nothing
                res = ''
            tmp.write_text(PAGE.format(css=CSS, art=art(p), kicker=E(p['kicker']), title=E(title),
                                       size=64 if len(title) < 34 else 54 if len(title) < 52 else 46,
                                       result=f'<p class="r">{E(res[:1].upper() + res[1:])}</p>' if res else ''))
            png = REPO / f'_share-{p["slug"]}.png'
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                            '--window-size=1200,630', '--virtual-time-budget=4000', '--allow-file-access-from-files',
                            f'--screenshot={png}', tmp.as_uri()], capture_output=True, timeout=120)
            out = REPO / 'assets/img/projects' / f'{p["slug"]}-share.jpg'
            Image.open(png).convert('RGB').crop((0, 0, 1200, 630)).save(out, quality=86, optimize=True, progressive=True)   # no exif= : no metadata
            png.unlink()
            made.append(f'{out.name} {out.stat().st_size // 1024} KB')
    finally:
        tmp.unlink(missing_ok=True)
    print('\n'.join(made))


if __name__ == '__main__':
    main()
