"""Live v2: Live (NASA-punk, greenhouse, colour stripe) + parts of Merged + parts of the current site.

New: ArUco markers and cubes with detection boxes and a log (no popups), gauges that wake on cubes, icon cards with
hover motion + live preview, an airbrakes controller panel, OSIRIS power/data pulses on the real board render,
a coursework terminal and the red experience band.
python3 -I build5.py -> live2.html + live2.js. Local only.
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build4 as B4  # noqa: E402
from build2 import gauge  # noqa: E402
from content import ROOT  # noqa: E402

D, P, e, YEAR = B4.D, B4.P, html.escape, B4.YEAR
FOUND = ['theseus', 'havoc2-cosmos', 'osiris', 'airbrakes', 'digital-orrery', 'weather-station', 'errol', 'metr4810']
CUBES = [
    {'key': 'rank', 'name': 'Green', 'col': '#3E9B5F', 'label': '1st of 17', 'sub': 'Theseus V, ARC 2026'},
    {'key': 'apogee', 'name': 'Blue', 'col': '#2E1499', 'label': 'About 540 m', 'sub': 'HAVOC-2 first flight'},
    {'key': 'drc', 'name': 'Red', 'col': '#BB0700', 'label': '0 ERC errors', 'sub': 'OSIRIS V0 schematic'},
    {'key': 'sims', 'name': 'Orange', 'col': '#FF5102', 'label': '200 simulated flights', 'sub': 'Airbrake controllers'},
    {'key': 'rows', 'name': 'Yellow', 'col': '#FFC908', 'label': '98,218 rows passed', 'sub': 'Launch-site weather station'},
    {'key': 'lighter', 'name': 'White', 'col': '#F5F4F0', 'label': '21% lighter', 'sub': 'Titanium crank arm'},
]


def board_parts():
    s = (ROOT / 'projects/osiris.html').read_text()
    out = []
    for m in re.finditer(r'<button type="button" class="bm-mark( bm-under)?" data-part="(\d)" style="left:([\d.]+)%;top:([\d.]+)%" aria-label="\d\. ([^:]+): ([^"]+)">', s):
        out.append({'n': int(m.group(2)), 'x': float(m.group(3)), 'y': round(float(m.group(4)) * 1.043, 2), 'name': html.unescape(m.group(5)),
                    'detail': html.unescape(m.group(6)), 'under': bool(m.group(1))})
    return out


EXTRA_CSS = """
.top-bulletin{display:flex;align-items:center;gap:14px;background:var(--ink);color:#d9dce1;font:600 12px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;padding:8px 28px;overflow:hidden;white-space:nowrap}
.top-bulletin b{color:var(--leaf);display:inline-flex;align-items:center;gap:7px}
.top-bulletin b::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--leaf);box-shadow:0 0 8px var(--leaf);animation:blink 1.4s steps(2) infinite}
@keyframes blink{50%{opacity:.2}}
.hero-copy h1{font:900 clamp(2.8rem,5.4vw,5rem)/.92 Fraunces,Georgia,serif!important;text-transform:none!important;letter-spacing:-.02em!important}
h2{font-family:Fraunces,Georgia,serif!important;font-weight:900!important;text-transform:none!important;letter-spacing:-.015em!important}
.dlog{position:absolute;right:22px;top:22px;bottom:70px;width:300px;z-index:3;display:flex;flex-direction:column;background:color-mix(in srgb,var(--panel) 92%,transparent);border:2px solid var(--ink);box-shadow:6px 6px 0 var(--ink)}
.dlog::before{content:"";display:block;height:6px;background:var(--stripe)}
.dlog .hd{display:flex;justify-content:space-between;align-items:center;padding:9px 12px;border-bottom:1px solid var(--line);font:600 12px var(--mono);letter-spacing:.08em;text-transform:uppercase}
.dlog .hd b{color:var(--red)}
.dlog ol{list-style:none;margin:0;padding:6px;overflow:auto;flex:1}
.dlog li{animation:slidein .45s cubic-bezier(.2,1,.3,1)}
@keyframes slidein{from{opacity:0;transform:translateX(18px)}}
.dlog button{all:unset;box-sizing:border-box;width:100%;display:grid;grid-template-columns:22px 1fr auto;gap:10px;align-items:center;padding:8px 6px;border-bottom:1px dashed var(--line);cursor:pointer;font:500 12px/1.35 var(--mono)}
.dlog button b{font-weight:600}.dlog button em{display:block;font-style:normal;color:var(--red)}
.dlog button i{font-style:normal;color:var(--leaf);font-weight:600}
.dlog button:hover,.dlog button:focus-visible{background:var(--yel);outline:0}
.dlog .empty{font:500 12px/1.5 var(--mono);color:var(--mute);padding:10px 8px}
.glyph{width:20px;height:20px;border:1.5px solid var(--ink);display:block}
.glyph.aruco{display:grid;grid-template-columns:repeat(4,1fr);padding:2px;background:#111;border-color:#111}
.glyph.aruco i{display:block}
.tip{position:absolute;z-index:6;transform:translate(14px,-50%);background:var(--ink);color:#fff;padding:7px 10px;font:500 12px/1.35 var(--mono);pointer-events:none;max-width:240px}
.tip b{display:block;font:700 15px/1.1 var(--head);text-transform:uppercase;letter-spacing:.03em}
.tip span{color:var(--yel)}
#instruments{padding:70px 0 40px;border-bottom:1px solid var(--line)}
.inst{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:24px;margin-top:22px;align-items:stretch}
.six{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;padding:22px;background:linear-gradient(180deg,#F1EFEA,#DCD8CE);border:2px solid var(--ink);position:relative}
.six::before{content:"";position:absolute;left:0;right:0;top:0;height:6px;background:var(--stripe)}
.gauge{margin:0;text-align:center;transition:opacity .5s,filter .5s}
.gauge.dim{opacity:.45;filter:grayscale(1)}
.gauge svg{width:100%;max-width:150px}
.gauge .bez{fill:#1b1a17;stroke:#5c564a;stroke-width:2}.gauge .face{fill:#121110}.gauge .tk line{stroke:#e9e3d6;stroke-width:1.2}
.gauge .gl{fill:#b9ad92;font:600 7px var(--head);letter-spacing:.14em;text-anchor:middle;text-transform:uppercase}
.gauge .gv{fill:#FFB22E;font:600 13px var(--mono);text-anchor:middle}
.gauge .gu{fill:#b9ad92;font:600 5.5px var(--head);letter-spacing:.12em;text-anchor:middle}
.gauge .needle{transform-origin:50px 50px;transform:rotate(calc(var(--a) + 90deg));transition:transform 1.6s cubic-bezier(.3,1.4,.5,1)}
.gauge .needle path{stroke:var(--leaf);stroke-width:2.4;stroke-linecap:round}.gauge .needle circle{fill:#d9d2c0}
.gauge.zero .needle{transform:rotate(-135deg)}
.gauge figcaption{font:600 12px/1.3 var(--head);letter-spacing:.12em;text-transform:uppercase;margin-top:6px}
.ginfo{display:flex;justify-content:space-between;align-items:center;gap:14px;margin-top:12px;flex-wrap:wrap}
.status-panel{border:2px solid var(--ink);background:var(--panel);display:flex;flex-direction:column}
.status-panel .sp{padding:12px 16px;border-bottom:1px solid var(--line)}
.status-panel .sp:last-child{border-bottom:0}
.status-panel .k{font:600 11px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--mute);display:flex;justify-content:space-between}
.status-panel b{display:block;font:700 1.25rem/1.1 var(--head);text-transform:uppercase;margin:4px 0 2px}
.status-panel p{margin:0;font-size:.92rem}
.lampx{display:inline-flex;align-items:center;gap:6px;color:var(--leaf)}.lampx::before{content:"";width:9px;height:9px;border-radius:50%;background:var(--leaf);box-shadow:0 0 8px var(--leaf)}
.pj2{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:28px;margin-top:36px;align-items:start}
.pgrid{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.pcard{position:relative;background:#FFF7DA;border:2px solid var(--ink);display:flex;flex-direction:column;padding:12px 14px 14px;transition:transform .2s,box-shadow .2s}
.pcard:hover,.pcard:focus-within,.pcard.on{transform:translate(-3px,-3px);box-shadow:6px 6px 0 var(--ink)}
.pcard.on{box-shadow:6px 6px 0 var(--ind)}
.pcard .icon{display:block;width:100%;aspect-ratio:1;margin:0 auto 6px}
.pcard h3{font:900 1.06rem/1.15 Fraunces,Georgia,serif;margin:0 0 4px}
.pcard h3 button{all:unset;cursor:pointer}.pcard h3 button::after{content:"";position:absolute;inset:0}
.pcard h3 button:focus-visible{outline:3px solid var(--red);outline-offset:4px}
.pcard .m{font:500 11px var(--mono);color:var(--mute);margin:0}
.pcard .r{font:600 12px var(--mono);color:var(--red);margin:8px 0 0}
.pcard .pill{margin-top:auto;align-self:flex-start;font:700 12px var(--head);letter-spacing:.12em;text-transform:uppercase;background:var(--red);color:#fff;padding:6px 10px;margin-top:10px;transition:transform .2s}
.pcard:hover .pill{transform:translateY(-2px)}
.preview2{position:sticky;top:80px}
.systems{padding:100px 0;border-bottom:1px solid var(--line)}
.sys{display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:30px}
.panel2{border:2px solid var(--ink);background:var(--panel);position:relative;box-shadow:6px 6px 0 var(--ink)}
.panel2::before{content:"";display:block;height:6px;background:var(--stripe)}
.panel2 .ph2{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:14px 18px 6px}
.panel2 h3{font:900 1.5rem/1.1 Fraunces,Georgia,serif;margin:0}
.panel2 .note{font:500 12px/1.5 var(--mono);color:var(--mute);padding:0 18px 14px;margin:0}
#ab{width:100%;height:auto;display:block;border-top:1px solid var(--line);border-bottom:1px solid var(--line);touch-action:none}
.abro{display:grid;grid-template-columns:repeat(3,1fr)}
.abro div{padding:10px 16px;border-right:1px solid var(--line)}.abro div:last-child{border-right:0}
.abro b{display:block;font:600 22px var(--mono)}.abro span{font:500 11px var(--mono);color:var(--mute);text-transform:uppercase;letter-spacing:.08em}
.abctl{display:flex;gap:12px;align-items:center;padding:10px 18px;border-top:1px solid var(--line);font:500 12px var(--mono)}
.abctl input{flex:1;accent-color:var(--org)}
#pcb{position:relative;border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:#fff}
#pcb img{width:100%;height:auto;display:block}
#pcb-svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
.trace{fill:none;stroke:var(--c);stroke-width:.7;stroke-linejoin:round;opacity:.75;stroke-dasharray:1.2 1.2;transition:opacity .3s,stroke-width .3s}
.trace.power{stroke-width:1}
#pcb.focus .trace{opacity:.15}#pcb.focus .trace.lit{opacity:1;stroke-width:1.3}
.pulse{filter:drop-shadow(0 0 1px #000)}
.pm{position:absolute;transform:translate(-50%,-50%);width:28px;height:28px;border-radius:50%;border:2px solid var(--ink);background:var(--yel);font:700 13px var(--mono);cursor:pointer;z-index:2;color:var(--ink)}
.pm.under{background:#fff;border-style:dashed}
.pm:hover,.pm:focus-visible{background:var(--ink);color:var(--yel);outline:0}
.pcb-cap{padding:10px 18px;font-size:.92rem;min-height:3.2em;margin:0}
.pcb-leg{display:flex;gap:14px;flex-wrap:wrap;padding:0 18px 14px;font:500 12px var(--mono)}
.pcb-leg span{display:inline-flex;align-items:center;gap:6px}.pcb-leg i{width:16px;height:4px;display:inline-block}
.redband{background:var(--red);color:#FFF6DE;padding:80px 0}
.redband h2{color:#FFF6DE}
.redband .eyebrow{color:#ffd9cf}.redband .eyebrow::before{background:var(--yel)}
.xp{list-style:none;margin:28px 0 0;padding:0;display:grid;grid-template-columns:repeat(2,1fr);gap:0 40px}
.xp li{display:flex;justify-content:space-between;gap:20px;padding:12px 0;border-top:1px solid #ffffff44}
.xp b{display:block;font:900 1.1rem Fraunces,Georgia,serif}.xp span{font-size:.92rem}.xp i{font:normal 500 12px var(--mono);white-space:nowrap;color:var(--yel)}
.redband .edu{margin-top:22px;font-size:.95rem}
.term{background:#15171B;border:2px solid var(--ink);color:#FFB22E;font:500 15px/1.6 var(--mono);padding:20px 24px;box-shadow:6px 6px 0 var(--ink);margin-top:26px}
.term .hd{color:var(--leaf);margin:0 0 10px}
.term ul{list-style:none;margin:0;padding:0;columns:2;column-gap:40px}
.term a{display:grid;grid-template-columns:100px 1fr;text-decoration:none;padding:2px 4px;break-inside:avoid}
.term a:hover,.term a:focus-visible{background:#FFB22E;color:#15171B;outline:0}
.ab2{display:grid;grid-template-columns:240px minmax(0,1fr);gap:40px;margin-top:30px}
.ab2 img{border:2px solid var(--ink);aspect-ratio:1;object-fit:cover;width:100%;height:auto;filter:grayscale(1);transition:filter .5s;box-shadow:6px 6px 0 var(--ink)}
.ab2 img:hover{filter:none}
@media (max-width:1100px){.dlog{width:240px}.six{grid-template-columns:repeat(3,1fr)}.inst,.pj2,.sys{grid-template-columns:1fr}.preview2{position:static;order:-1}.pgrid{grid-template-columns:repeat(3,1fr)}}
@media (max-width:900px){.dlog{position:relative;right:auto;top:auto;bottom:auto;width:auto;margin:0 16px;max-height:220px}#explore{height:auto!important;min-height:0!important;display:flex;flex-direction:column;padding-bottom:16px}
 #arena{position:relative!important;height:520px!important;order:2}.hero-copy{position:relative!important;left:auto!important;top:auto!important;margin:16px;order:1}.dlog{order:3}.status{position:relative!important;left:auto!important;bottom:auto!important;margin:10px 16px 0;order:4}
 .pgrid{grid-template-columns:repeat(2,1fr)}.xp{grid-template-columns:1fr}.term ul{columns:1}.term a{grid-template-columns:1fr}.ab2{grid-template-columns:1fr}.ab2 img{max-width:240px}.top-bulletin{padding:8px 16px}}
@media (max-width:600px){.six{grid-template-columns:repeat(2,1fr)}.pgrid{grid-template-columns:1fr 1fr;gap:10px}.pcard{padding:8px}.pcard h3{font-size:.95rem}}
"""


def page():
    proj = [{k: p[k] for k in ('slug', 'href', 'title', 'meta', 'summary', 'outcome', 'facts', 'figure', 'image', 'result')} for p in P]
    data = json.dumps({'projects': proj, 'found': FOUND, 'cubes': CUBES, 'flight': B4.flight(), 'parts': board_parts()}).replace('</', '<\\/')
    cards = ''.join(f"""<li class="pcard card" data-slug="{p['slug']}">{p['icon']}<h3><button type="button" data-open="{p['slug']}">{e(p['title'])}</button></h3>
<p class="m">{e(p['meta'])}</p><p class="r">{e(p['result'])}</p><span class="pill" aria-hidden="true">Tell me more</span></li>""" for p in P)
    olist = ''.join(f'<li><button type="button" data-fly="{p["slug"]}">{e(p["title"])}<i>{e(YEAR[p["slug"]][-4:])}</i></button></li>' for p in P)
    six = ''.join(gauge(*g).replace('<figure class="gauge"', f'<figure class="gauge" data-key="{k}"', 1) for k, g in [
        ('rank', ('Rover rank', '1st', 1.0, 'OF 17', 'ARC 2026')), ('apogee', ('Apogee', '540', 540 / 600, 'METRES', 'HAVOC-2')),
        ('drc', ('ERC errors', '0', 0.0, 'OSIRIS V0', 'schematic check')), ('sims', ('Sim flights', '200', 200 / 250, 'AIRBRAKES', '4 controllers')),
        ('rows', ('Rows OK', '98,218', 0.99, 'WX STATION', 'All passed')), ('lighter', ('Lighter', '21%', 0.21 / 0.3, 'CRANK ARM', 'Ti, printed'))])
    xp = ''.join(f'<li><div><b>{e(r)}</b><span>{e(o)}</span></div><i>{e(w)}</i></li>' for r, o, w in D['experience'])
    term = ''.join(f'<li><a href="{c["href"]}"><span>{e(c["meta"].split(" · ")[0])}</span><span>{e(c["title"].upper())}</span></a></li>' for c in D['coursework'])
    bio = ''.join(f'<p>{e(x)}</p>' for x in D['about'][:4])
    links = [('live2', 'Live v2'), ('live', 'Live'), ('merged', 'Merged')]
    switch = '<nav class="proto-switch" aria-label="Prototypes">' + ''.join(f'<a href="{k}.html"{" aria-current=page" if k == "live2" else ""}>{n}</a>' for k, n in links) + '</nav>'
    v = int((HERE / 'live2.js').stat().st_mtime) if (HERE / 'live2.js').exists() else 0
    css = B4.CSS + EXTRA_CSS
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Isaac Johan Ziebarth · Live v2</title>
<link rel="stylesheet" href="/assets/css/iso-kit.css"><link rel="stylesheet" href="icons.css">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Chivo+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>@font-face{{font-family:Fraunces;src:url(/assets/fonts/fraunces-900-latin.woff2) format("woff2");font-weight:900;font-display:swap}}
@font-face{{font-family:Sanchez;src:url(/assets/fonts/sanchez-400-latin.woff2) format("woff2");font-weight:400;font-display:swap}}
.card .icon svg{{width:100%;height:100%;display:block}}{css}</style></head><body>
<a class="vh" href="#main">Skip to content</a>
<div class="top-bulletin" role="note"><b>Available</b>2027 graduate roles and internships · avionics and embedded systems · robotics and autonomy · guidance, navigation and control</div>
<header class="top"><a class="nm" href="#explore"><i>IJZ</i>Isaac Johan Ziebarth</a><nav aria-label="Main"><a href="#explore">Explore</a><a href="#flight">Flight</a><a href="#projects">Projects</a><a href="#systems">Systems</a><a href="#orrery">Orrery</a><a href="#about">About</a></nav></header>
<main id="main">
<section id="explore" aria-labelledby="me"><canvas id="arena" aria-label="A rover exploring an unknown arena with frontier exploration and A* path planning, detecting ArUco markers and coloured cubes. Click to send it somewhere."></canvas>
<div class="hero-copy" data-keep><p class="eyebrow" style="--c:var(--leaf)">01 · Explore</p><h1 id="me">Isaac Johan <span>Ziebarth</span></h1>
<p>I write software that flies, drives and finds its way. This rover runs frontier exploration with A* path planning, like Theseus V at the 2026 Australian Rover Challenge, where we placed 1st of 17. ArUco markers are my projects; coloured cubes are results.</p>
<div class="acts"><button class="btn solid" type="button" id="showall">Show everything</button><a class="btn" href="mailto:{D['email']}">Email me</a></div></div>
<aside class="dlog" data-keep aria-label="Detections"><div class="hd">Detections <b id="log-n">0/14</b></div><ol id="log" aria-live="polite"></ol></aside>
<div class="tip" id="tip" hidden></div>
<div class="status" data-keep><span class="mono" id="st">booting</span><span class="bar" aria-hidden="true"><i id="stbar"></i></span><span class="mono">click the floor to set a goal · hover a marker</span></div></section>

<section id="instruments" aria-labelledby="ih"><div class="wrap"><p class="eyebrow" style="--c:var(--leaf)">01b · Instruments</p><h2 id="ih">Results at a glance</h2>
<div class="inst"><div><div class="six" role="group" aria-label="Results as gauges">{six}</div>
<div class="ginfo"><p class="mono" id="g-hint">0 of 6 cubes found. Each needle wakes when the rover finds its cube.</p><button class="btn" type="button" id="g-wake">Wake all gauges</button></div></div>
<aside class="status-panel" aria-label="Status"><div class="sp"><span class="k">Now <span class="lampx">nominal</span></span><b>Research assistant</b><p>PX4 flight control and modelling, UQ School of EECS</p></div>
<div class="sp"><span class="k">Also now</span><b>Avionics engineer, UQ Space</b><p>Ground stations, PCBs and the Theseus VI autonomy stack</p></div>
<div class="sp"><span class="k">Next up <span>2027</span></span><b>Graduating November 2027</b><p>Open to internships and graduate roles in avionics, autonomy and GNC.</p></div></aside></div></div></section>

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

<section id="projects" aria-labelledby="ph"><div class="wrap"><p class="eyebrow" style="--c:var(--yel)">03 · Hover to wake</p><h2 id="ph">Projects</h2>
<p class="intro">Hover a card and its model moves; its real figure wakes up in the panel. Click for the full file.</p>
<div class="pj2"><ul class="pgrid">{cards}</ul>
<div class="preview2" aria-live="polite"><div class="pv" id="pv"><div class="ph">Hover a project</div></div><div class="pv-cap"><div><b id="pv-t"></b><p id="pv-s"></p></div><button class="btn" type="button" id="pv-open" hidden>Open</button></div></div></div></div></section>

<section class="systems" id="systems" aria-labelledby="sh"><div class="wrap"><p class="eyebrow" style="--c:var(--org)">04 · Systems, running</p><h2 id="sh">Two systems you can poke</h2>
<div class="sys"><div class="panel2"><div class="ph2"><h3>Airbrake controller</h3><span class="mono">drag the target</span></div>
<p class="note">A rocket coasts from burnout while the controller predicts apogee every step and opens the brakes to land on the target. Illustrative drag model, not the Hera study: there, three of my four controllers hit a 2,900 m target within about 4 m RMS on 177 reachable simulated flights.</p>
<canvas id="ab" width="1100" height="720" aria-label="Airbrake controller: altitude against time with brakes shut and with the controller, and a draggable target apogee"></canvas>
<div class="abro"><div><b id="ab-p">-</b><span>predicted apogee</span></div><div><b id="ab-u">-</b><span>brake deployment</span></div><div><b id="ab-e">-</b><span>miss at apogee</span></div></div>
<label class="abctl">Target <input id="ab-t" type="range" min="2400" max="3080" value="2900" aria-label="Target apogee in metres"></label></div>
<div class="panel2"><div class="ph2"><h3>OSIRIS V0, powered up</h3><span class="mono">hover a part</span></div>
<p class="note">My own flight computer board in KiCad. Orange is power from the battery through the buck to the STM32F411 module, green is sensor data coming in, yellow is logging out to the microSD on the underside.</p>
<div id="pcb"><img src="/assets/img/projects/osiris-v0-top.jpg" alt="Top view of the OSIRIS V0 board" width="1504" height="1568"><svg id="pcb-svg" viewBox="0 0 100 104.3" preserveAspectRatio="none" aria-hidden="true"></svg></div>
<p class="pcb-cap" id="pcb-cap">Hover or tab to a numbered part to trace its connections.</p>
<div class="pcb-leg" aria-hidden="true"><span><i style="background:#FF5102"></i>power</span><span><i style="background:#3E9B5F"></i>sensor data</span><span><i style="background:#FFC908"></i>logging</span></div></div></div></div></section>

<section id="orrery" aria-labelledby="oh"><div class="wrap"><p class="eyebrow" style="--c:var(--ind);color:#9aa0a8">05 · Plan a transfer</p><h2 id="oh">Every project is a body in orbit</h2>
<p class="intro">Built on the orbital mechanics from my digital orrery. Pick a project and the craft waits for the Hohmann launch window, burns, and coasts across on the transfer ellipse. When it arrives, the project opens.</p>
<div class="orb"><canvas id="sky" width="1200" height="960" aria-label="Projects orbiting as planets; pick one to fly a Hohmann transfer to it"></canvas>
<div><ul class="olist">{olist}</ul><p class="mission" id="mission" aria-live="polite">Pick a destination.</p></div></div></div></section>

<section id="about" aria-labelledby="ah"><div class="wrap"><p class="eyebrow" style="--c:var(--red)">06 · About</p><h2 id="ah">The engineer</h2>
<div class="ab2"><img src="/assets/img/profile.jpg" alt="Isaac Johan Ziebarth" width="800" height="800"><div>{bio}
<div class="term"><p class="hd">&gt; QUERY COURSEWORK --ALL ... {len(D['coursework'])} RECORDS</p><ul>{term}</ul></div></div></div></div></section>
<section class="redband" aria-labelledby="xh"><div class="wrap"><p class="eyebrow">07 · Experience</p><h2 id="xh">Service record</h2><ul class="xp">{xp}</ul><p class="edu">{e(D['edu'])}</p></div></section>
<section id="contact" aria-labelledby="ch"><div class="wrap"><p class="eyebrow" style="--c:var(--leaf);justify-content:center">08 · Graduating 2027 · avionics, autonomy, GNC</p><h2 id="ch">Let's build the next one.</h2>
<div class="acts"><a class="btn solid" href="mailto:{D['email']}">Email me</a><a class="btn" href="{D['linkedin']}">LinkedIn</a><a class="btn" href="{D['github']}">GitHub</a></div></div></section>
</main>
<dialog class="full" aria-labelledby="f-t"><button class="btn x" type="button" id="f-x">Close</button><div class="g"><div class="side"><p class="mono" id="f-m"></p><h3 id="f-t"></h3><p class="r" id="f-r"></p><p id="f-o"></p><div id="f-f"></div>
<div class="acts"><a class="btn solid" id="f-h" href="#">Read the write-up</a></div></div><div class="live" id="f-l"></div></div></dialog>
{switch}
<script type="application/json" id="data">{data}</script>
<script src="live2.js?v={v}"></script><script src="/assets/js/site.js"></script></body></html>"""


def js():
    s = (HERE / 'live.js').read_text()
    a, b, c, d, n = (s.find(m) for m in ('/* ---------- 1.', '/* ---------- 2.', '/* ---------- 3.', '/* ---------- 4.', '/* nav highlight */'))
    parts = (HERE / 'live2-parts.js').read_text()
    wake = s[c:d].replace("'.prow'", "'.pcard'").replace('.prow', '.pcard').replace('show(r.dataset.slug), 140)', 'show(r.dataset.slug), 320)')
    return s[:a] + parts + '\n' + s[b:c] + wake + s[d:]


if __name__ == '__main__':
    (HERE / 'live2.js').write_text(js())
    (HERE / 'live2.html').write_text(page())
    print('live2.html', f"{(HERE / 'live2.html').stat().st_size / 1024:.0f} KB", 'parts', len(board_parts()))
