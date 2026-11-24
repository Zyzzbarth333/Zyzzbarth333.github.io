"""Live v3: endless rover with field finds and a side panel, the projects grid, airbrakes with the real renders,
an OSIRIS logic analyser (real netlist buses, wiring-standard colours), a launch-window puzzle on the orrery's own
solver, and the HAVOC-2 scroll replay moved onto a prototype project page.

python3 -I build6.py -> live3.html, project-havoc2.html, live3.js. Local only.
"""
import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build4 as B4  # noqa: E402
import build5 as B5  # noqa: E402
import content as C  # noqa: E402

D, P, e, YEAR = B4.D, B4.P, html.escape, B4.YEAR
BY = {p['slug']: p for p in P}

CSS3 = """
#explore{height:auto!important;min-height:0!important;overflow:visible!important;border-bottom:1px solid var(--line)}
.ex{display:grid;grid-template-columns:minmax(0,1fr) 360px;height:min(84vh,820px);min-height:580px}
#arena-wrap{position:relative;overflow:hidden;border-right:2px solid var(--ink)}
#arena{position:absolute;inset:0;width:100%;height:100%}
.side{display:flex;flex-direction:column;background:var(--panel);min-height:0}
.side::before{content:"";display:block;height:6px;background:var(--stripe);flex:none}
.side .hd{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid var(--line);font:600 12px var(--mono);letter-spacing:.08em;text-transform:uppercase}
.side .hd b{color:var(--red)}
#latest{display:grid;grid-template-columns:96px 1fr;gap:12px;padding:14px;border-bottom:2px solid var(--ink);min-height:150px;align-items:start;animation:slidein .45s cubic-bezier(.2,1,.3,1)}
#latest .lt-ic{width:96px;height:96px;display:grid;place-items:center;background:#FFF7DA;border:2px solid var(--ink)}
#latest .lt-ic .icon{display:block;width:100%;height:100%}
#latest .lt-ic .glyph{width:44px;height:44px}
#latest .mono{margin:0 0 4px;color:var(--mute);font-size:11px}
#latest b{display:block;font:900 1.15rem/1.15 Fraunces,Georgia,serif;margin-bottom:4px}
#latest p{margin:0 0 8px;font-size:.9rem}
#latest .btn{padding:7px 12px;font-size:13px}
#latest .empty{grid-column:1/-1;font:500 13px/1.5 var(--mono);color:var(--mute);margin:0}
.side ol{list-style:none;margin:0;padding:6px 8px;overflow:auto;flex:1;min-height:0}
.side li{animation:slidein .45s cubic-bezier(.2,1,.3,1)}
.side .row{all:unset;box-sizing:border-box;width:100%;display:grid;grid-template-columns:22px 1fr auto;gap:10px;align-items:center;padding:7px 4px;border-bottom:1px dashed var(--line);font:500 12px/1.3 var(--mono)}
button.row{cursor:pointer}button.row:hover,button.row:focus-visible{background:var(--yel);outline:0}
.side .row b{font-weight:600;display:block}.side .row em{font-style:normal;color:var(--mute)}.side .row i{font-style:normal;color:var(--leaf);font-weight:600}
.side .ft{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:10px 14px;border-top:1px solid var(--line);font:600 12px var(--mono)}
.side .ft .btn{padding:8px 12px;font-size:13px}
.counts{display:flex;gap:16px}.counts span b{color:var(--ind);font-size:14px}
.hero-copy{max-width:470px}
.status{left:22px;bottom:16px}
.ab3{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);border-top:1px solid var(--line)}
.ab3 canvas{width:100%;height:auto;display:block;touch-action:none;border-right:1px solid var(--line)}
#ab-model{position:relative;aspect-ratio:1;background:#FFF7DA;margin:0}
#ab-model img{position:absolute;inset:0;width:100%;height:100%}
#ab-model .abf{opacity:0;transition:opacity .12s}#ab-model .abf.on{opacity:1}
#ab-model figcaption{position:absolute;left:12px;bottom:10px;font:600 12px var(--mono);background:var(--panel);border:1.5px solid var(--ink);padding:5px 8px}
#ab-model figcaption b{color:var(--org);font-size:15px}
.abro{grid-template-columns:repeat(4,1fr)!important}
.la{display:grid;grid-template-columns:minmax(0,.75fr) minmax(0,1.25fr);border-top:1px solid var(--line);align-items:start}
#la-board{position:relative;background:#fff;border-right:1px solid var(--line)}
#la-board img{width:100%;height:auto;display:block}
#la-board .pm{transition:box-shadow .15s,background .15s}
#la-board .pm.act{background:var(--leaf);color:#fff;box-shadow:0 0 0 5px rgba(62,155,95,.35),0 0 16px rgba(62,155,95,.9)}
#la{width:100%;display:block;background:#15171B}
.sysv{display:grid;gap:30px;margin-top:30px}
.wires{display:flex;flex-wrap:wrap;gap:12px;padding:10px 18px 16px;font:500 12px var(--mono)}
.wires span{display:inline-flex;align-items:center;gap:6px}.wires i{width:22px;height:8px;display:inline-block;border:1px solid #0004}
#puzzle{padding:100px 0;background:#14161A;color:var(--paper);border-bottom:1px solid var(--line)}
#puzzle h2{color:var(--paper)}#puzzle .intro{color:#C9C3DD}
.pzg{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:26px;margin-top:30px}
#pz{width:100%;height:auto;display:block;border:2px solid #3a3f47;cursor:crosshair}
#pz-orbit{width:100%;height:auto;display:block;border:2px solid #3a3f47;margin-top:14px}
.pzs{font:500 13px/1.5 var(--mono)}
.pzs .big{font:700 3rem/1 var(--head);color:var(--yel)}
#pz-msg{font:500 14px/1.5 var(--mono);color:#E6E1F5;min-height:4.5em}
#pz-msg b{color:var(--yel)}
#pz-list{list-style:none;margin:10px 0;padding:0}#pz-list li{padding:5px 0;border-bottom:1px dashed #ffffff22}#pz-list b{color:var(--yel)}
.pzb{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}
#puzzle .btn{border-color:#E6E1F5;color:#E6E1F5}#puzzle .btn.solid{background:var(--yel);border-color:var(--yel);color:var(--ink)}
#puzzle .btn:disabled{opacity:.4;cursor:not-allowed}
.nowp{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border:2px solid var(--ink);background:var(--panel);margin-top:26px}
.nowp .sp{border-right:1px solid var(--line)}.nowp .sp:last-child{border-right:0}
@media (max-width:1100px){.ex{grid-template-columns:1fr;height:auto}#arena-wrap{height:560px;border-right:0;border-bottom:2px solid var(--ink)}.side{max-height:460px}
 .ab3,.la,.pzg{grid-template-columns:1fr}.ab3 canvas{border-right:0}#ab-model{max-width:340px;margin:0 auto}.nowp{grid-template-columns:1fr}.nowp .sp{border-right:0;border-bottom:1px solid var(--line)}}
@media (max-width:700px){#arena-wrap{height:600px}.hero-copy{position:absolute!important;left:12px!important;right:12px!important;top:12px!important;margin:0!important;padding:14px 16px!important}.hero-copy h1{font-size:2.2rem!important}
 .hero-copy p:not(.eyebrow){font-size:.88rem}.status{display:none}.abro{grid-template-columns:repeat(2,1fr)!important}}
.full .side2{padding:26px;overflow:auto;border-right:1px solid var(--line)}
@media (max-width:1100px){#arena{position:absolute!important;height:100%!important}.hero-copy{position:absolute!important;left:16px!important;top:16px!important;margin:0!important}.full .side2{border-right:0;border-bottom:1px solid var(--line);max-height:45vh}}
#ab-model .ab3d{position:absolute;inset:0;width:100%!important;height:100%!important;cursor:grab;touch-action:none}
#ab-model.gl .abf,#ab-model.gl>img{visibility:hidden}
#ab-model{background:radial-gradient(circle at 50% 40%,#FBFAF6,#E1DED5)}
/* project page */
.pp-head{display:grid;grid-template-columns:220px minmax(0,1fr);gap:30px;padding:60px 0 30px;align-items:center}
.pp-head .card{background:#FFF7DA;border:2px solid var(--ink);box-shadow:6px 6px 0 var(--ink)}.pp-head .icon{display:block;width:100%;aspect-ratio:1}
.pp-head h1{font:900 clamp(2.4rem,5vw,4.2rem)/1 Fraunces,Georgia,serif;margin:6px 0 12px}
.pp-head .out{font-size:1.1rem;max-width:62ch;margin:0}
.facts{display:grid;grid-template-columns:repeat(4,1fr);border:2px solid var(--ink);background:var(--panel);margin:10px 0 0}
.facts div{padding:12px 16px;border-right:1px solid var(--line);font-size:.92rem}.facts div:last-child{border-right:0}
.facts dt{font:600 11px var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--mute)}.facts dd{margin:4px 0 0}
.back{display:inline-block;margin-top:26px;font:600 13px var(--mono);text-decoration:none}
@media (max-width:800px){.pp-head{grid-template-columns:1fr}.pp-head .card{max-width:200px}.facts{grid-template-columns:1fr 1fr}}
"""


def head(title, extra=''):
    v = int((HERE / 'live3.js').stat().st_mtime) if (HERE / 'live3.js').exists() else 0
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>{title}</title>
<script type="importmap">{{"imports":{{"three":"/assets/vendor/three-0.187.0/three.module.min.js"}}}}</script>
<link rel="stylesheet" href="/assets/css/iso-kit.css"><link rel="stylesheet" href="icons.css">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Chivo+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>@font-face{{font-family:Fraunces;src:url(/assets/fonts/fraunces-900-latin.woff2) format("woff2");font-weight:900;font-display:swap}}
@font-face{{font-family:Sanchez;src:url(/assets/fonts/sanchez-400-latin.woff2) format("woff2");font-weight:400;font-display:swap}}
.card .icon svg{{width:100%;height:100%;display:block}}{B4.CSS}{B5.EXTRA_CSS}{CSS3}</style></head><body>
<a class="vh" href="#main">Skip to content</a>""", v


def data_json():
    proj = [{k: p.get(k) for k in ('slug', 'href', 'title', 'meta', 'summary', 'outcome', 'facts', 'figure', 'image', 'result', 'ratio')} for p in P]
    for q in proj:   # OSIRIS previews as its board photo: the live KiCad viewer is 2.2 MB and flashed white, cyan, then black (design audit 5)
        if q['slug'] == 'osiris': q.update(figure=None, image='/assets/img/projects/osiris-v0-top.jpg', ratio=round(1504 / 1568, 3))
    return json.dumps({'projects': proj, 'found': B5.FOUND, 'cubes': B5.CUBES, 'flight': B4.flight(), 'parts': B5.board_parts()}).replace('</', '<\\/')


def switch(cur):
    links = [('live3', 'Live v3'), ('project-havoc2', 'HAVOC-2 page'), ('live2', 'Live v2')]
    return '<nav class="proto-switch" aria-label="Prototypes">' + ''.join(f'<a href="{k}.html"{" aria-current=page" if k == cur else ""}>{n}</a>' for k, n in links) + '</nav>'


FLIGHT = """<section id="flight" aria-labelledby="fh"><div class="wrap fl"><div class="fl-steps">
<div class="head"><p class="eyebrow" style="--c:var(--org)">Scroll to fly</p><h2 id="fh">The first flight, replayed</h2><p class="intro">Flown on 12 July 2026. Scroll and the real log replays, frame by frame.</p></div>
<div class="step" data-t="0"><p class="mono">T+0.0 s · liftoff</p><h3>Off the pad</h3><p>The firmware switches from pad idle to boost on the accelerometer, then logs every frame with a checksum.</p></div>
<div class="step" data-t="1.32"><p class="mono">T+1.3 s · burnout</p><h3>Burnout at 11.65 g</h3><p>The motor burns for 1.3 seconds and peaks at 11.65 g. From here the rocket coasts.</p></div>
<div class="step" data-t="9.68"><p class="mono">T+9.7 s · apogee</p><h3>Apogee, about 540 m</h3><p>The barometer and the state machine agree on apogee, and the recovery event fires.</p></div>
<div class="step" data-t="11.38"><p class="mono">T+11.4 s · brownout</p><h3>Nine seconds missing</h3><p>The ejection shock browned out the logger. The gap stays honest on the plot: dashed, not invented.</p></div>
<div class="step" data-t="46.28"><p class="mono">T+46.3 s · landed</p><h3>Every frame passed</h3><p>Under the parachute to the ground. Every logged frame passed its checksum, and COSMOS, the ground station I built, read it back.</p></div></div>
<div class="fl-chart"><div class="readout"><div><b id="ro-t">T+0.0</b><span>seconds</span></div><div><b id="ro-a">0</b><span>metres altitude</span></div><div><b id="ro-p">PAD</b><span>flight state</span></div></div>
<canvas id="alt" width="1200" height="760" aria-label="HAVOC-2 altitude against time, drawn as you scroll"></canvas></div></div></section>"""

DIALOG = """<dialog class="full" aria-labelledby="f-t"><button class="btn x" type="button" id="f-x">Close</button><div class="g"><div class="side2"><p class="mono" id="f-m"></p><h3 id="f-t"></h3><p class="r" id="f-r"></p><p id="f-o"></p><div id="f-f"></div>
<div class="acts"><a class="btn solid" id="f-h" href="#">Read the write-up</a></div></div><div class="live" id="f-l"></div></div></dialog>"""


def home():
    h, v = head('Isaac Johan Ziebarth · Live v3')
    icons = ''.join(f'<template id="ic-{p["slug"]}">{p["icon"]}</template>' for p in P)
    cards = ''.join(f"""<li class="pcard card" data-slug="{p['slug']}">{p['icon']}<h3><button type="button" data-open="{p['slug']}">{e(p['title'])}</button></h3>
<p class="m">{e(p['meta'])}</p><p class="r">{e(p['result'])}</p><span class="pill" aria-hidden="true">Tell me more</span></li>""" for p in P)
    frames = ''.join(f'<img class="abf{" on" if d == 0 else ""}" src="/assets/img/projects/airbrakes-f{d}.webp" alt="">' for d in (0, 16, 32, 48, 64, 80))
    xp = ''.join(f'<li><div><b>{e(r)}</b><span>{e(o)}</span></div><i>{e(w)}</i></li>' for r, o, w in D['experience'])
    term = ''.join(f'<li><a href="{c["href"]}"><span>{e(c["meta"].split(" · ")[0])}</span><span>{e(c["title"].upper())}</span></a></li>' for c in D['coursework'])
    bio = ''.join(f'<p>{e(x)}</p>' for x in D['about'][:4])
    wires = [('#8B5A2B', 'BN', 'chip select'), ('#F5F4F0', 'WH', 'SCK'), ('#8E5BD6', 'VT', 'MOSI'), ('#FF7A1A', 'OG', 'MISO / UART TX'), ('#3B82F6', 'BU', 'SDA'),
             ('#FFC908', 'YE', 'SCL / UART RX'), ('#E0282E', 'RD', '+VBATT'), ('linear-gradient(90deg,#E0282E 0 60%,#FFC908 60%)', 'RDYE', '+3.3 V'), ('#1E2126', 'BK', 'ground')]
    wl = ''.join(f'<span><i style="background:{c}"></i>{k} {n}</span>' for c, k, n in wires)
    body = f"""{h}
<div class="top-bulletin" role="note"><b>Available</b>2027 graduate roles and internships · avionics and embedded systems · robotics and autonomy · guidance, navigation and control</div>
<header class="top"><a class="nm" href="#explore"><i>IJZ</i>Isaac Johan Ziebarth</a><nav aria-label="Main"><a href="#explore">Explore</a><a href="#projects">Projects</a><a href="#systems">Systems</a><a href="#puzzle">Puzzle</a><a href="#about">About</a><a href="#contact">Contact</a></nav></header>
<main id="main">
<section id="explore" aria-labelledby="me"><div class="ex"><div id="arena-wrap"><canvas id="arena" aria-label="A rover exploring an endless series of arena sectors with frontier exploration and A* path planning. Click the floor to send it somewhere; hover a find to read it."></canvas>
<div class="hero-copy" data-keep><p class="eyebrow" style="--c:var(--leaf)">01 · Explore</p><h1 id="me">Isaac Johan <span>Ziebarth</span></h1>
<p>I write software that flies, drives and finds its way. This rover runs frontier exploration with A* path planning, like Theseus V at the 2026 Australian Rover Challenge, where we placed 1st of 17. It keeps mapping new sectors for as long as you watch.</p>
<div class="acts"><a class="btn solid" href="#projects">See the projects</a><a class="btn" href="mailto:{D['email']}">Email me</a></div></div>
<div class="tip" id="tip" hidden></div>
<div class="status" data-keep><span class="mono" id="st">booting</span><span class="mono">· click the floor to set a goal</span></div></div>
<aside class="side" aria-label="Field log"><div class="hd">Latest find <span>sector <b id="sector">01</b></span></div>
<p id="rv-say" class="visually-hidden" aria-live="polite"></p><div id="latest"><p class="empty">Nothing yet. ArUco markers are my projects, coloured cubes are results, and the rest is whatever the arena throws up.</p></div>
<div class="hd">Field log <span class="counts"><span>projects <b id="n-proj">0/8</b></span><span>finds <b id="n-find">0</b></span></span></div>
<ol id="log"></ol>
<div class="ft"><span class="mono">coins <b id="coins">0</b> · score <b id="score">0</b></span><button class="btn" type="button" id="showall">Log all projects</button></div></aside></div></section>

<section id="projects" aria-labelledby="ph"><div class="wrap"><p class="eyebrow" style="--c:var(--yel)">02 · Projects</p><h2 id="ph">Projects</h2>
<p class="intro"><span class="on-hover">Hover a card and its model moves; its real figure wakes up in the panel. Click for the full file.</span><span class="on-touch">Tap a card to open its write-up.</span></p>
<div class="pj2"><ul class="pgrid">{cards}</ul>
<div class="preview2" aria-live="polite"><div class="pv" id="pv"><div class="ph">Hover a project</div></div><div class="pv-cap"><div><b id="pv-t"></b><p id="pv-s"></p></div><button class="btn" type="button" id="pv-open" hidden>Open</button></div></div></div>{C.also_html()}</div></section>

<section class="systems" id="systems" aria-labelledby="sh"><div class="wrap"><p class="eyebrow" style="--c:var(--org)">03 · Systems, running</p><h2 id="sh">Two systems you can poke</h2>
<div class="sysv"><div class="panel2"><div class="ph2"><h3>Airbrake controller, on my airbrake design</h3><span class="mono">drag the yellow target</span></div>
<p class="note">After a 2.5 s lockout past burnout, the controller predicts apogee every step and opens the brakes to land on the target; on the right is my FHC-1 airbrake module from its CAD, in the 30kAB layout C airframe from our OpenRocket model, its four flaps turning on their real hinges. Illustrative drag model, not the Hera study: there, three of my four controllers hit a 2,900 m target within about 4 m RMS on 177 reachable simulated flights.</p>
<div class="ab3"><canvas id="ab" width="1100" height="760" aria-label="Airbrake controller: altitude against time with brakes shut and with the controller, deployment events marked, and a draggable target apogee"></canvas>
<figure id="ab-model"><img src="/assets/img/projects/airbrakes-body.webp" alt="My airbrake design">{frames}<figcaption>FHC-1 flaps <b id="ab-deg">0°</b> · <span id="ab-hud">600 m</span> · drag to orbit</figcaption></figure></div>
<div class="abro"><div><b id="ab-d">-</b><span>brakes open</span></div><div><b id="ab-p">-</b><span>predicted apogee</span></div><div><b id="ab-u">-</b><span>deployment</span></div><div><b id="ab-e">-</b><span>miss at apogee</span></div></div>
<label class="abctl">Target <input id="ab-t" type="range" min="2400" max="3080" value="2900" aria-label="Target apogee in metres"></label></div>
<div class="panel2"><div class="ph2"><h3>OSIRIS V0 on the logic analyser</h3><span class="mono">hover a part</span></div>
<p class="note">The buses are the real V0 netlist: the IMU on SPI1, the barometer and power monitor on I²C1, the microSD on SPI2, a UART out to a JST-PH port, and power from the XT30 through the INA228 shunt and arming key to the buck. Wire colours follow the IEC 60757 codes in the avionics wiring standard I drafted. Traffic timing is illustrative.</p>
<div class="la"><div id="la-board"><img src="/assets/img/projects/osiris-v0-top.jpg" alt="Top view of the OSIRIS V0 board" width="1504" height="1568"></div><canvas id="la" width="1300" height="900" aria-label="Logic analyser traces for each bus on OSIRIS V0"></canvas></div>
<p class="pcb-cap" id="la-cap">Parts light up green while their bus is talking. Hover a numbered part to isolate its bus.</p>
<div class="wires" aria-label="Wire colour key">{wl}</div></div></div></div></section>

<section id="puzzle" aria-labelledby="pzh"><div class="wrap"><p class="eyebrow" style="--c:var(--ind);color:#9aa0a8">04 · Puzzle</p><h2 id="pzh">Find the launch window</h2>
<p class="intro">Every Earth to Mars transfer is worked out live by my digital orrery's own Lambert solver, then hidden. Sweep the scanner across it: warm is cheap, dark is expensive. Click to launch from wherever you are and see how close you came to the optimum.</p>
<div class="pzg"><canvas id="pz" width="1200" height="820" tabindex="0" aria-label="Hidden porkchop plot: departure date across, time of flight up. Move to scan, click or press Enter to launch; arrow keys move the scanner."></canvas>
<div class="pzs"><p>Δv under the scanner, km/s</p><p class="big" id="pz-left">-</p><p id="pz-msg">Loading the solver...</p><ol id="pz-list"></ol>
<div class="pzb"><button class="btn solid" type="button" id="pz-go" disabled>Show me the best</button><button class="btn" type="button" id="pz-again">Try Venus</button></div>
<canvas id="pz-orbit" width="600" height="600" aria-label="The committed transfer, seen from above the Sun"></canvas></div></div></div></section>

<section id="about" aria-labelledby="ah"><div class="wrap"><p class="eyebrow" style="--c:var(--red)">05 · About</p><h2 id="ah">The engineer</h2>
<div class="ab2"><img src="/assets/img/profile.jpg" alt="Isaac Johan Ziebarth" width="800" height="800"><div>{bio}
<div class="nowp"><div class="sp"><span class="k">Now <span class="lampx">nominal</span></span><b>Research assistant</b><p>PX4 flight control and modelling, UQ School of EECS</p></div>
<div class="sp"><span class="k">Also now</span><b>Avionics engineer, UQ Space</b><p>Ground stations, PCBs and the Theseus VI autonomy stack</p></div>
<div class="sp"><span class="k">Next up</span><b>Graduating Nov 2027</b><p>Open to internships and graduate roles in avionics, autonomy and GNC.</p></div></div>
<div class="term"><p class="hd">&gt; QUERY COURSEWORK --ALL ... {len(D['coursework'])} RECORDS</p><ul>{term}</ul></div></div></div></div></section>
<section class="redband" aria-labelledby="xh"><div class="wrap"><p class="eyebrow">06 · Experience</p><h2 id="xh">Service record</h2><ul class="xp">{xp}</ul><p class="edu">{e(D['edu'])}</p></div></section>
<section id="contact" aria-labelledby="ch"><div class="wrap"><p class="eyebrow" style="--c:var(--leaf);justify-content:center">07 · Graduating 2027 · avionics, autonomy, GNC</p><h2 id="ch">Let's build the next one.</h2>
<div class="acts"><a class="btn solid" href="mailto:{D['email']}">Email me</a><a class="btn" href="{D['linkedin']}">LinkedIn</a><a class="btn" href="{D['github']}">GitHub</a><a class="btn" href="{D.get('printables', '')}">Printables</a><a class="btn" href="{D.get('makerworld', '')}">MakerWorld</a></div></div></section>
</main>{DIALOG}{icons}{switch('live3')}
<script type="application/json" id="data">{data_json()}</script>
<script src="live3.js?v={v}"></script><script type="module" src="puzzle.js?v={v}"></script><script type="module" src="ab3d.js?v={v}"></script><script src="/assets/js/site.js"></script></body></html>"""
    return body


def havoc():
    h, v = head('HAVOC-2 firmware and COSMOS ground station · prototype project page')
    p = BY['havoc2-cosmos']
    facts = ''.join(f'<div><dt>{e(k)}</dt><dd>{e(val)}</dd></div>' for k, val in p['facts'][:4])
    return f"""{h}
<header class="top"><a class="nm" href="live3.html"><i>IJZ</i>Isaac Johan Ziebarth</a><nav aria-label="Main"><a href="live3.html#projects">Projects</a><a href="live3.html#about">About</a><a href="live3.html#contact">Contact</a></nav></header>
<main id="main"><div class="wrap"><a class="back" href="live3.html#projects">&larr; All projects</a>
<header class="pp-head"><div class="card">{p['icon']}</div><div><p class="eyebrow" style="--c:var(--org)">{e(p['meta'])}</p><h1>{e(p['title'])}</h1><p class="out">{e(p['outcome'])}</p></div></header>
<dl class="facts">{facts}</dl></div>
{FLIGHT}
<div class="wrap" style="padding:60px 28px 120px"><p class="intro">The rest of the write-up (the problem, what I did, what went wrong and what's next) follows here, in the same template as every project page.</p>
<p style="margin-top:18px"><a class="btn solid" href="/projects/havoc2-cosmos.html">Read the current write-up</a></p></div></main>
{DIALOG}{switch('project-havoc2')}
<script type="application/json" id="data">{data_json()}</script>
<script src="live3.js?v={v}"></script><script src="/assets/js/site.js"></script></body></html>"""


def js():
    s = (HERE / 'live.js').read_text()
    a, b, c, d, n = (s.find(m) for m in ('/* ---------- 1.', '/* ---------- 2.', '/* ---------- 3.', '/* ---------- 4.', '/* nav highlight */'))
    shared = s[:a].replace("document.getElementById('f-x').onclick = () => dlg.close();\n  dlg.addEventListener", "if (dlg) { document.getElementById('f-x').onclick = () => dlg.close();\n  dlg.addEventListener")
    shared = shared.replace("dlg.addEventListener('click', ev => { if (ev.target === dlg) dlg.close(); });", "dlg.addEventListener('click', ev => { if (ev.target === dlg) dlg.close(); }); }")
    flight = s[b:c].replace("(function flight() {\n", "(function flight() {\n    if (!document.getElementById('alt')) return;\n", 1)
    wake = s[c:d].replace("'.prow'", "'.pcard'").replace('.prow', '.pcard').replace('show(r.dataset.slug), 140)', 'show(r.dataset.slug), 320)')
    wake = wake.replace("(function wake() {\n", "(function wake() {\n    if (!document.getElementById('pv')) return;\n", 1)
    return shared + (HERE / 'live3-rover.js').read_text() + '\n' + flight + wake + (HERE / 'live3-systems.js').read_text() + '\n  ' + s[n:]


if __name__ == '__main__':
    (HERE / 'live3.js').write_text(js())
    (HERE / 'live3.html').write_text(home())
    (HERE / 'project-havoc2.html').write_text(havoc())
    print('ok', (HERE / 'live3.html').stat().st_size // 1024, 'KB')
