"""Interaction-led prototype: a calm page with four live pieces driven by real work.

  1. Explore  - a rover runs frontier exploration + A* on an occupancy grid and finds the projects (Theseus V at ARC).
  2. Flight   - scrolling replays the real HAVOC-2 telemetry (altitude, events, the logging gap).
  3. Projects - hovering a project wakes its real live figure in a preview; click opens it full size.
  4. Orrery   - projects orbit; picking one waits for the Hohmann launch window and flies the transfer.

python3 -I build4.py -> live.html + live.js beside this file. Local only.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from content import load, ROOT  # noqa: E402
import html

D = load()
P = D['projects']
e = html.escape
YEAR = {p['slug']: p['meta'].split(' · ')[-1] for p in P}
FOUND = ['theseus', 'havoc2-cosmos', 'osiris', 'airbrakes', 'digital-orrery', 'weather-station', 'errol', 'metr4810', 'camera-mount', 'engg1100']   # every project card has a marker


def flight():
    s = (ROOT / 'assets/figures/havoc2-flight.html').read_text()
    i = s.find('const D =') + len('const D =')
    d, _ = json.JSONDecoder().raw_decode(s[i:].lstrip())
    return {'asc': [[t, round(a, 1)] for t, a in d['asc']], 'dsc': [[t, round(a, 1)] for t, a in d['dsc']],
            'ev': d['events']}


CSS = """
:root{--paper:#ECEAE4;--paper2:#E1DED5;--panel:#F5F4F0;--ink:#1E2126;--mute:#5D626B;--ind:#2E1499;--red:#BB0700;--yel:#FFC908;--org:#FF5102;--leaf:#3E9B5F;--line:#1E212624;
 --head:'Barlow Condensed',Arial Narrow,sans-serif;--body:Sanchez,Georgia,serif;--mono:'Chivo Mono',ui-monospace,monospace;
 --stripe:linear-gradient(90deg,var(--yel) 0 20%,var(--org) 20% 40%,var(--red) 40% 60%,var(--ind) 60% 80%,var(--leaf) 80%)}
.stripe{display:block;height:6px;background:var(--stripe)}
.code{display:inline-flex;align-items:center;gap:10px;font:600 13px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink);margin:0 0 14px}
.code i{width:28px;height:12px;background:var(--c,var(--ind));display:inline-block}
.code em{font-style:normal;color:var(--mute)}
*{box-sizing:border-box} html{scroll-padding-top:64px} body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 var(--body)}
a{color:inherit} img{max-width:100%;display:block}
.vh{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.mono{font:500 12px/1.4 var(--mono);letter-spacing:.04em}
header.top{position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:24px;padding:0 28px;height:56px;background:color-mix(in srgb,var(--panel) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
header.top::after{content:"";position:absolute;left:0;right:0;bottom:-6px;height:6px;background:var(--stripe)}
header.top .nm{font:700 1.25rem var(--head);letter-spacing:.06em;text-transform:uppercase;text-decoration:none;display:flex;align-items:center;gap:10px}
header.top .nm i{width:30px;height:30px;border:2px solid var(--ink);display:grid;place-items:center;font:normal 600 11px var(--mono);letter-spacing:0}
header.top nav{margin-left:auto;display:flex;gap:4px}
header.top nav a{font:500 13px var(--mono);text-decoration:none;padding:8px 10px;border-radius:6px;color:var(--mute)}
header.top nav a:hover,header.top nav a:focus-visible,header.top nav a.on{color:var(--ink);background:var(--paper2);outline:0}
.btn{display:inline-flex;align-items:center;gap:8px;font:700 15px var(--head);letter-spacing:.12em;text-transform:uppercase;padding:11px 18px;border-radius:2px;border:2px solid var(--ink);background:none;color:var(--ink);cursor:pointer;text-decoration:none;transition:background .2s,color .2s}
.btn:focus-visible{background:var(--ink);color:var(--paper);outline:0}@media (hover:hover){.btn:hover{background:var(--ink);color:var(--paper)}}
.btn.solid{background:var(--ind);border-color:var(--ind);color:#fff}.btn.solid:focus-visible{background:#220E73;border-color:#220E73}@media (hover:hover){.btn.solid:hover{background:#220E73;border-color:#220E73}}
section{position:relative}
.wrap{max-width:1240px;margin:0 auto;padding:0 28px}
.eyebrow{font:600 13px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--mute);margin:0 0 12px;display:flex;align-items:center;gap:10px}
.eyebrow::before{content:"";width:28px;height:12px;background:var(--c,var(--ind))}
h2{font:700 clamp(2.6rem,5vw,4.4rem)/.95 var(--head);margin:0 0 14px;letter-spacing:.01em;text-transform:uppercase}
.intro{max-width:56ch;color:var(--mute);margin:0}

/* 1 explore */
#explore{height:min(88vh,860px);min-height:560px;border-bottom:1px solid var(--line);overflow:hidden}
#arena{position:absolute;inset:0;width:100%;height:100%;display:block;cursor:crosshair;touch-action:manipulation}
.hero-copy{position:absolute;left:28px;top:34px;max-width:520px;z-index:3;pointer-events:none}
.hero-copy>*{pointer-events:auto}
.hero-copy{background:color-mix(in srgb,var(--panel) 90%,transparent);border:2px solid var(--ink);padding:22px 24px 24px;box-shadow:6px 6px 0 var(--ink)}
.hero-copy::before{content:"";display:block;height:6px;background:var(--stripe);margin:-22px -24px 18px}
.hero-copy h1{font:700 clamp(3rem,6vw,5.6rem)/.88 var(--head);margin:0 0 14px;letter-spacing:.01em;text-transform:uppercase}
.hero-copy h1 span{color:var(--ind);display:block}
.hero-copy p{margin:0 0 18px;max-width:42ch;font-size:1.05rem}
.hero-copy .acts{display:flex;flex-wrap:wrap;gap:10px}
.status{position:absolute;left:28px;bottom:22px;z-index:3;display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.status .mono b{color:var(--red);font-weight:600}
.status .bar{width:140px;height:4px;background:var(--line);border-radius:2px;overflow:hidden}
.status .bar i{display:block;height:100%;width:0;background:var(--ind);transition:width .4s}
.placard{position:absolute;z-index:4;transform:translate(-50%,calc(-100% - 14px)) scale(.6);opacity:0;transition:opacity .35s,transform .45s cubic-bezier(.2,1.4,.4,1);
 background:var(--panel);border:2px solid var(--ink);border-radius:2px;padding:8px 12px 9px;cursor:pointer;text-align:left;font:inherit;color:var(--ink);box-shadow:0 6px 18px #1d173622;max-width:220px}
.placard.on{opacity:1;transform:translate(-50%,calc(-100% - 14px)) scale(1)}
.placard::before{content:"";position:absolute;left:0;right:0;top:0;height:4px;background:var(--stripe)}
.placard::after{content:"";position:absolute;left:50%;bottom:-8px;width:12px;height:12px;background:var(--panel);border-right:2px solid var(--ink);border-bottom:2px solid var(--ink);transform:translateX(-50%) rotate(45deg)}
.placard b{display:block;font:700 17px/1.05 var(--head);text-transform:uppercase;letter-spacing:.03em;margin-top:3px}
.placard span{display:block;font:500 11px var(--mono);color:var(--red);margin-top:3px}
.placard:hover,.placard:focus-visible{background:var(--yel);outline:0}.placard:hover::after,.placard:focus-visible::after{background:var(--yel)}
.legend{position:absolute;right:24px;bottom:22px;z-index:3;display:flex;gap:14px;flex-wrap:wrap}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend i{width:10px;height:10px;display:inline-block;border-radius:2px}

/* 2 flight */
#flight{border-bottom:1px solid var(--line)}
.fl{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:40px}
.fl-steps{padding:90px 0 40vh}
.fl-steps .head{margin-bottom:30vh}
.step{min-height:62vh;display:flex;flex-direction:column;justify-content:center;opacity:.32;transition:opacity .4s}
.step.on{opacity:1}
.step h3{font:700 2.2rem/1 var(--head);text-transform:uppercase;margin:0 0 10px}
.step p{margin:0;max-width:40ch}
.step .mono{color:var(--red);margin-bottom:8px}
.fl-chart{position:sticky;top:76px;height:calc(100vh - 100px);display:flex;flex-direction:column;justify-content:center}
.readout{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border:2px solid var(--ink);border-radius:2px;overflow:hidden;margin-bottom:14px;background:#15171B;color:#FFB22E}
.readout span{color:#9aa0a8!important}
.readout div{padding:12px 16px;border-right:1px solid var(--line)}.readout div:last-child{border-right:0}
.readout b{display:block;font:600 30px/1.1 var(--mono);font-variant-numeric:tabular-nums}
.readout span{font:500 11px var(--mono);color:var(--mute);text-transform:uppercase;letter-spacing:.08em}
#alt{width:100%;height:auto;border:2px solid var(--ink);border-radius:2px;background:var(--panel)}

/* 3 projects */
#projects{padding:100px 0;border-bottom:1px solid var(--line)}
.pj{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:36px;margin-top:40px;align-items:start}
.plist{list-style:none;margin:0;padding:0;border-top:1px solid var(--ink)}
.prow{position:relative;display:grid;grid-template-columns:64px minmax(0,1fr) auto;gap:16px;align-items:center;padding:10px 6px;border-bottom:1px solid var(--line);cursor:pointer;transition:background .2s,padding .25s}
.prow .card{display:block}.prow .icon{display:block;width:64px;height:64px}
.prow h3{font:700 1.3rem/1.05 var(--head);text-transform:uppercase;letter-spacing:.02em;margin:0}
.prow h3 button{all:unset;cursor:pointer}.prow h3 button::after{content:"";position:absolute;inset:0}
.prow h3 button:focus-visible{outline:3px solid var(--red);outline-offset:3px}
.prow p{margin:2px 0 0;font:500 12px var(--mono);color:var(--mute)}
.prow .r{font:500 12px var(--mono);color:var(--red);text-align:right;max-width:150px}
.prow.on{background:var(--panel);padding-left:14px;box-shadow:inset 6px 0 0 var(--yel)}
.prow.on h3{color:var(--ind)}
.preview{position:sticky;top:80px}
.pv{position:relative;aspect-ratio:16/11;border:2px solid var(--ink);border-radius:2px;overflow:hidden;background:#fff;box-shadow:6px 6px 0 var(--ink)}
.pv::before{content:"";position:absolute;left:0;right:0;top:0;height:6px;background:var(--stripe);z-index:3}
.pv iframe,.pv img,.pv .ph{position:absolute;inset:0;width:100%;height:100%;border:0;object-fit:contain;opacity:0;transition:opacity .45s;background:#fff}
.pv .on{opacity:1}
.pv .ph{display:grid;place-items:center;font:500 13px var(--mono);color:var(--mute);opacity:1}
.pv-cap{display:flex;justify-content:space-between;gap:16px;margin-top:12px;align-items:flex-start}
.pv-cap b{font:700 1.6rem/1.05 var(--head);text-transform:uppercase;display:block}
.pv-cap p{margin:4px 0 0;font-size:.95rem;color:var(--mute);max-width:52ch}
.pv-cap .btn{flex:none}

/* 4 orrery */
#orrery{padding:100px 0;border-bottom:1px solid var(--line);background:#14161A;color:var(--paper)}
#orrery .intro{color:#C9C3DD}
#orrery h2{color:var(--paper)}
.orb{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,.6fr);gap:30px;margin-top:36px;align-items:center}
#sky{width:100%;aspect-ratio:1.25;display:block;cursor:pointer;border-radius:2px;border:2px solid #3a3f47;background:radial-gradient(circle at 50% 50%,#22263a,#101216 72%)}
.olist{list-style:none;margin:0;padding:0}
.olist button{all:unset;box-sizing:border-box;width:100%;display:flex;justify-content:space-between;gap:10px;padding:8px 10px;border-radius:8px;cursor:pointer;font:500 13px var(--mono);color:#E6E1F5}
.olist button:hover,.olist button:focus-visible,.olist button.on{background:#ffffff14;color:#fff;outline:0}
.olist button i{font-style:normal;color:var(--yel)}
.mission{font:500 13px/1.5 var(--mono);color:var(--yel);min-height:3em;margin:14px 0 0}

/* about + contact */
#about{padding:100px 0;border-bottom:1px solid var(--line)}
.ab{display:grid;grid-template-columns:240px minmax(0,1fr) minmax(0,.8fr);gap:40px;margin-top:30px}
.ab img{border-radius:2px;border:2px solid var(--ink);aspect-ratio:1;object-fit:cover;width:100%;height:auto;filter:grayscale(1);transition:filter .5s}
.ab img:hover{filter:none}
.ab p{margin:0 0 14px}
.exp{list-style:none;margin:0;padding:0;border-top:1px solid var(--ink)}
.exp li{padding:9px 0;border-bottom:1px solid var(--line);font-size:.92rem}
.exp b{display:block;font:700 1.1rem var(--head);text-transform:uppercase;letter-spacing:.02em}.exp i{font:normal 500 11px var(--mono);color:var(--mute)}
.cw{columns:2;column-gap:30px;list-style:none;padding:0;margin:14px 0 0}
.cw a{display:block;padding:5px 0;text-decoration:none;font-size:.95rem;break-inside:avoid}
.cw a b{font:500 11px var(--mono);color:var(--red);display:block}
.cw a:hover span{text-decoration:underline}
#contact{padding:110px 0 140px;text-align:center}
#contact h2{font-size:clamp(2.6rem,6vw,5rem)}
#contact .acts{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-top:22px}

dialog.full{width:min(1200px,calc(100vw - 24px));height:min(820px,calc(100vh - 24px));padding:0;border:2px solid var(--ink);border-radius:2px;background:var(--panel);color:var(--ink);overflow:hidden}
dialog.full::backdrop{background:#1d1736aa;backdrop-filter:blur(3px)}
.full .g{display:grid;grid-template-columns:minmax(260px,360px) 1fr;height:100%}
.full .side{padding:26px;overflow:auto;border-right:1px solid var(--line)}
.full h3{font:700 2.2rem/1 var(--head);text-transform:uppercase;margin:6px 0 8px}
.full .r{font:500 13px var(--mono);color:var(--red)}
.full dl{font-size:.9rem;margin:14px 0}.full dl div{border-top:1px solid var(--line);padding:6px 0}
.full dt{font:500 11px var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--mute)}.full dd{margin:0}
.full .live{position:relative;background:#fff}
.full .live iframe,.full .live img{position:absolute;inset:0;width:100%;height:100%;border:0;object-fit:contain}
.full .acts{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.full .x{position:absolute;right:12px;top:12px;z-index:2}

.proto-switch{position:fixed;right:12px;bottom:12px;z-index:99;display:flex;gap:4px;align-items:center;background:#111;color:#fff;font:600 12px/1 system-ui,sans-serif;padding:6px;border-radius:8px;box-shadow:0 4px 16px #0005}
.proto-switch a{color:#fff;text-decoration:none;padding:6px 8px;border-radius:5px}.proto-switch a[aria-current]{background:#FFC908;color:#111}

@media (max-width:900px){header.top{padding:0 14px;gap:10px}header.top nav a{padding:8px 5px;font-size:11px}.wrap{padding:0 16px}
 .hero-copy{left:16px;right:16px;top:20px}.hero-copy h1{font-size:2.6rem}.hero-copy p{font-size:.95rem;background:color-mix(in srgb,var(--paper) 85%,transparent)}.legend{display:none}.status{left:16px;bottom:14px}
 .fl{grid-template-columns:1fr}.fl-chart{top:60px;height:auto;padding:12px 0;background:var(--paper);z-index:2}.fl-steps{padding-top:20px}.step{min-height:48vh}.readout b{font-size:20px}
 .pj,.orb,.ab{grid-template-columns:1fr}.preview{position:static;order:-1}.prow .r{display:none}.full .g{grid-template-columns:1fr;grid-template-rows:auto 1fr}.full .side{border-right:0;border-bottom:1px solid var(--line);max-height:45vh}.cw{columns:1}}
@media (max-width:600px){header.top .nm{font-size:.95rem}header.top nav a:nth-child(n+5){display:none}}
"""


def page():
    proj = [{k: p[k] for k in ('slug', 'href', 'title', 'meta', 'summary', 'outcome', 'facts', 'figure', 'image', 'result')} for p in P]
    rows = ''.join(f"""<li class="prow" data-slug="{p['slug']}"><span class="card">{p['icon']}</span><div><h3><button type="button" data-open="{p['slug']}">{e(p['title'])}</button></h3>
<p>{e(p['meta'])}</p></div><span class="r">{e(p['result'])}</span></li>""" for p in P)
    olist = ''.join(f'<li><button type="button" data-fly="{p["slug"]}">{e(p["title"])}<i>{e(YEAR[p["slug"]][-4:])}</i></button></li>' for p in P)
    exp = ''.join(f'<li><b>{e(r)}</b>{e(o)}<br><i>{e(w)}</i></li>' for r, o, w in D['experience'])
    cw = ''.join(f'<li><a href="{c["href"]}"><b>{e(c["meta"])}</b><span>{e(c["title"])}</span></a></li>' for c in D['coursework'])
    bio = ''.join(f'<p>{e(x)}</p>' for x in D['about'][:3])
    data = json.dumps({'projects': proj, 'found': FOUND, 'flight': flight()}).replace('</', '<\\/')
    links = [('merged', 'Merged'), ('live', 'Live'), ('trailhead', 'Trailhead'), ('meguri', 'Meguri'), ('console', 'Console'), ('poster', 'Poster')]
    switch = '<nav class="proto-switch" aria-label="Prototypes">' + ''.join(
        f'<a href="{k}.html"{" aria-current=page" if k == "live" else ""}>{n}</a>' for k, n in links) + '</nav>'
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Isaac Johan Ziebarth · Live</title>
<link rel="stylesheet" href="/assets/css/iso-kit.css"><link rel="stylesheet" href="icons.css">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Chivo+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>@font-face{{font-family:Fraunces;src:url(/assets/fonts/fraunces-900-latin.woff2) format("woff2");font-weight:900;font-display:swap}}
@font-face{{font-family:Sanchez;src:url(/assets/fonts/sanchez-400-latin.woff2) format("woff2");font-weight:400;font-display:swap}}
.card .icon svg{{width:100%;height:100%;display:block}}{CSS}</style></head><body>
<a class="vh" href="#main">Skip to content</a>
<header class="top"><a class="nm" href="#explore"><i>IJZ</i>Isaac Johan Ziebarth</a><nav aria-label="Main"><a href="#explore">Explore</a><a href="#flight">Flight</a><a href="#projects">Projects</a><a href="#orrery">Orrery</a><a href="#about">About</a><a href="#contact">Contact</a></nav></header>
<main id="main">
<section id="explore" aria-labelledby="me"><canvas id="arena" aria-label="A rover exploring an unknown arena with frontier exploration and A* path planning. Click to send it somewhere."></canvas>
<div class="hero-copy"><p class="eyebrow" style="--c:var(--leaf)">01 · Explore</p><h1 id="me">Isaac Johan <span>Ziebarth</span></h1>
<p>I write software that flies, drives and finds its way. This rover is running frontier exploration, the way Theseus V did at the 2026 Australian Rover Challenge, where we placed 1st of 17. It's looking for my projects.</p>
<div class="acts"><button class="btn solid" type="button" id="showall">Show all projects</button><a class="btn" href="mailto:{D['email']}">Email me</a></div></div>
<div class="status"><span class="mono" id="st">booting · 0/{len(FOUND)} found</span><span class="bar" aria-hidden="true"><i id="stbar"></i></span><span class="mono">click anywhere to set a goal</span></div>
<div class="legend mono" aria-hidden="true"><span><i style="background:#1D1736"></i>obstacle</span><span><i style="background:#FF5102"></i>frontier</span><span><i style="background:#BB0700;height:3px"></i>A* path</span><span><i style="background:#2E149922"></i>unexplored</span></div>
<div id="placards"></div></section>

<section id="flight" aria-labelledby="fh"><div class="wrap fl"><div class="fl-steps">
<div class="head"><p class="eyebrow" style="--c:var(--org)">02 · Scroll to fly</p><h2 id="fh">HAVOC-2, first flight</h2><p class="intro">The C++ flight firmware I wrote for UQ Space's flight computer, flown on 12 July 2026. Scroll and the real log replays, frame by frame.</p></div>
<div class="step" data-t="0"><p class="mono">T+0.0 s · liftoff</p><h3>Off the pad</h3><p>The firmware switches from pad idle to boost on the accelerometer, then logs every frame with a checksum.</p></div>
<div class="step" data-t="1.32"><p class="mono">T+1.3 s · burnout</p><h3>Burnout at 11.65 g</h3><p>The motor burns for 1.3 seconds and peaks at 11.65 g. From here the rocket coasts.</p></div>
<div class="step" data-t="9.68"><p class="mono">T+9.7 s · apogee</p><h3>Apogee, about 540 m</h3><p>The barometer and the state machine agree on apogee, and the recovery event fires.</p></div>
<div class="step" data-t="11.38"><p class="mono">T+11.4 s · brownout</p><h3>Nine seconds missing</h3><p>The ejection shock browned out the logger. The gap stays honest on the plot: dashed, not invented.</p></div>
<div class="step" data-t="46.28"><p class="mono">T+46.3 s · landed</p><h3>Every frame passed</h3><p>Under the parachute to the ground. Every logged frame passed its checksum, and COSMOS, the ground station I built, read it back.</p>
<p style="margin-top:14px"><a class="btn" href="/projects/havoc2-cosmos.html">Read the write-up</a></p></div></div>
<div class="fl-chart"><div class="readout"><div><b id="ro-t">T+0.0</b><span>seconds</span></div><div><b id="ro-a">0</b><span>metres altitude</span></div><div><b id="ro-p">PAD</b><span>flight state</span></div></div>
<canvas id="alt" width="1200" height="760" aria-label="HAVOC-2 altitude against time, drawn as you scroll"></canvas></div></div></section>

<section id="projects" aria-labelledby="ph"><div class="wrap"><p class="eyebrow" style="--c:var(--yel)">03 · Hover to wake</p><h2 id="ph">Projects</h2><p class="intro">Point at a project and its real figure starts up beside it: the arena map, the flight replay, the KiCad board, the transfer planner. Click to open it full size.</p>
<div class="pj"><ul class="plist">{rows}</ul>
<div class="preview" aria-live="polite"><div class="pv" id="pv"><div class="ph">Point at a project</div></div><div class="pv-cap"><div><b id="pv-t"></b><p id="pv-s"></p></div><button class="btn" type="button" id="pv-open" hidden>Open</button></div></div></div></div></section>

<section id="orrery" aria-labelledby="oh"><div class="wrap"><p class="eyebrow" style="--c:var(--ind);color:#9aa0a8">04 · Plan a transfer</p><h2 id="oh">Every project is a body in orbit</h2>
<p class="intro">Built on the orbital mechanics from my digital orrery. Pick a project and the craft waits for the Hohmann launch window, burns, and coasts across on the transfer ellipse. When it arrives, the project opens.</p>
<div class="orb"><canvas id="sky" width="1200" height="960" aria-label="Projects orbiting as planets; pick one to fly a Hohmann transfer to it"></canvas>
<div><ul class="olist">{olist}</ul><p class="mission" id="mission" aria-live="polite">Pick a destination.</p></div></div></div></section>

<section id="about" aria-labelledby="ah"><div class="wrap"><p class="eyebrow" style="--c:var(--red)">05 · About</p><h2 id="ah">The engineer</h2>
<div class="ab"><img src="/assets/img/profile.jpg" alt="Isaac Johan Ziebarth" width="800" height="800"><div>{bio}</div>
<div><ul class="exp">{exp}</ul><p class="eyebrow" style="margin-top:26px;--c:var(--yel)">Coursework</p><ul class="cw">{cw}</ul></div></div></div></section>

<section id="contact" aria-labelledby="ch"><div class="wrap"><p class="eyebrow" style="--c:var(--leaf);justify-content:center">06 · Graduating 2027 · avionics, autonomy, GNC</p><h2 id="ch">Let's build the next one.</h2>
<div class="acts"><a class="btn solid" href="mailto:{D['email']}">Email me</a><a class="btn" href="{D['linkedin']}">LinkedIn</a><a class="btn" href="{D['github']}">GitHub</a></div></div></section>
</main>
<dialog class="full" aria-labelledby="f-t"><button class="btn x" type="button" id="f-x">Close</button><div class="g"><div class="side"><p class="mono" id="f-m"></p><h3 id="f-t"></h3><p class="r" id="f-r"></p><p id="f-o"></p><div id="f-f"></div>
<div class="acts"><a class="btn solid" id="f-h" href="#">Read the write-up</a></div></div><div class="live" id="f-l"></div></div></dialog>
{switch}
<script type="application/json" id="data">{data}</script>
<script src="live.js?v={int((HERE / 'live.js').stat().st_mtime)}"></script><script src="/assets/js/site.js"></script></body></html>"""


if __name__ == '__main__':
    (HERE / 'live.html').write_text(page())
    print('live.html', f"{(HERE / 'live.html').stat().st_size / 1024:.0f} KB")
