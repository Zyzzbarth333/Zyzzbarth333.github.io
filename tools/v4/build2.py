"""Round 3 prototypes: Trailhead stack, Meguri press, NASA-punk console, theatre poster.

python3 -I build2.py   -> trailhead.html, meguri.html, console.html, poster.html beside this file.
Serve the repo root on 8001 and open /.impeccable/mocks/proto/<name>.html. Local only (.impeccable/ is git-excluded).
Templates use @@TOKEN@@ placeholders so CSS and JS keep their own braces.
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from content import load, ROOT  # noqa: E402

D = load()
P = D['projects']
MAIN = [p for p in P if not p['earlier']]
EARLIER = [p for p in P if p['earlier']]
e = html.escape
TOOLS = ['C++', 'Python', 'C', 'ROS 2', 'Nav2', 'PX4', 'Gazebo', 'MATLAB', 'Simulink', 'SymPy', 'Mathematica',
         'Fusion 360', 'KiCad', '3D printing']
YEAR = {p['slug']: p['meta'].split(' · ')[-1] for p in P}

PROTOS = [('trailhead', 'Trailhead stack'), ('meguri', 'Meguri press'), ('console', 'Mission console'),
          ('poster', 'Theatre poster')]


def havoc_profile():
    s = (ROOT / 'assets/figures/havoc2-flight.html').read_text()
    i = s.find('const D =') + len('const D =')
    d, _ = json.JSONDecoder().raw_decode(s[i:].lstrip())
    pad = d['events']['pad']
    asc = [(t, a - pad) for t, a in d['asc'][::3]]
    dsc = [(t, a - pad) for t, a in d['dsc'][::6]]
    return asc, dsc, d['events']


ASC, DSC, EV = havoc_profile()


def profile_svg(w=520, h=170, stroke='currentColor', accent='#BB0700', font='inherit'):
    t0, t1, amax = -3, 47, 600
    X = lambda t: 34 + (t - t0) / (t1 - t0) * (w - 44)
    Y = lambda a: h - 22 - max(a, 0) / amax * (h - 36)
    pa = ' '.join(f'{X(t):.1f},{Y(a):.1f}' for t, a in ASC)
    pd = ' '.join(f'{X(t):.1f},{Y(a):.1f}' for t, a in DSC)
    gap = f'{X(ASC[-1][0]):.1f},{Y(ASC[-1][1]):.1f} {X(DSC[0][0]):.1f},{Y(DSC[0][1]):.1f}'
    ax, ay = X(EV['apogee_t']), Y(EV['apogee_m'] - EV['pad'] + 21.5 - 21.5)
    ticks = ''.join(f'<line x1="30" x2="{w - 8}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{stroke}" stroke-opacity=".18" stroke-dasharray="2 4"/>'
                    f'<text x="28" y="{Y(v) + 4:.1f}" text-anchor="end" font-size="10" fill="{stroke}">{v}</text>' for v in (0, 200, 400, 600))
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="HAVOC-2 first flight altitude: apogee about {EV["apogee_m"]} m at {EV["apogee_t"]} s" '
            f'style="width:100%;height:auto;font-family:{font}">{ticks}'
            f'<polyline points="{pa}" fill="none" stroke="{stroke}" stroke-width="2.2"/>'
            f'<polyline points="{gap}" fill="none" stroke="{stroke}" stroke-width="1.5" stroke-dasharray="4 4" stroke-opacity=".6"/>'
            f'<polyline points="{pd}" fill="none" stroke="{accent}" stroke-width="2.2"/>'
            f'<circle cx="{ax:.1f}" cy="{Y(540):.1f}" r="4.5" fill="{accent}"/>'
            f'<text x="{ax + 9:.1f}" y="{Y(540) + 4:.1f}" font-size="11" fill="{stroke}">apogee ~540 m</text>'
            f'<text x="{w - 8}" y="{h - 4}" text-anchor="end" font-size="10" fill="{stroke}">seconds after liftoff · dashed: no log</text></svg>')


SWITCH_CSS = """
.proto-switch{position:fixed;right:12px;bottom:12px;z-index:99;display:flex;gap:4px;align-items:center;flex-wrap:wrap;
 background:#111;color:#fff;font:600 12px/1 system-ui,sans-serif;padding:6px;border-radius:8px;box-shadow:0 4px 16px #0005}
.proto-switch b{padding:0 6px;opacity:.6;font-weight:600}
.proto-switch a{color:#fff;text-decoration:none;padding:6px 8px;border-radius:5px}
.proto-switch a[aria-current]{background:#FFC908;color:#111}
@media (max-width:600px){.proto-switch b{display:none}.proto-switch{left:8px;right:8px;justify-content:center}.proto-switch a{padding:6px 5px}}
"""


def switcher(cur):
    links = ''.join(f'<a href="{k}.html"{" aria-current=page" if k == cur else ""}>{n}</a>' for k, n in PROTOS)
    return f'<nav class="proto-switch" aria-label="Prototypes"><b>Prototype</b>{links}</nav>'


def page(title, fonts, css, body, js=''):
    data = json.dumps([{k: p[k] for k in ('slug', 'href', 'title', 'meta', 'summary', 'outcome', 'facts', 'sections',
                                          'figure', 'image', 'result', 'short', 'tags')} for p in P]).replace('</', '<\\/')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>{title}</title>
<link rel="stylesheet" href="/assets/css/iso-kit.css"><link rel="stylesheet" href="icons.css">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">
<style>
@font-face{{font-family:Fraunces;src:url(/assets/fonts/fraunces-900-latin.woff2) format("woff2");font-weight:900;font-display:swap}}
@font-face{{font-family:Sanchez;src:url(/assets/fonts/sanchez-400-latin.woff2) format("woff2");font-weight:400;font-display:swap}}
*{{box-sizing:border-box}} html{{-webkit-text-size-adjust:100%;scroll-padding-top:80px}} img{{max-width:100%;display:block}}
.vh{{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}}
.card .icon svg{{width:100%;height:100%;display:block}}
{SWITCH_CSS}{css}</style></head><body>
<a class="vh" href="#main">Skip to content</a>
{body}{switcher(title.split(' · ')[-1].lower().split()[0] if False else '')}
<script type="application/json" id="proj-data">{data}</script>
<script>const PROJ=JSON.parse(document.getElementById('proj-data').textContent);
const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
const byslug=s=>PROJ.find(p=>p.slug===s);
function figureHTML(p){{ if(p.figure) return `<iframe src="${{p.figure}}" title="Live figure: ${{p.title}}" loading="lazy"></iframe>`;
 if(p.image) return `<img src="${{p.image}}" alt="">`; return ''; }}
function factsHTML(p){{ return '<dl>'+p.facts.map(([k,v])=>`<div><dt>${{k}}</dt><dd>${{v}}</dd></div>`).join('')+'</dl>'; }}
{js}</script><script src="/assets/js/site.js"></script></body></html>"""


def fill(tpl, **kw):
    for k, v in kw.items():
        tpl = tpl.replace(f'@@{k}@@', str(v))
    left = re.findall(r'@@\w+@@', tpl)
    assert not left, left
    return tpl


def bio(n=4):
    return ''.join(f'<p>{e(x)}</p>' for x in D['about'][:n])


# ======================================================================= 1. Trailhead stack
def trailhead():
    css = """
:root{--paper:#FBFAF6;--ink:#17151F;--mute:#56525F;--line:2px solid var(--ink);--red:#BB0700;--ind:#2E1499;--yel:#FFC908;
 --sans:'Schibsted Grotesk',system-ui,sans-serif;--mono:'Chivo Mono',ui-monospace,monospace}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 var(--sans)}
a{color:inherit}
.menubar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:6px;height:48px;padding:0 18px;background:var(--paper);border-bottom:var(--line);font:500 14px var(--mono)}
.menubar .logo{display:flex;align-items:center;gap:10px;font:700 17px var(--sans);text-decoration:none;margin-right:22px}
.menubar .logo i{width:22px;height:22px;border:var(--line);display:grid;place-items:center;font:normal 700 11px var(--mono)}
.menubar nav a{text-decoration:none;padding:8px 10px}
.menubar nav a:hover,.menubar nav a:focus-visible,.menubar nav a[aria-current]{background:var(--ink);color:var(--paper);outline:0}
.menubar .right{margin-left:auto;font-size:12px;color:var(--mute)}
.shell{display:grid;grid-template-columns:250px minmax(0,1fr) 270px;gap:18px;padding:18px;max-width:1500px;margin:0 auto;align-items:start}
.box{border:var(--line);background:var(--paper)}
.bh{display:flex;justify-content:space-between;align-items:center;padding:9px 12px;border-bottom:var(--line);font:600 12px var(--mono);letter-spacing:.06em;text-transform:uppercase}
.bh span{font-weight:400;text-transform:none;letter-spacing:0;color:var(--mute)}
.side{position:sticky;top:66px}
.toc{list-style:none;margin:0;padding:6px;max-height:calc(100vh - 170px);overflow:auto}
.toc button{all:unset;box-sizing:border-box;width:100%;display:grid;grid-template-columns:30px 1fr auto;gap:8px;align-items:center;padding:8px 8px;cursor:pointer;font:500 13px/1.25 var(--mono)}
.toc button i{width:26px;height:26px;border:1.5px solid var(--ink);display:grid;place-items:center;font:normal 600 10px var(--mono)}
.toc button b{font-weight:400;color:var(--mute);font-size:11px}
.toc button:hover{background:#EEEBE2}
.toc button[aria-current=true]{background:var(--ink);color:var(--paper)}
.toc button[aria-current=true] i{border-color:var(--paper)}.toc button[aria-current=true] b{color:var(--paper)}
.toc button:focus-visible{outline:3px solid var(--red);outline-offset:-3px}
.toc .sep{font:600 10px var(--mono);letter-spacing:.1em;color:var(--mute);padding:10px 8px 4px;text-transform:uppercase}
.pager{display:flex;align-items:center;justify-content:space-between;border-top:var(--line);padding:8px}
.pager button{all:unset;cursor:pointer;border:var(--line);width:34px;height:28px;display:grid;place-items:center}
.pager button:hover,.pager button:focus-visible{background:var(--ink);color:var(--paper)}
.pager span{font:500 12px var(--mono)}
.card-pane[hidden]{display:none}
.welcome{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:26px;padding:26px}
h1{font:600 clamp(2.4rem,4.6vw,4.3rem)/1.02 var(--sans);letter-spacing:-.025em;margin:0 0 16px}
.lede{font-size:1.08rem;max-width:44ch;margin:0 0 20px}
.btns{display:flex;flex-wrap:wrap;gap:10px}
.btn{all:unset;box-sizing:border-box;cursor:pointer;font:500 14px var(--mono);border:var(--line);padding:10px 16px;text-decoration:none;display:inline-block}
.btn.dark{background:var(--ink);color:var(--paper)}
.btn:hover,.btn:focus-visible{background:var(--red);color:#fff;border-color:var(--red)}
.portrait{border:var(--line);margin:0;align-self:start}
.portrait img{filter:grayscale(1) contrast(1.12);aspect-ratio:4/4.3;object-fit:cover;width:100%;height:auto;transition:filter .3s}
.portrait:hover img{filter:none}
.portrait figcaption{border-top:var(--line);padding:7px 10px;font:500 11px var(--mono);display:flex;justify-content:space-between}
.split{display:grid;grid-template-columns:1.3fr 1fr;border-top:var(--line)}
.split>div{padding:0}
.split>div+div{border-left:var(--line)}
table.recent{width:100%;border-collapse:collapse;font:500 13px var(--mono)}
.recent td{padding:9px 12px;border-bottom:1px solid #D5D1C6}
.recent td:last-child{text-align:right;color:var(--mute);white-space:nowrap}
.recent button{all:unset;cursor:pointer;text-decoration:underline;text-underline-offset:3px}
.recent .r{color:var(--red);white-space:nowrap}
.mapimg{display:block;width:100%;aspect-ratio:1.5;object-fit:cover;object-position:40% 40%;filter:grayscale(1) contrast(1.4)}
.row3{display:grid;grid-template-columns:1fr 1.5fr 1fr;gap:18px;margin-top:18px}
.pad{padding:14px 14px}
.note-date{display:grid;grid-template-columns:62px 1fr;gap:12px}
.note-date .d{border:var(--line);text-align:center;font:600 11px var(--mono);height:max-content}
.note-date .d b{display:block;font:700 26px/1.1 var(--sans);border-top:var(--line)}
.small{font:500 13px/1.6 var(--mono)}
.tools{columns:2;font:500 13px/1.9 var(--mono);margin:0;padding:0 0 0 18px}
.wid{margin-bottom:18px}
.clock{border:var(--line);margin:14px;padding:12px;text-align:center;font:600 40px/1 var(--mono);letter-spacing:.02em}
.clock small{font:500 12px var(--mono);vertical-align:top}
.wid .c{text-align:center;font:500 13px var(--mono);margin:-4px 0 14px}
.next{display:grid;grid-template-columns:30px 1fr;gap:10px;padding:14px;font:500 13px/1.45 var(--mono)}
.next svg{width:28px;height:28px}
.next b{font:600 15px var(--sans);display:block}
.stat{display:flex;justify-content:space-between;align-items:baseline;padding:10px 14px;border-top:1px solid #D5D1C6;font:500 12px var(--mono)}
.stat:first-of-type{border-top:0}
.stat b{font:700 22px var(--sans)}
.stat b.r{color:var(--red)}
.proj-pane{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr)}
.proj-pane .txt{padding:24px;border-right:var(--line)}
.proj-pane h2{font:600 2.2rem/1.05 var(--sans);letter-spacing:-.02em;margin:6px 0 8px}
.proj-pane .res{font:700 1.4rem var(--sans);color:var(--red);margin:4px 0 12px}
.proj-pane .meta{font:500 12px var(--mono);color:var(--mute)}
.proj-pane .live{min-height:560px;position:relative;background:#fff}
.proj-pane .live iframe{border:0;position:absolute;inset:0;width:100%;height:100%}
.proj-pane .live img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}
.proj-pane .icon{display:block;width:140px;height:140px;float:right;margin:-6px -6px 6px 10px}
dl{margin:14px 0;font-size:.92rem} dl div{display:grid;grid-template-columns:6.5em 1fr;gap:10px;padding:7px 0;border-top:1px solid #D5D1C6}
dt{font:600 11px/1.9 var(--mono);text-transform:uppercase;letter-spacing:.05em} dd{margin:0}
.secs{font:500 12px var(--mono);color:var(--mute)}
.grid{list-style:none;margin:0;padding:18px;display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px}
.grid .card{position:relative;border:var(--line);padding:12px 14px 14px;display:flex;flex-direction:column;background:var(--paper)}
.grid .card:hover,.grid .card:focus-within{background:#F1EEE5}
.grid .icon{display:block;width:70%;margin:0 auto;aspect-ratio:1}
.grid h3{font:600 1.05rem/1.2 var(--sans);margin:6px 0 4px}
.grid h3 button{all:unset;cursor:pointer}.grid h3 button::after{content:"";position:absolute;inset:0}
.grid h3 button:focus-visible{outline:3px solid var(--red);outline-offset:4px}
.grid .r{color:var(--red);font:600 13px var(--mono);margin-top:auto}
.grid .m{font:500 11px var(--mono);color:var(--mute)}
.cw{list-style:none;margin:0;padding:6px 0}
.cw a{display:grid;grid-template-columns:110px 1fr;gap:12px;padding:11px 18px;border-bottom:1px solid #D5D1C6;text-decoration:none;font:500 14px var(--mono)}
.cw a b{font-weight:600}
.cw a:hover,.cw a:focus-visible{background:var(--ink);color:var(--paper);outline:0}
.about{display:grid;grid-template-columns:1.4fr 1fr}
.about>div{padding:22px}.about>div+div{border-left:var(--line)}
.exp{list-style:none;margin:0;padding:0}
.exp li{padding:9px 0;border-top:1px solid #D5D1C6;font:500 13px/1.45 var(--mono)}
.exp b{font:600 15px var(--sans);display:block}
.contact{padding:40px 26px;text-align:center}
.contact h2{font:600 clamp(2rem,4vw,3.4rem)/1 var(--sans);letter-spacing:-.02em;margin:0 0 12px}
.contact .btns{justify-content:center;margin-top:18px}
@media (max-width:1180px){.shell{grid-template-columns:220px minmax(0,1fr)}.widgets{grid-column:1/-1;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.wid{margin:0}}
@media (max-width:820px){.shell{grid-template-columns:1fr;padding:12px}.side{position:static}.toc{max-height:none;display:flex;overflow-x:auto;gap:4px}
 .toc li{flex:0 0 auto}.toc .sep{display:none}.toc button{grid-template-columns:26px auto;white-space:nowrap}.toc button b{display:none}
 .welcome,.split,.row3,.proj-pane,.about{grid-template-columns:1fr}.split>div+div,.about>div+div{border-left:0;border-top:var(--line)}
 .proj-pane .txt{border-right:0;border-bottom:var(--line)}.proj-pane .live{min-height:420px}.widgets{grid-template-columns:1fr}
 .menubar nav a{padding:8px 5px;font-size:12px}.menubar .right{display:none}.menubar .logo{margin-right:6px}.menubar .logo span{display:none}}
"""
    toc = ['<li><button type="button" data-card="welcome" aria-current="true"><i>01</i>Welcome<b></b></button></li>',
           '<li><button type="button" data-card="projects"><i>02</i>All projects<b>11</b></button></li>',
           '<li class="sep">Project cards</li>']
    for i, p in enumerate(P):
        toc.append(f'<li><button type="button" data-card="p-{p["slug"]}"><i>{i + 3:02d}</i>{e(p["short"][0].title() if p["slug"] != "havoc2-cosmos" else "HAVOC-2 + COSMOS")}<b>{e(YEAR[p["slug"]][-4:])}</b></button></li>')
    n = len(P) + 2
    toc += ['<li class="sep">More</li>',
            f'<li><button type="button" data-card="coursework"><i>{n + 1:02d}</i>Coursework<b>{len(D["coursework"])}</b></button></li>',
            f'<li><button type="button" data-card="about"><i>{n + 2:02d}</i>About<b></b></button></li>',
            f'<li><button type="button" data-card="contact"><i>{n + 3:02d}</i>Contact<b></b></button></li>']
    recent = ''.join(f'<tr><td><button type="button" data-card="p-{p["slug"]}">{e(p["title"])}</button></td><td class="r">{e(p["result"])}</td><td>{e(YEAR[p["slug"]])}</td></tr>' for p in MAIN[:5])
    grid = ''.join(f'<li class="card">{p["icon"]}<h3><button type="button" data-card="p-{p["slug"]}">{e(p["title"])}</button></h3><p class="m">{e(p["meta"])}</p><p class="r">{e(p["result"])}</p></li>' for p in P)
    panes = []
    for p in P:
        live = f'<iframe src="about:blank" data-src="{p["figure"]}" title="Live figure: {e(p["title"])}"></iframe>' if p['figure'] else (f'<img src="{p["image"]}" alt="">' if p['image'] else '')
        facts = '<dl>' + ''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in p['facts']) + '</dl>'
        panes.append(f"""<section class="box card-pane" id="p-{p['slug']}" hidden aria-labelledby="h-{p['slug']}"><div class="bh">{e(p['title'])}<span>{e(YEAR[p['slug']])}</span></div>
<div class="proj-pane"><div class="txt card">{p['icon']}<p class="meta">{e(p['meta'])}</p><h2 id="h-{p['slug']}">{e(p['title'])}</h2><p class="res">{e(p['result'])}</p>
<p>{e(p['outcome'])}</p>{facts}<p class="secs">Full write-up: {' · '.join(e(s) for s in p['sections'])}</p>
<div class="btns"><a class="btn dark" href="{p['href']}">Read the write-up</a><button class="btn" type="button" data-step="1">Next card</button></div></div>
<div class="live">{live}</div></div></section>""")
    cw = ''.join(f'<li><a href="{c["href"]}"><b>{e(c["meta"])}</b>{e(c["title"])}</a></li>' for c in D['coursework'])
    exp = ''.join(f'<li><b>{e(r)}</b>{e(o)}<br>{e(w)}</li>' for r, o, w in D['experience'])
    body = fill("""<header class="menubar"><a class="logo" href="#"><i>IZ</i><span>Isaac's Stack</span></a>
<nav aria-label="Main"><a href="#" data-card="welcome">Welcome</a><a href="#" data-card="projects">Projects</a><a href="#" data-card="coursework">Coursework</a><a href="#" data-card="about">About</a><a href="#" data-card="contact">Contact</a></nav>
<span class="right">@@N@@ cards</span></header>
<div class="shell" id="main">
<aside class="side box" aria-label="Stack contents"><div class="bh">Stack contents<span>@@N@@ cards</span></div><ul class="toc">@@TOC@@</ul>
<div class="pager"><button type="button" data-step="-1" aria-label="Previous card">←</button><span id="pos">1 of @@N@@</span><button type="button" data-step="1" aria-label="Next card">→</button></div></aside>
<main>
<section class="box card-pane" id="welcome" aria-labelledby="me"><div class="bh">Welcome<span>card 01</span></div>
<div class="welcome"><div><h1 id="me">Software that flies, drives and finds its way.</h1>
<p class="lede">I'm Isaac Johan Ziebarth, a mechatronic engineering student at UQ. I write robot and flight software, design the boards it runs on and build the ground stations that read it back.</p>
<div class="btns"><button class="btn dark" type="button" data-card="projects">Open projects</button><a class="btn" href="mailto:@@EMAIL@@">Email me</a><a class="btn" href="@@LI@@">LinkedIn</a></div></div>
<figure class="portrait"><img src="/assets/img/profile.jpg" alt="" width="800" height="800"><figcaption><span>Isaac, Brisbane</span><span>hover for colour</span></figcaption></figure></div>
<div class="split"><div><div class="bh" style="border-top:0">Recent work<span><button class="btn" style="all:unset;cursor:pointer;text-decoration:underline" type="button" data-card="projects">view all</button></span></div>
<table class="recent"><caption class="vh">Recent work</caption>@@RECENT@@</table></div>
<div><div class="bh">On the map<span>ARC 2026 arena</span></div><img class="mapimg" src="/assets/figures/theseus-map-cloud.webp" alt="Point cloud map of the 2026 rover arena that Theseus V built"></div></div></section>
<section class="box card-pane" id="projects" hidden aria-labelledby="ph"><div class="bh"><span style="color:inherit" id="ph">All projects</span><span>@@NP@@ cards</span></div><ul class="grid">@@GRID@@</ul></section>
@@PANES@@
<section class="box card-pane" id="coursework" hidden aria-labelledby="ch"><div class="bh"><span style="color:inherit" id="ch">Coursework</span><span>graded reports</span></div><ul class="cw">@@CW@@</ul></section>
<section class="box card-pane" id="about" hidden aria-labelledby="ah"><div class="bh"><span style="color:inherit" id="ah">About</span><span>notes</span></div>
<div class="about"><div>@@BIO@@</div><div><p class="small" style="margin-top:0"><b>Tools</b></p><ul class="tools">@@TOOLS@@</ul><p class="small"><b>Experience</b></p><ul class="exp">@@EXP@@</ul><p class="small">@@EDU@@</p></div></div></section>
<section class="box card-pane" id="contact" hidden aria-labelledby="cth"><div class="bh">Contact<span>last card</span></div><div class="contact"><h2 id="cth">Let's talk.</h2>
<p class="small">@@EMAIL@@</p><div class="btns"><a class="btn dark" href="mailto:@@EMAIL@@">Email me</a><a class="btn" href="@@LI@@">LinkedIn</a><a class="btn" href="@@GH@@">GitHub</a></div></div></section>
<div class="row3"><section class="box" aria-labelledby="fn"><div class="bh"><span style="color:inherit" id="fn">Field notes</span><span>Nov 2026</span></div>
<div class="pad note-date"><div class="d">NOV<b>18</b></div><p class="small" style="margin:0">Handed the avionics lead over to make room for research and a Master's placement. Still on the team, working on the ground stations, PCBs and the Theseus VI autonomy stack.</p></div></section>
<section class="box" aria-labelledby="fp"><div class="bh"><span style="color:inherit" id="fp">Flight profile</span><span>HAVOC-2, 12 Jul 2026</span></div><div class="pad">@@PROFILE@@</div></section>
<section class="box" aria-labelledby="tl"><div class="bh"><span style="color:inherit" id="tl">Toolbox</span><span>daily</span></div><div class="pad"><ul class="tools">@@TOOLS@@</ul></div></section></div>
</main>
<aside class="widgets" aria-label="Status">
<section class="box wid"><div class="bh">Today<span>Brisbane</span></div><div class="clock" id="clock">--:--</div><p class="c" id="date"></p></section>
<section class="box wid"><div class="bh">Now<span></span></div>
<div class="next"><svg viewBox="0 0 28 28" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="22" height="18"/><path d="M3 11h22M9 2v6M19 2v6"/></svg><div><b>Research assistant</b>PX4 flight control and modelling, UQ EECS</div></div>
<div class="next" style="border-top:1px solid #D5D1C6"><svg viewBox="0 0 28 28" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 22l7-14 5 9 3-5 5 10z"/></svg><div><b>Avionics engineer</b>UQ Space: ground stations, PCBs, Theseus VI</div></div></section>
<section class="box wid"><div class="bh">Next up<span>2027</span></div>
<div class="next"><svg viewBox="0 0 28 28" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 3l11 5-11 5L3 8zM7 10v7c4 3 10 3 14 0v-7"/></svg><div><b>Graduating Nov 2027</b>Looking for internships and graduate roles: avionics, autonomy, GNC</div></div>
<div style="padding:0 14px 14px"><button class="btn dark" type="button" data-card="contact" style="width:100%;text-align:center">Get in touch</button></div></section>
<section class="box wid"><div class="bh">By the numbers<span></span></div>
<div class="stat">ARC 2026 rover<b class="r">1st of 17</b></div><div class="stat">HAVOC-2 apogee<b>~540 m</b></div><div class="stat">OSIRIS V0 DRC<b>0</b></div><div class="stat">Engineers led<b>~25</b></div></section>
</aside></div>""", N=n + 3, NP=len(P), TOC=''.join(toc), RECENT=recent, GRID=grid, PANES=''.join(panes), CW=cw, BIO=bio(4),
               TOOLS=''.join(f'<li>{t}</li>' for t in TOOLS), EXP=exp, EDU=e(D['edu']), EMAIL=D['email'], LI=D['linkedin'],
               GH=D['github'], PROFILE=profile_svg(font="'Chivo Mono',monospace"))
    js = """
const order=[...document.querySelectorAll('.toc button')].map(b=>b.dataset.card);
let cur='welcome';
function go(id,push=true){ if(!document.getElementById(id)) return; cur=id;
 document.querySelectorAll('.card-pane').forEach(s=>{ const on=s.id===id; s.hidden=!on;
  s.querySelectorAll('iframe[data-src]').forEach(f=>{ if(on){ if(f.getAttribute('src')==='about:blank') f.src=f.dataset.src; } }); });
 document.querySelectorAll('[data-card]').forEach(b=>{ if(b.closest('.toc')||b.closest('.menubar')) b.setAttribute('aria-current', b.dataset.card===id); });
 document.getElementById('pos').textContent=(order.indexOf(id)+1)+' of '+order.length;
 if(push) history.replaceState(null,'','#'+id);
 const m=document.querySelector('main'); if(m.getBoundingClientRect().top<0) m.scrollIntoView({behavior:RM?'auto':'smooth'}); }
document.addEventListener('click',ev=>{ const b=ev.target.closest('[data-card]'); if(b){ ev.preventDefault(); go(b.dataset.card); }
 const s=ev.target.closest('[data-step]'); if(s){ const i=order.indexOf(cur); go(order[(i+ +s.dataset.step+order.length)%order.length]); } });
document.addEventListener('keydown',ev=>{ if(ev.target.closest('input,textarea')) return;
 if(ev.key==='ArrowRight'&&ev.altKey) document.querySelector('[data-step="1"]').click(); });
if(location.hash.length>1) go(location.hash.slice(1),false);
const tick=()=>{ const d=new Date(); document.getElementById('clock').innerHTML=d.toLocaleTimeString('en-AU',{hour:'numeric',minute:'2-digit',hour12:true,timeZone:'Australia/Brisbane'}).replace(/\\s?(am|pm)/i,'<small> $1</small>');
 document.getElementById('date').textContent=d.toLocaleDateString('en-AU',{weekday:'long',day:'numeric',month:'long',timeZone:'Australia/Brisbane'}); };
tick(); setInterval(tick,20000);
"""
    return page('Isaac Johan Ziebarth · Trailhead stack', 'family=Schibsted+Grotesk:wght@500;600;700&family=Chivo+Mono:wght@400;500;600', css, body, js), 'trailhead'


# ======================================================================= 2. Meguri press
def meguri():
    css = """
:root{--paper:#F2EADA;--paper2:#EAE0CC;--ink:#1E1A16;--ind:#2E1499;--ind2:#241077;--red:#BB0700;--yel:#FFC908;--org:#FF5102;--rule:#1E1A16;
 --head:Fraunces,Georgia,serif;--body:Sanchez,Georgia,serif;--cap:'Chivo Mono',monospace}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 var(--body);
 background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='.85' numOctaves='2' seed='4'/%3E%3CfeColorMatrix values='0 0 0 0 .35 0 0 0 0 .27 0 0 0 0 .18 0 0 0 .08 0'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)'/%3E%3C/svg%3E")}
a{color:inherit}
.layout{display:grid;grid-template-columns:220px minmax(0,1fr);min-height:100vh}
.rail{position:sticky;top:0;height:100vh;border-right:2px solid var(--rule);display:flex;flex-direction:column;padding:22px 16px;gap:16px;background:var(--paper)}
.seal{display:grid;justify-items:center;text-align:center;text-decoration:none;gap:8px;padding-bottom:16px;border-bottom:2px solid var(--rule)}
.seal i{width:62px;height:62px;border:3px solid var(--red);color:var(--red);display:grid;place-items:center;font:normal 900 22px var(--head);outline:1px solid var(--red);outline-offset:3px}
.seal b{font:600 13px/1.3 var(--cap);letter-spacing:.2em}
.rail nav{display:flex;flex-direction:column;border:2px solid var(--rule)}
.rail nav a{display:flex;align-items:center;gap:10px;padding:10px 12px;text-decoration:none;font:600 12.5px var(--cap);letter-spacing:.12em;text-transform:uppercase;border-bottom:1px solid var(--rule)}
.rail nav a:last-child{border-bottom:0}
.rail nav a svg{width:18px;height:18px;flex:none}
.rail nav a[aria-current],.rail nav a:hover,.rail nav a:focus-visible{background:var(--red);color:#fff;outline:0}
.stamps{margin-top:auto;display:grid;gap:12px;justify-items:center}
.stamp{border:2.5px solid var(--red);color:var(--red);font:600 11px/1.25 var(--cap);letter-spacing:.08em;text-align:center;padding:7px 9px;text-transform:uppercase;transform:rotate(-4deg)}
.stamp.round{border-radius:50%;width:84px;height:84px;display:grid;place-items:center;transform:rotate(6deg)}
.stamp b{display:block;font:900 18px/1 var(--head);letter-spacing:0}
main{min-width:0}
.hero{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:38px;padding:44px 44px 30px;border-bottom:2px solid var(--rule);position:relative}
.hero:before{content:"";position:absolute;left:44px;top:22px;width:calc(48% - 40px);height:2px;background:var(--rule)}
.hero:after{content:"";position:absolute;left:calc(48% - 22px);top:18px;width:24px;height:10px;background:var(--rule)}
.kick{font:600 12px var(--cap);letter-spacing:.16em;text-transform:uppercase;margin:18px 0 18px}
h1{font:900 clamp(3rem,6.2vw,6rem)/.95 var(--head);letter-spacing:-.02em;margin:0 0 22px}
.lede{font-size:1.12rem;max-width:40ch;margin:0 0 26px}
.btns{display:flex;flex-wrap:wrap;gap:14px}
.btn{display:inline-flex;align-items:center;gap:14px;font:600 13px var(--cap);letter-spacing:.14em;text-transform:uppercase;text-decoration:none;padding:14px 18px;border:2px solid var(--ind);cursor:pointer;background:none;color:var(--ind)}
.btn.solid{background:var(--ind);color:#fff}
.btn.red{border-color:var(--red);color:var(--red)}
.btn:hover,.btn:focus-visible{background:var(--ink);border-color:var(--ink);color:#fff;outline:0}
.badges{display:grid;grid-template-columns:repeat(4,1fr);margin-top:30px;border-top:2px solid var(--rule)}
.badges div{display:flex;gap:9px;align-items:center;padding:12px 10px 0 0;font:600 11px/1.3 var(--cap);letter-spacing:.06em;text-transform:uppercase}
.badges div+div{border-left:1px solid var(--rule);padding-left:12px}
.badges svg{width:26px;height:26px;flex:none}
.plate{position:relative;border:2px solid var(--rule);background:#fff;align-self:stretch;min-height:440px}
.plate img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.plate .cart{position:absolute;right:14px;top:14px;writing-mode:vertical-rl;background:var(--paper);border:2px solid var(--red);outline:1px solid var(--red);outline-offset:-6px;
 color:var(--red);font:600 12px var(--cap);letter-spacing:.24em;padding:14px 8px;text-transform:uppercase}
.plate figcaption{position:absolute;left:0;right:0;bottom:0;background:var(--paper);border-top:2px solid var(--rule);font:600 11px var(--cap);letter-spacing:.1em;text-transform:uppercase;padding:8px 12px;display:flex;justify-content:space-between}
.edition{display:grid;grid-template-columns:minmax(0,1.15fr) repeat(3,minmax(0,1fr)) minmax(0,1.1fr);border-bottom:2px solid var(--rule)}
.edition>*{border-right:2px solid var(--rule);min-height:300px}
.edition>*:last-child{border-right:0}
.ed-main{padding:24px}
.ed-main .k{font:600 12px var(--cap);letter-spacing:.16em;color:var(--red);text-transform:uppercase}
.ed-main h2{font:900 2.1rem/1.02 var(--head);margin:10px 0}
.ed-main .r{font:900 1.5rem var(--head);color:var(--red);margin:8px 0}
.ed-main .small{font:500 13px/1.5 var(--cap)}
.tile{display:flex;flex-direction:column;text-decoration:none}
.tile .t{padding:14px 14px 10px}
.tile .t span{font:600 11px var(--cap);letter-spacing:.14em;text-transform:uppercase;display:block}
.tile .t b{font:900 1.35rem/1.1 var(--head);display:block;margin-top:4px}
.tile img{flex:1;width:100%;object-fit:cover;min-height:0;border-top:2px solid var(--rule)}
.tile:hover b,.tile:focus-visible b{color:var(--red)}
.journal{background:var(--ind);color:#fff;padding:22px;display:flex;flex-direction:column;text-decoration:none}
.journal span{font:600 11px var(--cap);letter-spacing:.16em;text-transform:uppercase;display:flex;justify-content:space-between}
.journal b{font:900 1.6rem/1.1 var(--head);margin:16px 0 10px}
.journal p{margin:0;font-size:.95rem;opacity:.9}
.journal em{margin-top:auto;font:normal 600 11px var(--cap);letter-spacing:.14em;text-transform:uppercase;border-top:1px solid #fff6;padding-top:12px}
.journal:hover,.journal:focus-visible{background:var(--ind2);outline:0}
section.sec{padding:52px 44px;border-bottom:2px solid var(--rule)}
.sec-h{display:flex;justify-content:space-between;align-items:end;gap:20px;margin-bottom:28px}
.sec-h h2{font:900 clamp(2.2rem,4vw,3.4rem)/1 var(--head);margin:0}
.sec-h p{font:600 12px var(--cap);letter-spacing:.12em;text-transform:uppercase;margin:0}
.cat{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:0;border-top:2px solid var(--rule);border-left:2px solid var(--rule)}
.cat .card{position:relative;border-right:2px solid var(--rule);border-bottom:2px solid var(--rule);padding:16px 18px 18px;display:flex;flex-direction:column;background:var(--paper)}
.cat .card:hover,.cat .card:focus-within{background:#FBF6EA}
.cat .no{display:flex;justify-content:space-between;font:600 11px var(--cap);letter-spacing:.12em;text-transform:uppercase}
.cat .icon{display:block;width:66%;margin:6px auto;aspect-ratio:1}
.cat h3{font:900 1.2rem/1.15 var(--head);margin:4px 0}
.cat h3 a{text-decoration:none}.cat h3 a::after{content:"";position:absolute;inset:0}
.cat h3 a:focus-visible{outline:3px solid var(--red);outline-offset:4px}
.cat .r{color:var(--red);font:900 1.05rem var(--head);margin:4px 0 6px}
.cat .s{font-size:.9rem;margin:0}
.studies{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:0 30px}
.studies a{display:grid;grid-template-columns:96px 1fr;gap:12px;padding:12px 0;border-bottom:1px solid var(--rule);text-decoration:none}
.studies b{font:600 12px/1.9 var(--cap);letter-spacing:.08em;color:var(--red)}
.studies a:hover span,.studies a:focus-visible span{text-decoration:underline}
.studio{display:grid;grid-template-columns:1.3fr 1fr;gap:44px}
.exp{list-style:none;margin:0;padding:0;border-top:2px solid var(--rule)}
.exp li{padding:11px 0;border-bottom:1px solid var(--rule)}
.exp b{font:900 1.02rem var(--head);display:block}.exp i{font:normal 600 11px var(--cap);letter-spacing:.08em;text-transform:uppercase}
.foot{background:var(--ind);color:#fff;padding:56px 44px;display:grid;grid-template-columns:1fr auto;gap:30px;align-items:end}
.foot h2{font:900 clamp(2.2rem,5vw,4.2rem)/1 var(--head);margin:0}
.foot .btn{border-color:#fff;color:#fff}.foot .btn.solid{background:#fff;color:var(--ind)}
@media (max-width:1100px){.edition{grid-template-columns:1fr 1fr 1fr}.ed-main{grid-column:1/-1;border-bottom:2px solid var(--rule)}.journal{grid-column:1/-1}.edition>*{min-height:240px}}
@media (max-width:860px){.layout{grid-template-columns:1fr}.rail{position:sticky;top:0;z-index:20;height:auto;flex-direction:row;align-items:center;padding:8px 12px;border-right:0;border-bottom:2px solid var(--rule)}
 .seal{border:0;padding:0;grid-template-columns:auto auto;align-items:center}.seal i{width:40px;height:40px;font-size:15px}.seal b{display:none}
 .rail nav{flex-direction:row;overflow-x:auto;border:0}.rail nav a{border:0;padding:8px 7px;font-size:11px;letter-spacing:.06em}.rail nav a svg{display:none}.stamps{display:none}
 .hero{grid-template-columns:1fr;padding:30px 16px}.hero:before,.hero:after{display:none}.plate{min-height:300px}.badges{grid-template-columns:1fr 1fr;gap:10px 0}.badges div:nth-child(3){border-left:0;padding-left:0}
 section.sec{padding:40px 16px}.edition{grid-template-columns:1fr}.edition>*{border-right:0;border-bottom:2px solid var(--rule)}.studio{grid-template-columns:1fr}.foot{grid-template-columns:1fr;padding:40px 16px}}
"""
    ico = {
        'home': '<path d="M3 11l9-7 9 7v9H3z"/>', 'work': '<rect x="3" y="7" width="18" height="13"/><path d="M8 7V4h8v3"/>',
        'cw': '<path d="M4 5h7v14H4zM13 5h7v14h-7z"/>', 'how': '<circle cx="12" cy="12" r="8"/><path d="M12 7v5l3 3"/>',
        'about': '<circle cx="12" cy="8" r="4"/><path d="M4 21c1-5 15-5 16 0"/>', 'contact': '<rect x="3" y="5" width="18" height="14"/><path d="M3 6l9 7 9-7"/>'}
    svg = lambda k: f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">{ico[k]}</svg>'
    t = MAIN[0]
    cat = ''.join(f"""<li class="card"><div class="no"><span>No. {i + 1:02d}</span><span>{e(YEAR[p['slug']])}</span></div>{p['icon']}
<h3><a href="{p['href']}">{e(p['title'])}</a></h3><p class="r">{e(p['result'])}</p><p class="s">{e(p['summary'])}</p></li>""" for i, p in enumerate(P))
    studies = ''.join(f'<li><a href="{c["href"]}"><b>{e(c["meta"])}</b><span>{e(c["title"])}</span></a></li>' for c in D['coursework'])
    exp = ''.join(f'<li><b>{e(r)}</b>{e(o)}<br><i>{e(w)}</i></li>' for r, o, w in D['experience'])
    body = fill("""<div class="layout"><aside class="rail" aria-label="Site">
<a class="seal" href="#top"><i>IJZ</i><b>ISAAC J.<br>ZIEBARTH</b></a>
<nav aria-label="Main"><a href="#top" aria-current="page">@@I_HOME@@Home</a><a href="#work">@@I_WORK@@Projects</a><a href="#studies">@@I_CW@@Coursework</a><a href="#method">@@I_HOW@@Method</a><a href="#studio">@@I_ABOUT@@About</a><a href="#contact">@@I_CONTACT@@Contact</a></nav>
<div class="stamps" aria-hidden="true"><div class="stamp"><b>1st of 17</b>ARC 2026</div><div class="stamp round"><span><b>2027</b>Graduate</span></div></div></aside>
<main id="main">
<section class="hero" id="top" aria-labelledby="me"><div><p class="kick">Isaac Johan Ziebarth · Mechatronic engineering · UQ</p>
<h1 id="me">Engineer the system whole.</h1>
<p class="lede">Flight firmware, rover autonomy, circuit boards and the ground stations that read them back, built one layer at a time and tested on the real thing.</p>
<div class="btns"><a class="btn solid" href="#work">See the work <span aria-hidden="true">›</span></a><a class="btn red" href="mailto:@@EMAIL@@">Email me <span aria-hidden="true">›</span></a></div>
<div class="badges">
<div><svg viewBox="0 0 26 26" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M13 3l3 7h-6zM10 10v9l3 4 3-4v-9"/></svg>C++ flight firmware</div>
<div><svg viewBox="0 0 26 26" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="4" y="9" width="18" height="9"/><circle cx="8" cy="20" r="2.5"/><circle cx="18" cy="20" r="2.5"/><path d="M13 9V4h5"/></svg>ROS 2 autonomy</div>
<div><svg viewBox="0 0 26 26" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="4" y="4" width="18" height="18"/><path d="M8 4v18M4 9h4M4 14h4M12 9h6v6h-6z"/></svg>KiCad boards</div>
<div><svg viewBox="0 0 26 26" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 21l9-9M9 4a13 13 0 0 1 13 13M9 9a8 8 0 0 1 8 8"/></svg>Ground stations</div></div></div>
<figure class="plate" style="margin:0"><img src="/assets/img/projects/osiris-v0-top.jpg" alt="OSIRIS V0, the flight computer board I designed in KiCad"><span class="cart">Own design · 2026</span>
<figcaption><span>OSIRIS V0 flight computer</span><span>0 DRC violations</span></figcaption></figure></section>
<section class="edition" aria-label="Flagship project"><div class="ed-main"><p class="k">Current edition</p><h2>@@T_TITLE@@</h2><p class="r">@@T_RES@@</p>
<p class="small">@@T_META@@</p><p style="font-size:.95rem">@@T_SUM@@</p><a class="btn" href="@@T_HREF@@">Read the write-up ›</a></div>
<a class="tile" href="/projects/theseus.html"><div class="t"><span>Map</span><b>FAST-LIO2 cloud</b></div><img src="/assets/figures/theseus-map-cloud.webp" alt="" style="object-position:40% 40%"></a>
<a class="tile" href="/projects/havoc2-cosmos.html"><div class="t"><span>Flight data</span><b>540 m, logged</b></div><img src="/assets/img/projects/havoc2-share.jpg" alt="" style="object-position:0 0"></a>
<a class="tile" href="/projects/weather-station.html"><div class="t"><span>Hardware</span><b>Range weather</b></div><img src="/assets/img/projects/weather-station-open.jpg" alt=""></a>
<a class="journal" href="/projects/theseus.html#what-went-wrong"><span>Field notes <i aria-hidden="true">→</i></span><b>What went wrong on Theseus V</b>
<p>IMU vibration, a QoS mismatch and what changed for Theseus VI.</p><em>Read the notes</em></a></section>
<section class="sec" id="work" aria-labelledby="wh"><div class="sec-h"><h2 id="wh">Catalogue of work</h2><p>@@NP@@ pieces · 2022 to now</p></div><ul class="cat">@@CAT@@</ul></section>
<section class="sec" id="method" aria-labelledby="mh"><div class="sec-h"><h2 id="mh">Method</h2><p>How I build</p></div>
<div class="studio"><div><p>I start from a model: what the system should do, measured against what it does on the bench. Then I build it a layer at a time, board, firmware, software and ground station, and test each on real hardware before the next goes on.</p>
<p>When something goes wrong in the field I write it down, fix the cause and carry the fix into the next build. Each project page ends with what went wrong and what changed.</p></div>
<div><p class="kick" style="margin-top:0">Tools</p><p>@@TOOLS@@</p></div></div></section>
<section class="sec" id="studies" aria-labelledby="sh"><div class="sec-h"><h2 id="sh">Coursework</h2><p>@@NC@@ graded reports</p></div><ul class="studies">@@STUDIES@@</ul></section>
<section class="sec" id="studio" aria-labelledby="ah"><div class="sec-h"><h2 id="ah">About</h2><p>The studio</p></div><div class="studio"><div>@@BIO@@</div><div><ul class="exp">@@EXP@@</ul><p style="font-size:.9rem">@@EDU@@</p></div></div></section>
<section class="foot" id="contact"><h2>Commission the next build.</h2><div class="btns"><a class="btn solid" href="mailto:@@EMAIL@@">Email me ›</a><a class="btn" href="@@LI@@">LinkedIn ›</a><a class="btn" href="@@GH@@">GitHub ›</a></div></section>
</main></div>""", I_HOME=svg('home'), I_WORK=svg('work'), I_CW=svg('cw'), I_HOW=svg('how'), I_ABOUT=svg('about'), I_CONTACT=svg('contact'),
                EMAIL=D['email'], LI=D['linkedin'], GH=D['github'], T_TITLE=e(t['title']), T_RES=e(t['result']), T_META=e(t['meta']),
                T_SUM=e(t['summary']), T_HREF=t['href'], NP=len(P), CAT=cat, TOOLS=e(', '.join(TOOLS)) + '.', NC=len(D['coursework']),
                STUDIES=studies, BIO=bio(4), EXP=exp, EDU=e(D['edu']))
    js = """
const links=[...document.querySelectorAll('.rail nav a')]; const secs=links.map(a=>document.querySelector(a.getAttribute('href')));
const io=new IntersectionObserver(es=>es.forEach(x=>{ if(x.isIntersecting){ links.forEach(a=>a.toggleAttribute('aria-current', a.getAttribute('href')==='#'+x.target.id)); } }),{rootMargin:'-40% 0px -55% 0px'});
secs.forEach(s=>s&&io.observe(s));
"""
    return page('Isaac Johan Ziebarth · Meguri press', 'family=Chivo+Mono:wght@500;600', css, body, js), 'meguri'


# ======================================================================= 3. NASA-punk mission console (+ six-pack gauges, emergency broadcast)
def gauge(label, value, frac, unit, sub):
    import math
    ticks = ''
    for i in range(0, 41):
        a = math.radians(-225 + i * 270 / 40)
        r1, r2 = (40, 46) if i % 5 else (36, 46)
        ticks += f'<line x1="{50 + r1 * math.cos(a):.1f}" y1="{50 + r1 * math.sin(a):.1f}" x2="{50 + r2 * math.cos(a):.1f}" y2="{50 + r2 * math.sin(a):.1f}"/>'
    ang = -225 + frac * 270
    return f"""<figure class="gauge" style="--a:{ang}deg" role="img" aria-label="{e(label)}: {e(value)} {e(unit)}">
<svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="49" class="bez"/><circle cx="50" cy="50" r="46" class="face"/><g class="tk">{ticks}</g>
<text x="50" y="34" class="gl">{e(label)}</text><text x="50" y="74" class="gv">{e(value)}</text><text x="50" y="84" class="gu">{e(unit)}</text>
<g class="needle"><path d="M50 50 L50 10" /><circle cx="50" cy="50" r="5"/></g></svg><figcaption>{e(sub)}</figcaption></figure>"""


def console():
    css = """
:root{--wall:#2B2823;--panel:#DDD6C6;--panel-lo:#D3CBB9;--panel-hi:#E9E3D6;--seam:#A39A86;--seam2:#7D7564;--ink:#1D1B16;--ink2:#433E34;--engrave:#70220D;
 --win:#121110;--amber:#FFB22E;--green:#7FE06A;--key:#D9531F;--keylit:#FF7A3D;--caution:#F2C230;--warn:#BB0700;--teal:#2F6F6A;--mustard:#D9A21B;
 --lab:'Barlow Condensed',Arial Narrow,sans-serif;--disp:Archivo,system-ui,sans-serif;--crt:'VT323',monospace;--body:Sanchez,Georgia,serif}
body{margin:0;background:var(--wall);color:var(--ink);font:17px/1.55 var(--body);
 background-image:linear-gradient(90deg,#0000 0 49.5%,#0002 50%,#0000 50.5%),linear-gradient(#ffffff06,#0000);background-size:60px 100%,100% 100%}
a{color:inherit}
.panel{background:linear-gradient(180deg,var(--panel-hi),var(--panel) 30%,var(--panel-lo));border:1px solid var(--seam2);box-shadow:inset 0 1px 0 #fff8,inset 0 -2px 0 #0001,0 2px 0 #0004;position:relative;border-radius:3px}
.panel>.scr{position:absolute;width:9px;height:9px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#f4efe3,#8d8574 70%);box-shadow:0 0 0 1px #6f6858}
.panel>.scr::after{content:"";position:absolute;left:1px;right:1px;top:4px;height:1px;background:#5a5446;transform:rotate(35deg)}
.s1{left:8px;top:8px}.s2{right:8px;top:8px}.s3{left:8px;bottom:8px}.s4{right:8px;bottom:8px}
.eng{font:600 12px/1 var(--lab);letter-spacing:.2em;text-transform:uppercase;color:var(--engrave)}
.win{background:var(--win);border-radius:3px;box-shadow:inset 0 2px 6px #000,0 1px 0 #fff6;color:var(--amber);font:400 26px/1 var(--crt);padding:8px 12px;text-shadow:0 0 8px #ffb22e66}
.top{position:sticky;top:0;z-index:30;display:flex;align-items:stretch;gap:12px;padding:10px 16px;margin:0;border-radius:0;border-width:0 0 1px}
.plate{display:flex;flex-direction:column;justify-content:center;padding:0 18px 0 8px;border-right:1px solid var(--seam)}
.plate b{font:800 22px/1 var(--disp);font-stretch:125%;letter-spacing:.01em}
.readouts{display:flex;gap:10px;align-items:center}
.ro{display:flex;flex-direction:column;gap:4px}
.ro .win{font-size:24px;min-width:110px;text-align:right}
.lamps{display:flex;gap:10px;align-items:center;padding:0 8px}
.lamp{display:flex;flex-direction:column;align-items:center;gap:5px;font:600 10px var(--lab);letter-spacing:.14em;color:var(--engrave)}
.lamp i{width:16px;height:16px;border-radius:50%;background:#3a3631;box-shadow:inset 0 1px 2px #000}
.lamp.on i{background:radial-gradient(circle at 40% 35%,#d9ffcc,var(--green) 55%,#3c8a2f);box-shadow:0 0 10px var(--green)}
.keys{margin-left:auto;display:flex;gap:8px;align-items:center}
.k{display:inline-grid;place-items:center;min-width:92px;height:44px;padding:0 12px;background:linear-gradient(var(--panel-hi),#d6cebd);border:1px solid var(--seam2);border-radius:4px;
 box-shadow:0 3px 0 #8d8574,inset 0 1px 0 #fff;font:700 14px var(--lab);letter-spacing:.16em;text-transform:uppercase;text-decoration:none;color:var(--ink);cursor:pointer}
.k:hover,.k:focus-visible{background:linear-gradient(#fff3d9,var(--caution));outline:0}
.k:active{transform:translateY(2px);box-shadow:0 1px 0 #8d8574}
.k.lit{background:linear-gradient(var(--keylit),var(--key));color:var(--ink);box-shadow:0 3px 0 #7a2c0f,0 0 18px #ff7a3d66}
.bulletin{display:flex;align-items:stretch;background:var(--warn);color:#fff;border-top:6px solid transparent;border-bottom:6px solid transparent;
 border-image:repeating-linear-gradient(-45deg,#fff 0 12px,var(--warn) 12px 24px) 6;overflow:hidden;position:sticky;top:66px;z-index:25}
.bulletin .tag{flex:none;background:#fff;color:var(--warn);font:700 15px/1 var(--lab);letter-spacing:.2em;padding:11px 16px;display:flex;align-items:center;gap:10px}
.bulletin .tag i{width:10px;height:10px;border-radius:50%;background:var(--warn);animation:blink 1.2s steps(2) infinite}
.crawl{white-space:nowrap;font:700 17px/40px var(--lab);letter-spacing:.14em;text-transform:uppercase;animation:crawl 38s linear infinite;padding-left:24px}
@keyframes crawl{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@keyframes blink{50%{opacity:.15}}
.wrap{max-width:1400px;margin:0 auto;padding:22px 18px 100px}
.hero{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr);gap:18px}
.hero .panel{padding:30px 32px}
.who{display:grid;grid-template-columns:200px 1fr;gap:24px;align-items:start}
.crt{position:relative;background:var(--win);padding:10px;border-radius:10px;box-shadow:inset 0 0 0 3px #2a2722,0 2px 0 #fff6}
.crt img{border-radius:6px;filter:sepia(1) saturate(2.4) hue-rotate(-12deg) brightness(.9) contrast(1.1);aspect-ratio:1;object-fit:cover;width:100%;height:auto;transition:filter .4s}
.crt::after{content:"";position:absolute;inset:10px;border-radius:6px;background:repeating-linear-gradient(#0000 0 2px,#0005 2px 3px);pointer-events:none}
.crt:hover img{filter:none}
.crt figcaption{font:400 16px var(--crt);color:var(--amber);padding-top:6px}
h1{font:800 clamp(2.4rem,4.4vw,4.4rem)/.92 var(--disp);font-stretch:125%;letter-spacing:-.01em;margin:8px 0 14px}
.role{font-size:1.05rem;margin:0 0 16px;max-width:42ch}
.big{display:flex;gap:12px;flex-wrap:wrap;margin:6px 0 18px}
.big .win{font-size:44px;padding:10px 16px}
.big .win small{display:block;font:600 11px var(--lab);letter-spacing:.18em;color:#b9ad92;text-shadow:none;margin-top:4px}
.cta{display:flex;flex-wrap:wrap;gap:10px}
.primary{display:grid;grid-template-rows:auto 1fr;position:relative}
.primary .hd{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;gap:12px;flex-wrap:wrap}
.screen{background:#0d0c0b;border-radius:10px;padding:10px;box-shadow:inset 0 0 0 3px #2a2722;min-height:440px;position:relative}
.screen iframe{border:0;width:100%;height:100%;min-height:420px;border-radius:6px;background:#fff;display:block}
.arrow{position:absolute;left:-58px;top:46%;width:100px;height:60px;z-index:3;pointer-events:none}
.six{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;margin-top:18px;padding:22px 24px}
.gauge{margin:0;text-align:center}
.gauge svg{width:100%;max-width:150px}
.gauge .bez{fill:#1b1a17;stroke:#5c564a;stroke-width:2}
.gauge .face{fill:#121110}
.gauge .tk line{stroke:#e9e3d6;stroke-width:1.2}
.gauge .gl{fill:#b9ad92;font:600 7px var(--lab);letter-spacing:.14em;text-anchor:middle;text-transform:uppercase}
.gauge .gv{fill:var(--amber);font:400 15px var(--crt);text-anchor:middle}
.gauge .gu{fill:#b9ad92;font:600 5.5px var(--lab);letter-spacing:.12em;text-anchor:middle}
.gauge .needle{transform-origin:50px 50px;transform:rotate(calc(var(--a) + 90deg));transition:transform 1.6s cubic-bezier(.3,1.4,.5,1)}
.gauge .needle path{stroke:var(--green);stroke-width:2.4;stroke-linecap:round}
.gauge .needle circle{fill:#d9d2c0}
.gauge.zero .needle{transform:rotate(-135deg)}
.gauge figcaption{font:600 12px/1.3 var(--lab);letter-spacing:.12em;text-transform:uppercase;color:var(--engrave);margin-top:6px}
.sec-h{display:flex;align-items:center;gap:16px;margin:48px 0 16px}
.sec-h h2{font:800 30px/1 var(--disp);font-stretch:125%;color:var(--panel);margin:0}
.sec-h .rule{flex:1;height:10px;background:repeating-linear-gradient(-45deg,var(--caution) 0 10px,var(--ink) 10px 20px);border-radius:2px;opacity:.9}
.sec-h p{font:600 13px var(--lab);letter-spacing:.18em;color:#b9ad92;margin:0;text-transform:uppercase}
.mods{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.mod{padding:18px 20px 16px;display:flex;flex-direction:column}
.mod .hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;padding:0 6px}
.mod .bay{background:#f6f1e5;border-radius:4px;box-shadow:inset 0 2px 5px #0003;padding:6px}
.mod .icon{display:block;width:66%;margin:0 auto;aspect-ratio:1}
.mod h3{font:800 1.12rem/1.15 var(--disp);font-stretch:112%;margin:12px 0 4px}
.mod h3 button{all:unset;cursor:pointer}.mod h3 button::after{content:"";position:absolute;inset:0}
.mod h3 button:focus-visible{outline:3px solid var(--key);outline-offset:4px}
.mod .meta{font:600 12px var(--lab);letter-spacing:.12em;text-transform:uppercase;color:var(--ink2);margin:0 0 10px}
.mod .rrow{display:flex;gap:10px;align-items:center;margin-top:auto}
.mod .rrow .win{flex:1;font-size:22px;padding:6px 10px}
.mod .st{display:flex;align-items:center;gap:6px;font:700 12px var(--lab);letter-spacing:.14em;color:var(--engrave)}
.mod .st i{width:12px;height:12px;border-radius:50%;background:radial-gradient(circle at 40% 35%,#d9ffcc,var(--green) 55%,#3c8a2f);box-shadow:0 0 8px var(--green)}
.mod .st.amb i{background:radial-gradient(circle at 40% 35%,#fff0c9,var(--amber) 55%,#a86a00);box-shadow:0 0 8px var(--amber)}
.mod:hover,.mod:focus-within{box-shadow:inset 0 1px 0 #fff8,0 0 0 3px var(--caution),0 2px 0 #0004}
.term{background:var(--win);border-radius:8px;box-shadow:inset 0 0 0 3px #2a2722;padding:18px 22px;color:var(--amber);font:400 22px/1.35 var(--crt);text-shadow:0 0 6px #ffb22e55}
.term ul{list-style:none;margin:0;padding:0;columns:2;column-gap:40px}
.term li{break-inside:avoid;padding:4px 0}
.term a{text-decoration:none;display:grid;grid-template-columns:110px 1fr}
.term a:hover,.term a:focus-visible{background:var(--amber);color:var(--win);text-shadow:none;outline:0}
.term .hd{color:var(--green);margin-bottom:10px}
.crew{display:grid;grid-template-columns:1.35fr 1fr;gap:18px}
.crew .panel{padding:26px 30px}
.crew p{margin:0 0 12px}
.rec{width:100%;border-collapse:collapse;font-size:.92rem}
.rec td{border-top:1px solid var(--seam);padding:8px 4px;vertical-align:top}
.rec td:first-child{font:600 13px var(--lab);letter-spacing:.08em;white-space:nowrap;color:var(--engrave)}
.rec b{display:block;font:800 1rem var(--disp);font-stretch:110%}
.tx{margin-top:48px;padding:34px;display:flex;align-items:center;gap:26px;flex-wrap:wrap;border:6px solid;border-image:repeating-linear-gradient(-45deg,var(--caution) 0 14px,var(--ink) 14px 28px) 6}
.tx h2{font:800 clamp(2rem,4vw,3.4rem)/1 var(--disp);font-stretch:125%;margin:0}
.tx .k{height:60px;min-width:160px;font-size:18px}
dialog.mon{width:min(1220px,calc(100vw - 24px));max-height:calc(100vh - 24px);padding:14px;border:0;border-radius:14px;background:var(--wall);color:var(--ink);overflow:auto}
dialog.mon::backdrop{background:#000a}
.mon .inner{display:grid;grid-template-columns:minmax(260px,380px) 1fr;gap:14px}
.mon .side{padding:24px}
.mon .scr2{background:#0d0c0b;border-radius:10px;padding:10px;min-height:540px;position:relative}
.mon .scr2 iframe,.mon .scr2 img{position:absolute;inset:10px;width:calc(100% - 20px);height:calc(100% - 20px);border:0;border-radius:6px;background:#fff;object-fit:contain}
.mon .term{font-size:19px;padding:10px 14px;margin:10px 0}
dl{margin:10px 0;font-size:.9rem} dl div{border-top:1px solid var(--seam);padding:6px 0}
dt{font:600 12px var(--lab);letter-spacing:.14em;text-transform:uppercase;color:var(--engrave)} dd{margin:0}
.mon .bar{display:flex;gap:10px;margin-top:12px;flex-wrap:wrap}
@media (max-width:1180px){.six{grid-template-columns:repeat(3,1fr)}.lamps{display:none}}
@media (max-width:980px){.hero,.crew,.mon .inner{grid-template-columns:1fr}.arrow{display:none}.readouts{display:none}}
@media (max-width:700px){.top{flex-wrap:wrap;padding:8px 10px;gap:6px}.plate{border:0;padding:0}.plate b{font-size:17px}.keys{margin:0;width:100%;overflow-x:auto}.k{min-width:0;height:36px;font-size:12px;padding:0 9px}
 .bulletin{top:98px}.bulletin .tag{font-size:12px;padding:8px}.crawl{font-size:14px;line-height:32px}
 .wrap{padding:16px 12px 100px}.hero .panel{padding:22px 18px}.who{grid-template-columns:1fr}.crt{max-width:220px}.big .win{font-size:34px}
 .six{grid-template-columns:repeat(2,1fr);padding:16px}.term ul{columns:1}.term a{grid-template-columns:1fr}.tx{padding:22px}.mon .scr2{min-height:380px}}
@media (prefers-reduced-motion:reduce){.crawl{animation:none;white-space:normal;line-height:1.4;padding:8px 14px}.bulletin .tag i{animation:none}.gauge .needle{transition:none}}
"""
    scr = '<span class="scr s1"></span><span class="scr s2"></span><span class="scr s3"></span><span class="scr s4"></span>'
    t = MAIN[0]
    status = {'osiris': ('ON BENCH', 'amb'), 'digital-orrery': ('LIVE', '')}
    mods = ''.join(f"""<li class="panel mod">{scr}<div class="hdr"><span class="eng">Module {i + 1:02d} · {e((p['tags'] or ['misc'])[0])}</span><span class="st {status.get(p['slug'], ('', ''))[1]}"><i></i>{e(status.get(p['slug'], (p['short'][2],))[0])}</span></div>
<div class="bay card">{p['icon']}</div><h3><button type="button" data-open="{p['slug']}">{e(p['title'])}</button></h3><p class="meta">{e(p['meta'])}</p>
<div class="rrow"><span class="win">{e(p['short'][1])}</span></div></li>""" for i, p in enumerate(P))
    term = ''.join(f'<li><a href="{c["href"]}"><span>{e(c["meta"].split(" · ")[0])}</span><span>{e(c["title"].upper())}</span></a></li>' for c in D['coursework'])
    rec = ''.join(f'<tr><td>{e(w)}</td><td><b>{e(r)}</b>{e(o)}</td></tr>' for r, o, w in D['experience'])
    crawl = ' ★ '.join(['Official broadcast', 'Isaac Johan Ziebarth is available for 2027 graduate roles and internships',
                        'Avionics and embedded systems', 'Robotics and autonomy', 'Guidance, navigation and control',
                        'Theseus V placed 1st of 17 at the 2026 Australian Rover Challenge', 'HAVOC-2 first flight to about 540 m, every frame passed'])
    six = (gauge('Rover rank', '1st', 1.0, 'OF 17', 'ARC 2026') + gauge('Apogee', '540', 540 / 600, 'METRES', 'HAVOC-2') +
           gauge('DRC faults', '0', 0.0, 'OSIRIS V0', 'KiCad checks') + gauge('Sim flights', '200', 200 / 250, 'AIRBRAKES', '4 controllers') +
           gauge('Rows OK', '98,218', 0.99, 'WX STATION', 'All passed') + gauge('Lighter', '21%', 0.21 / 0.3, 'CRANK ARM', 'Ti, printed'))
    body = fill("""<header class="panel top">@@SCR@@<div class="plate"><span class="eng">Crew · IJZ-27</span><b>I.J. Ziebarth</b></div>
<div class="readouts"><div class="ro"><span class="eng">Brisbane</span><span class="win" id="clock">--:--</span></div><div class="ro"><span class="eng">To graduation</span><span class="win" id="tminus">T-000 D</span></div></div>
<div class="lamps" aria-label="Seeking roles in"><span class="lamp on"><i></i>SEEKING</span><span class="lamp on"><i></i>AVIONICS</span><span class="lamp on"><i></i>AUTONOMY</span><span class="lamp on"><i></i>GNC</span></div>
<nav class="keys" aria-label="Main"><a class="k" href="#log">Projects</a><a class="k" href="#training">Coursework</a><a class="k" href="#crew">About</a><a class="k lit" href="#tx">Contact</a></nav></header>
<div class="bulletin" role="region" aria-label="Broadcast"><span class="tag"><i></i>ON AIR</span><div class="crawl" aria-hidden="true">@@CRAWL@@ ★ @@CRAWL@@ ★ </div><span class="vh">@@CRAWL@@</span></div>
<main class="wrap" id="main">
<div class="hero"><section class="panel" aria-labelledby="me">@@SCR@@<div class="who"><figure class="crt" style="margin:0"><img src="/assets/img/profile.jpg" alt="" width="800" height="800"><figcaption>CREW FILE 01 · HOVER</figcaption></figure>
<div><span class="eng">Mechatronic engineering · UQ · class of 2027</span><h1 id="me">Isaac Johan Ziebarth</h1>
<p class="role">I write robot and flight software, design the boards it runs on and build the ground stations that read it back.</p></div></div>
<div class="big"><span class="win">1ST/17<small>ROVER · ARC 2026</small></span><span class="win">~540 M<small>HAVOC-2 APOGEE</small></span></div>
<div class="cta"><a class="k lit" href="mailto:@@EMAIL@@">Transmit</a><a class="k" href="#log">Mission log</a><a class="k" href="@@LI@@">LinkedIn</a><a class="k" href="@@GH@@">GitHub</a></div></section>
<section class="panel primary" aria-labelledby="pm" style="padding:24px 26px">@@SCR@@
<svg class="arrow" viewBox="0 0 100 60" aria-hidden="true"><path d="M2 30 H70" stroke="#BB0700" stroke-width="16"/><path d="M62 4 L98 30 L62 56 Z" fill="#BB0700"/></svg>
<div class="hd"><div><span class="eng">Primary mission · @@T_META@@</span><h2 id="pm" style="font:800 1.7rem/1.1 var(--disp);font-stretch:118%;margin:6px 0 0">@@T_TITLE@@</h2></div>
<button class="k" type="button" data-open="@@T_SLUG@@">Open file</button></div>
<div class="screen"><iframe src="@@T_FIG@@" title="Live figure: @@T_TITLE@@"></iframe></div></section></div>
<section class="panel six" aria-label="Results at a glance">@@SCR@@@@SIX@@</section>
<div class="sec-h" id="log"><h2>Mission log</h2><span class="rule"></span><p>@@NP@@ modules</p></div><ul class="mods">@@MODS@@</ul>
<div class="sec-h" id="training"><h2>Training record</h2><span class="rule"></span><p>Coursework</p></div>
<div class="term"><p class="hd" style="margin:0 0 10px">&gt; QUERY COURSEWORK --ALL ... @@NC@@ RECORDS</p><ul>@@TERM@@</ul></div>
<div class="sec-h" id="crew"><h2>Crew file</h2><span class="rule"></span><p>About</p></div>
<div class="crew"><section class="panel" aria-label="About">@@SCR@@@@BIO@@<p><span class="eng">Systems</span><br>@@TOOLS@@</p></section>
<section class="panel" aria-label="Service record">@@SCR@@<span class="eng">Service record</span><table class="rec">@@REC@@</table><p style="font-size:.88rem;margin-top:12px">@@EDU@@</p></section></div>
<section class="panel tx" id="tx" aria-labelledby="txh"><h2 id="txh">Open a channel.</h2><a class="k lit" href="mailto:@@EMAIL@@">Transmit</a><a class="k" href="@@LI@@">LinkedIn</a><a class="k" href="@@GH@@">GitHub</a></section>
</main>
<dialog class="mon" aria-labelledby="m-title"><div class="inner"><div class="panel side">@@SCR@@<span class="eng" id="m-meta"></span><h3 id="m-title" style="font:800 1.8rem/1.05 var(--disp);font-stretch:115%;margin:8px 0"></h3>
<div class="term" id="m-res"></div><p id="m-out"></p><div id="m-facts"></div>
<div class="bar"><a class="k lit" id="m-full" href="#">Full report</a><button class="k" type="button" id="m-next">Next</button><button class="k" type="button" id="m-close">Close</button></div></div>
<div class="scr2" id="m-live"></div></div></dialog>""", SCR=scr, CRAWL=e(crawl.upper()), EMAIL=D['email'], LI=D['linkedin'], GH=D['github'],
                T_META=e(t['meta']), T_TITLE=e(t['title']), T_SLUG=t['slug'], T_FIG=t['figure'], SIX=six, NP=len(P), MODS=mods,
                NC=len(D['coursework']), TERM=term, BIO=bio(4), TOOLS=e(', '.join(TOOLS)), REC=rec, EDU=e(D['edu']))
    js = """
const tick=()=>{ const d=new Date(); document.getElementById('clock').textContent=d.toLocaleTimeString('en-AU',{hour:'2-digit',minute:'2-digit',hour12:false,timeZone:'Australia/Brisbane'});
 const days=Math.ceil((new Date('2027-11-30T00:00:00+10:00')-d)/864e5); document.getElementById('tminus').textContent='T-'+String(days).padStart(3,'0')+' D'; };
tick(); setInterval(tick,20000);
const gs=[...document.querySelectorAll('.gauge')]; if(!RM){ gs.forEach(g=>g.classList.add('zero'));
 const io=new IntersectionObserver(es=>es.forEach(x=>{ if(x.isIntersecting){ setTimeout(()=>x.target.classList.remove('zero'),120); io.unobserve(x.target);} }),{threshold:.5}); gs.forEach(g=>io.observe(g)); }
const dlg=document.querySelector('dialog.mon'); let cur=0;
function show(i){ cur=(i+PROJ.length)%PROJ.length; const p=PROJ[cur];
 document.getElementById('m-meta').textContent=p.meta; document.getElementById('m-title').textContent=p.title;
 document.getElementById('m-res').textContent='> RESULT: '+p.result.toUpperCase(); document.getElementById('m-out').textContent=p.outcome;
 document.getElementById('m-facts').innerHTML=factsHTML(p); document.getElementById('m-live').innerHTML=figureHTML(p); document.getElementById('m-full').href=p.href; }
document.querySelectorAll('[data-open]').forEach(b=>b.addEventListener('click',()=>{ show(PROJ.findIndex(p=>p.slug===b.dataset.open)); dlg.showModal(); }));
document.getElementById('m-next').onclick=()=>show(cur+1); document.getElementById('m-close').onclick=()=>dlg.close();
dlg.addEventListener('close',()=>document.getElementById('m-live').innerHTML='');
"""
    return page('Isaac Johan Ziebarth · Mission console', 'family=Archivo:wdth,wght@100..125,700..800&family=Barlow+Condensed:wght@600;700&family=VT323', css, body, js), 'console'


# ======================================================================= 4. Theatre poster (+ variable-type scale)
def poster():
    css = """
:root{--yel:#FFC908;--red:#BB0700;--org:#FF5102;--ind:#2E1499;--cream:#FFF4D6;--ink:#1A0F3D;
 --disp:'Anton',Impact,sans-serif;--head:Fraunces,Georgia,serif;--body:Sanchez,Georgia,serif;--cond:'Barlow Condensed',Arial Narrow,sans-serif}
body{margin:0;background:var(--yel);color:var(--ind);font:17px/1.55 var(--body)}
a{color:inherit}
.bar{position:sticky;top:0;z-index:30;display:flex;align-items:stretch;background:var(--cream);border-bottom:4px solid var(--ind);font:700 17px/1 var(--cond);letter-spacing:.08em;text-transform:uppercase}
.bar .nm{display:flex;align-items:center;padding:0 18px;font:400 24px/1 var(--disp);letter-spacing:.02em;text-decoration:none;border-right:4px solid var(--ind)}
.bar nav{display:flex}
.bar nav a{display:flex;align-items:center;padding:0 16px;text-decoration:none;border-right:2px solid var(--ind)}
.bar nav a:hover,.bar nav a:focus-visible{background:var(--ind);color:var(--cream);outline:0}
.bar .next{margin-left:auto;display:flex;align-items:center;gap:10px;padding:0 16px;font-size:14px}
.bar .next b{font:400 22px var(--disp);color:var(--red);letter-spacing:.02em}
.bar .tix{display:flex;align-items:center;padding:14px 20px;background:var(--red);color:var(--cream);text-decoration:none;font-size:18px}
.bar .tix:hover,.bar .tix:focus-visible{background:var(--ind);outline:0}
.sheet{display:grid;grid-template-columns:96px minmax(0,1fr) 96px;border-bottom:4px solid var(--ind)}
.dates{background:var(--cream);display:flex;flex-direction:column;border-right:4px solid var(--ind)}
.dates.r{border-right:0;border-left:4px solid var(--ind)}
.dates div{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;border-bottom:2px solid var(--ind);padding:8px 4px;font:700 12px/1.1 var(--cond);letter-spacing:.06em;text-transform:uppercase}
.dates div b{font:400 30px/1 var(--disp);color:var(--red)}
.dates div:last-child{border-bottom:0}
.dates div.hot{background:var(--red);color:var(--cream)}.dates div.hot b{color:var(--yel)}
.stage{position:relative;overflow:hidden;padding:30px 34px 26px;min-height:620px;
 background:radial-gradient(circle at 70% 60%,#FFE070 0 18%,transparent 19%),var(--yel)}
.halo{position:absolute;right:4%;top:6%;width:min(46%,560px);aspect-ratio:1;border-radius:50%;background:repeating-radial-gradient(circle,var(--org) 0 10px,transparent 10px 22px);opacity:.55}
.title{position:relative;z-index:2;font:400 clamp(4rem,11vw,10.5rem)/.84 var(--disp);text-transform:uppercase;color:var(--ind);margin:0;letter-spacing:.005em;
 text-shadow:5px 5px 0 var(--cream)}
.title span{display:block}
.title .o{color:var(--red)}
.ribbon{position:relative;z-index:2;display:inline-block;background:var(--red);color:var(--cream);font:400 clamp(1.6rem,3vw,2.6rem)/1 var(--disp);text-transform:uppercase;
 padding:10px 18px;transform:rotate(-2deg);margin:16px 0 0;box-shadow:6px 6px 0 var(--ind)}
.strap{position:relative;z-index:2;font:700 clamp(1.3rem,2.2vw,1.9rem)/1.1 var(--cond);letter-spacing:.14em;text-transform:uppercase;margin:16px 0 0}
.strap b{color:var(--red)}
.halftone{position:absolute;right:3%;bottom:0;width:min(44%,520px);z-index:1}
.halftone .ph{position:relative;aspect-ratio:1;-webkit-mask:radial-gradient(circle,#000 62%,transparent 63%);mask:radial-gradient(circle,#000 62%,transparent 63%)}
.halftone img{width:100%;height:100%;object-fit:cover;filter:grayscale(1) contrast(1.5) brightness(1.05)}
.halftone .ph::after{content:"";position:absolute;inset:0;background:radial-gradient(circle,var(--ind) 34%,transparent 36%) 0 0/7px 7px;mix-blend-mode:screen;opacity:.9}
.halftone .ph::before{content:"";position:absolute;inset:0;background:var(--ind);mix-blend-mode:lighten;z-index:1}
.side-acts{position:absolute;right:30px;top:30px;z-index:3;display:flex;flex-direction:column;gap:10px;width:220px}
.act{display:flex;justify-content:space-between;align-items:center;background:var(--cream);border:3px solid var(--ind);padding:10px 12px;font:700 15px/1 var(--cond);letter-spacing:.1em;text-transform:uppercase;text-decoration:none;box-shadow:4px 4px 0 var(--ind)}
.act.hot{background:var(--red);color:var(--cream)}
.act:hover,.act:focus-visible{background:var(--ind);color:var(--cream);outline:0}
.week{display:grid;grid-template-columns:repeat(7,1fr);background:var(--cream);border-bottom:4px solid var(--ind)}
.week a{display:block;padding:12px 12px 14px;border-right:2px solid var(--ind);text-decoration:none}
.week a:last-child{border-right:0}
.week a b{display:block;font:400 22px/1 var(--disp);color:var(--red);letter-spacing:.02em}
.week a span{font:700 13px/1.15 var(--cond);letter-spacing:.06em;text-transform:uppercase}
.week a:hover,.week a:focus-visible{background:var(--yel);outline:0}
.spec{background:var(--ind);color:var(--cream);padding:46px 34px;display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:30px;align-items:center;border-bottom:4px solid var(--ind)}
.spec .word{font-family:var(--head);font-weight:900;font-size:clamp(3rem,9vw,8.6rem);line-height:.9;transition:font-size .25s}
.spec .word .r{color:var(--yel)}
.ctl label{display:block;font:700 13px var(--cond);letter-spacing:.14em;text-transform:uppercase;margin:12px 0 4px}
.ctl input{width:100%;accent-color:var(--yel)}
.ctl .v{font:400 28px var(--disp);color:var(--yel)}
.playbill{display:grid;grid-template-columns:repeat(12,1fr);gap:0;border-bottom:4px solid var(--ind);background:var(--cream)}
.bill{position:relative;padding:20px 22px 22px;border-right:3px solid var(--ind);border-bottom:3px solid var(--ind);display:flex;flex-direction:column}
.bill.lead{grid-column:span 6;grid-row:span 2;background:var(--org);color:var(--ink)}
.bill.lead .icon{width:62%}
.bill.mid{grid-column:span 3}
.bill.low{grid-column:span 4}
.bill .k{font:700 13px var(--cond);letter-spacing:.14em;text-transform:uppercase;display:flex;justify-content:space-between}
.bill .icon{display:block;width:72%;margin:4px auto;aspect-ratio:1}
.bill h3{font:400 clamp(1.5rem,2.2vw,2.1rem)/.95 var(--disp);text-transform:uppercase;letter-spacing:.01em;margin:8px 0 6px}
.bill.lead h3{font-size:clamp(2.4rem,4.2vw,4rem)}
.bill h3 a{text-decoration:none}.bill h3 a::after{content:"";position:absolute;inset:0}
.bill h3 a:focus-visible{outline:4px solid var(--red);outline-offset:4px}
.bill .r{display:inline-block;background:var(--red);color:var(--cream);font:400 1.2rem/1 var(--disp);padding:6px 9px;letter-spacing:.03em;text-transform:uppercase;align-self:flex-start;transform:rotate(-1.5deg)}
.bill.lead .r{font-size:2rem;padding:10px 14px;background:var(--ind)}
.bill p.s{font-size:.95rem;margin:10px 0 0}
.bill:hover,.bill:focus-within{background:var(--yel)}
.bill.lead:hover,.bill.lead:focus-within{background:#ff6a26}
.band{background:var(--red);color:var(--cream);padding:34px;display:grid;grid-template-columns:1fr 1.3fr;gap:30px;border-bottom:4px solid var(--ind)}
.band h2,.crewh{font:400 clamp(2.6rem,5vw,4.6rem)/.9 var(--disp);text-transform:uppercase;margin:0}
.band ul{list-style:none;margin:0;padding:0;columns:2;column-gap:24px}
.band li{break-inside:avoid;border-top:2px solid #fff6;padding:8px 0}
.band a{text-decoration:none;font:700 17px/1.2 var(--cond);letter-spacing:.04em;text-transform:uppercase}
.band a b{display:block;color:var(--yel);font-size:13px;letter-spacing:.12em}
.band a:hover span,.band a:focus-visible span{text-decoration:underline}
.crew{background:var(--cream);display:grid;grid-template-columns:1.3fr 1fr;border-bottom:4px solid var(--ind)}
.crew>div{padding:34px}.crew>div+div{border-left:4px solid var(--ind)}
.crew p{margin:0 0 12px}
.exp{list-style:none;margin:0;padding:0}
.exp li{border-top:2px solid var(--ind);padding:9px 0;font-size:.92rem}
.exp b{font:400 1.15rem/1.05 var(--disp);text-transform:uppercase;letter-spacing:.02em;display:block}
.exp i{font:normal 700 12px var(--cond);letter-spacing:.12em;text-transform:uppercase;color:var(--red)}
.foot{background:var(--ind);color:var(--cream);padding:46px 34px;display:flex;flex-wrap:wrap;gap:24px;align-items:center;justify-content:space-between}
.foot h2{font:400 clamp(2.6rem,6vw,5.6rem)/.9 var(--disp);text-transform:uppercase;margin:0;color:var(--yel)}
.foot .act{box-shadow:4px 4px 0 var(--yel)}
@media (max-width:1100px){.sheet{grid-template-columns:70px minmax(0,1fr)}.dates.r{display:none}.side-acts{position:relative;right:auto;top:auto;width:auto;flex-direction:row;flex-wrap:wrap;margin-top:22px}
 .bill.lead{grid-column:span 12;grid-row:auto}.bill.mid{grid-column:span 6}.bill.low{grid-column:span 6}.week{grid-template-columns:repeat(4,1fr)}.week a:nth-child(n+5){display:none}}
@media (max-width:700px){.bar .next{display:none}.bar nav a{padding:0 8px;font-size:13px}.bar .nm{font-size:18px;padding:0 10px}.bar .tix{padding:12px 10px;font-size:14px}
 .sheet{grid-template-columns:1fr}.dates{display:none}.stage{padding:22px 16px;min-height:0}.halftone{position:relative;right:auto;width:80%;margin:20px auto 0}.halo{width:80%}
 .spec{grid-template-columns:1fr;padding:30px 16px}.bill.mid,.bill.low{grid-column:span 12}.band,.crew{grid-template-columns:1fr}.band ul{columns:1}.crew>div+div{border-left:0;border-top:4px solid var(--ind)}
 .crew>div,.band,.foot{padding:26px 16px}.week{grid-template-columns:1fr 1fr}.week a:nth-child(n+3){display:none}}
"""
    years = [('2022', 'First build'), ('2023', 'Research'), ('2024', 'UQ Space'), ('2025', 'Errol'), ('2026', '1st of 17'), ('2027', 'Graduate')]
    left = ''.join(f'<div{" class=hot" if y == "2026" else ""}><b>{y[2:]}</b>{e(t)}</div>' for y, t in years)
    right_items = [('1st', 'of 17'), ('540', 'metres'), ('0', 'DRC'), ('200', 'sim flights'), ('21%', 'lighter'), ('~25', 'led')]
    right = ''.join(f'<div{" class=hot" if i == 0 else ""}><b>{a}</b>{e(b)}</div>' for i, (a, b) in enumerate(right_items))
    week = ''.join(f'<a href="{p["href"]}"><b>{e(p["short"][0])}</b><span>{e(p["result"])}</span></a>' for p in MAIN[:7])
    bills = []
    for i, p in enumerate(P):
        cls = 'lead' if i == 0 else ('mid' if i < 9 else 'low')
        bills.append(f"""<li class="bill {cls} card"><div class="k"><span>{e(p['meta'].split(' · ')[0])}</span><span>{e(YEAR[p['slug']])}</span></div>{p['icon']}
<h3><a href="{p['href']}">{e(p['title'])}</a></h3><span class="r">{e(p['result'])}</span>{'<p class="s">' + e(p['outcome']) + '</p>' if i == 0 else ''}</li>""")
    # 1 lead (6 cols x 2 rows) + 8 mid (3 cols) + 2 low: fill rows with grid; low items span 6 to close the grid
    bills_html = ''.join(bills).replace('class="bill low card"', 'class="bill low card" style="grid-column:span 6"')
    cw = ''.join(f'<li><a href="{c["href"]}"><b>{e(c["meta"])}</b><span>{e(c["title"])}</span></a></li>' for c in D['coursework'])
    exp = ''.join(f'<li><b>{e(r)}</b>{e(o)}<br><i>{e(w)}</i></li>' for r, o, w in D['experience'])
    body = fill("""<header class="bar"><a class="nm" href="#top">I.J. Ziebarth</a><nav aria-label="Main"><a href="#bill">Projects</a><a href="#cw">Coursework</a><a href="#crew">About</a></nav>
<span class="next">Now showing <b>Theseus VI</b></span><a class="tix" href="mailto:@@EMAIL@@">Hire me</a></header>
<main id="main"><section class="sheet" id="top" aria-labelledby="me"><div class="dates" aria-label="Timeline">@@LEFT@@</div>
<div class="stage"><div class="halo" aria-hidden="true"></div>
<h1 class="title" id="me"><span>Isaac</span><span>Johan</span><span class="o">Ziebarth</span></h1>
<p class="ribbon">Flight software · Autonomy · Boards</p>
<p class="strap">Mechatronic engineer, UQ · <b>graduating 2027</b><br>Rover team placed <b>1st of 17</b> · ARC 2026</p>
<figure class="halftone" style="margin:0"><div class="ph"><img src="/assets/img/profile.jpg" alt=""></div></figure>
<div class="side-acts"><a class="act hot" href="mailto:@@EMAIL@@">Email me <span aria-hidden="true">→</span></a><a class="act" href="#bill">See the work <span aria-hidden="true">→</span></a>
<a class="act" href="@@LI@@">LinkedIn <span aria-hidden="true">→</span></a><a class="act" href="@@GH@@">GitHub <span aria-hidden="true">→</span></a></div></div>
<div class="dates r" aria-label="Results">@@RIGHT@@</div></section>
<nav class="week" aria-label="Headline projects">@@WEEK@@</nav>
<section class="spec" aria-label="Type specimen"><div class="word" id="word">Built to <span class="r">fly</span>, <span class="r">drive</span> and <span class="r">find its way</span>.</div>
<div class="ctl"><label for="sz">Scale</label><input id="sz" type="range" min="40" max="140" value="96"><label>Now showing</label><div class="v" id="vv">96 PT</div>
<p style="font-size:.9rem;margin:10px 0 0">Every headline on the site is set from one scale: drag it to see the hierarchy hold.</p></div></section>
<section id="bill" aria-labelledby="bh"><h2 class="vh" id="bh">Projects</h2><ul class="playbill" style="list-style:none;margin:0;padding:0">@@BILLS@@</ul></section>
<section class="band" id="cw" aria-labelledby="cwh"><h2 id="cwh">Coursework<br>repertoire</h2><ul>@@CW@@</ul></section>
<section class="crew" id="crew" aria-labelledby="ch"><div><h2 class="crewh" id="ch" style="color:var(--red);margin-bottom:18px">The engineer</h2>@@BIO@@</div><div><ul class="exp">@@EXP@@</ul><p style="font-size:.9rem;margin-top:14px">@@EDU@@</p></div></section>
<section class="foot" aria-label="Contact"><h2>Book the next build.</h2><div style="display:flex;gap:12px;flex-wrap:wrap"><a class="act hot" href="mailto:@@EMAIL@@">Email me →</a><a class="act" href="@@LI@@">LinkedIn →</a><a class="act" href="@@GH@@">GitHub →</a></div></section>
</main>""", EMAIL=D['email'], LI=D['linkedin'], GH=D['github'], LEFT=left, RIGHT=right, WEEK=week, BILLS=bills_html, CW=cw, BIO=bio(4),
                EXP=exp, EDU=e(D['edu']))
    js = """
const sz=document.getElementById('sz'), w=document.getElementById('word'), vv=document.getElementById('vv');
sz.addEventListener('input',()=>{ w.style.fontSize=(sz.value/16)+'rem'; vv.textContent=sz.value+' PT'; });
"""
    return page('Isaac Johan Ziebarth · Theatre poster', 'family=Anton&family=Barlow+Condensed:wght@700', css, body, js), 'poster'


if __name__ == '__main__':
    for fn in (trailhead, meguri, console, poster):
        html_text, name = fn()
        html_text = html_text.replace('<nav class="proto-switch" aria-label="Prototypes"><b>Prototype</b>',
                                      '<nav class="proto-switch" aria-label="Prototypes"><b>Prototype</b>', 1)
        # mark the current prototype in the switcher
        html_text = html_text.replace(f'<a href="{name}.html">', f'<a href="{name}.html" aria-current="page">', 1)
        out = HERE / f'{name}.html'
        out.write_text(html_text)
        print(out.name, f'{out.stat().st_size / 1024:.0f} KB')
