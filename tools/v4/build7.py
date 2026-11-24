"""Live v4: Theseus V to scale (CAD sprite, MID-360 + two 60 deg cameras, bucket pickups, camera-coloured cloud,
3D rover's-eye inset), airbrake graph scrubbing the 3D FHC-1 rocket, and the space section as "drag the launch".
python3 -I build7.py -> live4.html + live4.js. Local only.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build6 as B6  # noqa: E402
import content as C  # noqa: E402

CSS4 = """
#eye{position:absolute;right:14px;bottom:14px;width:340px;height:220px;z-index:4;background:linear-gradient(#F5F4F0,#E1DED5);border:2px solid var(--ink);box-shadow:5px 5px 0 var(--ink)}
.viewsw{position:absolute;right:14px;top:14px;z-index:5;display:flex;border:2px solid var(--ink);background:var(--panel)}
.viewsw button{all:unset;cursor:pointer;font:600 12px var(--mono);letter-spacing:.06em;text-transform:uppercase;padding:7px 10px}
.viewsw button[aria-pressed=true]{background:var(--ink);color:var(--paper)}.viewsw button:focus-visible{outline:3px solid var(--red)}
.snote{position:absolute;right:14px;top:56px;z-index:5;max-width:380px;margin:0;font:500 12px/1.45 var(--mono);background:var(--panel);border:2px solid var(--ink);padding:8px 10px}
#eye canvas{width:100%!important;height:100%!important;display:block}
#eye .lbl{position:absolute;left:8px;top:6px;font:600 11px var(--mono);letter-spacing:.06em;text-transform:uppercase;background:var(--panel);padding:2px 6px;border:1px solid var(--ink);z-index:2}
.sensors{position:absolute;left:22px;bottom:44px;z-index:3;display:flex;gap:12px;flex-wrap:wrap;font:500 11px var(--mono);background:color-mix(in srgb,var(--panel) 85%,transparent);padding:5px 8px;border:1px solid var(--line)}
.sensors span{display:inline-flex;align-items:center;gap:5px}.sensors i{display:inline-block;width:14px;height:8px}
.livo{display:inline-flex;align-items:center;gap:6px;font:600 12px var(--mono);cursor:pointer}
.livo input{accent-color:var(--leaf)}
#space{padding:100px 0;background:#101216;color:var(--paper);border-bottom:1px solid var(--line)}
#space h2{color:var(--paper)}#space .intro{color:#C9C3DD}
.spg{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:28px;margin-top:30px;align-items:start}
#sol{width:100%;height:auto;display:block;border:2px solid #3a3f47;background:radial-gradient(circle at 50% 50%,#1b1f2e,#0b0c10 75%)}
.spc label{display:block;font:600 12px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:#9aa0a8;margin:16px 0 6px}
.spc input[type=range]{width:100%;accent-color:var(--yel)}
.spc .val{font:600 15px var(--mono);color:#fff;margin:4px 0 0}
.dvm{margin-top:18px;border:2px solid #3a3f47;padding:12px 14px}
.dvm b{font:700 2.6rem/1 var(--head);color:#fff}.dvm span{font:500 12px var(--mono);color:#9aa0a8}
.dvbar{height:10px;background:#22252d;margin-top:10px}.dvbar i{display:block;height:100%;width:40%;transition:width .15s,background .15s}
#mini{width:100%;height:auto;display:block;border:2px solid #3a3f47;margin-top:16px;cursor:crosshair;image-rendering:pixelated;touch-action:none}
.mini-l{display:flex;justify-content:space-between;font:500 11px var(--mono);color:#9aa0a8;margin-top:4px}
#sp-msg{font:500 14px/1.5 var(--mono);color:#E6E1F5;min-height:4.5em;margin-top:14px}#sp-msg b{color:var(--yel)}
#space .btn{border-color:#E6E1F5;color:#E6E1F5}#space .btn.solid{background:var(--yel);border-color:var(--yel);color:var(--ink)}#space .btn:disabled{opacity:.4}
.spb{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
/* motion: one easing token; the card lift animates transform/opacity only (the hard shadow is a pseudo-element) */
:root{--ease-out:cubic-bezier(0.23,1,0.32,1)}
.pcard{transition:transform 200ms var(--ease-out)!important;box-shadow:none!important}
.pcard{isolation:isolate;background:transparent!important}
.pcard::after{content:"";position:absolute;inset:0;background:#FFF7DA;z-index:-1}
.pcard::before{content:"";position:absolute;inset:-2px;background:var(--ink);transform:translate(0,0);opacity:0;z-index:-2;transition:transform 200ms var(--ease-out),opacity 200ms var(--ease-out)}
.pcard:hover::before,.pcard:focus-within::before,.pcard.on::before{transform:translate(6px,6px);opacity:1}
.pcard.on::before{background:var(--ind)}
.dlog li,.side li,#latest{animation-timing-function:var(--ease-out)!important}
dialog.full[open]{animation:dlg-in 200ms var(--ease-out)}
dialog.full[open]::backdrop{animation:dlg-fade 200ms var(--ease-out)}
@keyframes dlg-in{from{opacity:0;transform:scale(.96)}}
@keyframes dlg-fade{from{opacity:0}}
@media (prefers-reduced-motion:reduce){
 .top-bulletin b::before{animation:none}
 .dlog li,.side li,#latest,dialog.full[open],dialog.full[open]::backdrop{animation:none!important}
 .pcard,.pcard::before{transition:none!important}.pcard:hover,.pcard:focus-within,.pcard.on{transform:none}
 .pv iframe,.pv img,#ab-model .abf{transition:none}
 html{scroll-behavior:auto}
}
@media (max-width:1100px){.spg{grid-template-columns:1fr}#eye{width:240px;height:160px}}
@media (max-width:700px){#eye{display:none}.sensors{display:none}}
"""

SPACE = """<section id="space" aria-labelledby="sph"><div class="wrap"><p class="eyebrow" style="--c:var(--ind);color:#9aa0a8">04 · Space</p><h2 id="sph">Drag the launch</h2>
<p class="intro">Pick a launch date and a flight time to Mars. Every move runs a real Lambert solve with my digital orrery's own code and redraws the transfer; the meter shows what it costs from a 200 km Earth orbit to capture at Mars. Find a cheap one and launch it.</p>
<div class="spg"><canvas id="sol" width="1100" height="1000" aria-label="Top-down view of the inner solar system with the transfer from Earth"></canvas>
<div class="spc"><label for="sp-dep">Launch date</label><input id="sp-dep" type="range" min="0" max="120" value="30"><p class="val" id="sp-dep-l">-</p>
<label for="sp-tof">Flight time</label><input id="sp-tof" type="range" min="100" max="450" step="2" value="250"><p class="val" id="sp-tof-l">-</p>
<div class="dvm"><span>Δv, km/s</span><br><b id="sp-dv">-</b><div class="dvbar"><i id="sp-bar"></i></div></div>
<canvas id="mini" width="240" height="176" aria-label="Porkchop map of every launch date and flight time; click or drag to pick"></canvas>
<div class="mini-l"><span>launch date →</span><span>↑ flight time · every transfer, from the orrery</span></div>
<div class="spb"><button class="btn solid" type="button" id="sp-go" disabled>Launch</button><button class="btn" type="button" id="sp-best">Fly the best</button><button class="btn" type="button" id="sp-dest">Go to Venus instead</button></div>
<p id="sp-msg">Loading the solver...</p></div></div></div></section>"""


def home():
    h = B6.home()
    def rep(a, b):
        nonlocal h
        assert a in h, a[:90]
        h = h.replace(a, b, 1)
    rep('<script type="importmap">', '<script type="importmap">')
    h = h.replace('<style>', '<style>' + CSS4.replace('\\', '\\\\'), 1) if False else h.replace('</style>', CSS4 + '</style>', 1)
    rep("""<p>I write software that flies, drives and finds its way. This rover runs frontier exploration with A* path planning, like Theseus V at the 2026 Australian Rover Challenge, where we placed 1st of 17. It keeps mapping new sectors for as long as you watch.</p>""",
        """<p>I write software that flies, drives and finds its way. Here is Theseus V, drawn to scale from its CAD, as it ran at the 2026 Australian Rover Challenge, where we placed 1st of 17: a Livox MID-360 maps, two 60° cameras find the markers, and A* plans round its own footprint. It keeps covering new sectors for as long as you watch.</p>""")
    rep('<div class="tip" id="tip" hidden></div>', '''<div class="tip" id="tip" hidden></div>
<div class="viewsw" data-keep role="group" aria-label="Map view"><button type="button" data-view="cloud" aria-pressed="true">Point cloud</button><button type="button" data-view="costmap" aria-pressed="false">2D costmap</button><button type="button" data-view="nav2" aria-pressed="false">Nav2</button><button type="button" id="rv-pause" aria-pressed="false">Pause</button></div>
<p class="snote" id="sensors-note" hidden>Theseus V has no 2D LiDAR. Its ground filter keeps MID-360 returns 0.08 to 1.0 m up and Nav2 plans on them, on KISS-SLAM's 15 cm occupancy grid; an earlier build sliced the cloud into a 2D scan with pointcloud_to_laserscan. <b style="color:#111">■</b> occupied · <b style="color:#A028C8">■</b> footprint · <b style="color:#28AAD2">■</b> cost · <b style="color:#E0282E">■</b> latest scan</p>
<p class="snote" id="nav2-note" hidden>How Theseus V drives with Nav2. The planner searches the costmap outward from the rover (<b style="color:#2E1499">■</b> the cells it tried, <b style="color:#C9A000">■</b> its front); a smoother rounds off its grid path (dotted) into the one it drives (red); Regulated Pure Pursuit steers for a point 0.8 m ahead on that path (<b style="color:#C9A000">●</b> in the circle), slowing near obstacles. Cost (<b style="color:#28AAD2">■</b>) falls away over the 1.0 m inflation radius. When it stops making progress, the behaviour tree backs it up 0.3 m and plans again. <b style="color:#3E9B5F">◆</b> places worth exploring.</p>
<div id="eye" data-keep aria-label="3D view of the MID-360 point cloud from behind the rover"><span class="lbl">MID-360 cloud · 3D</span></div>
<div class="sensors" aria-hidden="true"><span><i style="background:rgba(255,201,8,.5)"></i>cameras, 60° · 4 m</span><span><i style="background:#78C8FF"></i>latest LiDAR scan</span><span><i style="background:#2E1499"></i>LiDAR returns</span><span><i style="background:#c8b28a"></i>camera-coloured</span><span><i style="background:#BB0700;height:3px"></i>A* path</span></div>''')
    rep('<span class="mono">coins <b id="coins">0</b> · score <b id="score">0</b></span>', '<label class="livo"><input type="checkbox" id="livo" checked> colour from cameras</label><span class="mono">coins <b id="coins">0</b> · score <b id="score">0</b></span>')
    h = re.sub(r'<section id="puzzle".*?</section>', SPACE, h, count=1, flags=re.S)
    # the header's five items, as settled in site-architecture-2026-11-19.md: Space is reached by scrolling
    rep('<nav aria-label="Main"><a href="#explore">Explore</a><a href="#projects">Projects</a><a href="#systems">Systems</a><a href="#puzzle">Puzzle</a><a href="#about">About</a><a href="#contact">Contact</a></nav>',
        '<nav aria-label="Main"><a href="#projects">Projects</a><a href="#systems">Systems</a><a href="#coursework">Coursework</a><a href="#about">About</a><a href="#contact">Contact</a></nav>')
    # coursework as its own section of cards after Projects (Isaac, 19 Nov 2026), replacing the terminal list in About
    D = B6.D if hasattr(B6, 'D') else C.load()
    cw = D['coursework']
    h = re.sub(r'<div class="term">.*?</ul></div>', '', h, count=1, flags=re.S)
    i = h.index('<section class="systems" id="systems"')
    h = h[:i] + ('<section id="coursework" aria-labelledby="cwh"><div class="wrap"><p class="eyebrow" style="--c:var(--leaf)">03 · Coursework</p>'
                 f'<h2 id="cwh">Coursework</h2><p class="intro">{len(cw)} pieces from my degree at UQ, newest first. Each says whether it was mine alone or a team effort.</p>'
                 + C.cw_cards(cw, 'vt/coursework.html') + '<p class="cwmore"><a class="btn" href="vt/coursework.html">All coursework write-ups</a></p></div></section>\n') + h[i:]
    for old, new in (('03 · Systems', '04 · Systems'), ('04 · Space', '05 · Space'), ('05 · About', '06 · About'), ('06 · Experience', '07 · Experience'), ('07 · Graduating', '08 · Graduating')):
        h = h.replace(old, new, 1)
    rep('<span class="mono">drag the yellow target</span>', '<span class="mono">scrub along the graph · drag the yellow target</span>')
    h = re.sub(r'<script src="live3\.js\?v=\d+"></script><script type="module" src="puzzle\.js\?v=\d+"></script><script type="module" src="ab3d\.js\?v=\d+"></script>',
               lambda m: f'<script src="live4.js?v={V}"></script><script type="module" src="space.js?v={V}"></script><script type="module" src="ab3d.js?v={V}"></script><script type="module" src="rover3d.js?v={V}"></script>', h, count=1)
    assert 'live4.js' in h
    h = h.replace('<title>Isaac Johan Ziebarth · Live v3</title>', '<title>Isaac Johan Ziebarth · Live v4</title>')
    h = h.replace('<meta name="viewport" content="width=device-width,initial-scale=1">', '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#F5F4F0"><meta name="color-scheme" content="light">', 1).replace('</style></head>', '</style><link rel="stylesheet" href="polish.css"><link rel="stylesheet" href="fonts3.css"></head>', 1)
    # Three fonts (19 Nov, Isaac's pick): Barlow Condensed dropped; fonts3.css moves its labels to Chivo Mono caps.
    assert 'family=Barlow+Condensed:wght@600;700&' in h
    h = h.replace('family=Barlow+Condensed:wght@600;700&', '', 1)
    h = h.replace("--head:'Barlow Condensed',Arial Narrow,sans-serif", "--head:'Chivo Mono',ui-monospace,monospace", 1)
    h = re.sub(r'<nav class="proto-switch".*?</nav>', '<nav class="proto-switch" aria-label="Prototypes"><a href="live4.html" aria-current=page>Live v4</a><a href="live4-bit.html">Bit rover</a><a href="live4-ring.html">v4 archive</a><a href="archive-v3.html">v3 archive</a><a href="/.impeccable/mocks/archive-live/index.html">Old site</a><a href="project-havoc2.html">HAVOC-2 page</a></nav>', h, count=1, flags=re.S)
    return h


def js():
    s = (HERE / 'live.js').read_text()
    a, b, c, d, n = (s.find(m) for m in ('/* ---------- 1.', '/* ---------- 2.', '/* ---------- 3.', '/* ---------- 4.', '/* nav highlight */'))
    shared = s[:a].replace("document.getElementById('f-x').onclick = () => dlg.close();\n  dlg.addEventListener", "if (dlg) { document.getElementById('f-x').onclick = () => dlg.close();\n  dlg.addEventListener")
    shared = shared.replace("dlg.addEventListener('click', ev => { if (ev.target === dlg) dlg.close(); });", "dlg.addEventListener('click', ev => { if (ev.target === dlg) dlg.close(); }); }")
    flight = s[b:c].replace("(function flight() {\n", "(function flight() {\n    if (!document.getElementById('alt')) return;\n", 1)
    wake = s[c:d].replace("'.prow'", "'.pcard'").replace('.prow', '.pcard').replace('show(r.dataset.slug), 140)', 'show(r.dataset.slug), 320)')
    wake = wake.replace("(function wake() {\n", "(function wake() {\n    if (!document.getElementById('pv')) return;\n", 1)
    # the preview panel takes the shape of the figure it is showing (content.py's ratio)
    old = "t.textContent = p.title;"
    assert old in wake
    wake = wake.replace(old, "pv.style.aspectRatio = String(p.ratio || 16 / 11); pv.style.height = ''; " + old, 1)
    # a live figure page grows taller as the panel narrows, so once it loads the panel takes its real height (same
    # origin), up to the window; a taller figure is zoomed down to fit, never scrolled inside the panel (Isaac, 19 Nov
    # 2026: no scrolling windows); a very tall one is scaled to no less than 62% and clipped
    old = "if (el.tagName === 'IFRAME') { el.addEventListener('load', () => { el.dataset.ok = 1; if (cur === slug) el.classList.add('on'); }, { once: true }); if (el.dataset.ok) el.classList.add('on'); }"
    assert old in wake
    fit = ("const fit = () => { try { const doc = el.contentDocument, d = doc.documentElement, b = doc.body, cap = Math.max(320, innerHeight - 230);"
           " el.style.transform = el.style.width = el.style.height = ''; d.style.overflow = 'hidden'; let h = Math.ceil(Math.max(d.scrollHeight, d.getBoundingClientRect().height));"
           " if (h > cap) { const k = Math.max(.62, cap / h); el.style.transformOrigin = '0 0'; el.style.transform = 'scale(' + k.toFixed(3) + ')'; el.style.width = el.style.height = (100 / k).toFixed(2) + '%'; h = cap; }"   # the frame is scaled, not its content, so pointer positions inside stay true; never below 62%, the rest is clipped
           " el.dataset.h = h; if (cur === slug) { pv.style.aspectRatio = 'auto'; pv.style.height = el.dataset.h + 'px'; } } catch (e) {} };")
    wake = wake.replace(old, "if (el.tagName === 'IFRAME') { " + fit + " el.addEventListener('load', () => { el.dataset.ok = 1; if (cur === slug) el.classList.add('on'); fit(); setTimeout(fit, 1500); }, { once: true }); if (el.dataset.ok) { el.classList.add('on'); fit(); } }", 1)
    # the header now links a page (Coursework) as well as sections, so only '#' links are watched
    nav = s[n:].replace("links.forEach(a => { const s = document.querySelector(a.getAttribute('href')); if (s) io.observe(s); });",
                        "links.forEach(a => { const h = a.getAttribute('href'); const s = h.startsWith('#') && document.querySelector(h); if (s) io.observe(s); });")
    assert "h.startsWith('#')" in nav
    return shared + (HERE / ROVER).read_text() + '\n' + flight + wake + (HERE / 'live4-systems.js').read_text() + '\n  ' + nav


ROVER = 'live4-rover.js'

def worst():   # break-ui: realistic worst cases at the data boundary (content), never in markup
    P = B6.P
    P[3]['title'] = 'Six-degree-of-freedom airbrake control simulation for UQ Space\'s Hera sounding rocket'
    P[3]['result'] = 'three of four controllers within about 4 m RMS of a 2,900 m target on 177 reachable flights'
    P[1]['meta'] = 'Team project · UQ Space · Avionics and Recovery subteams · 2025–26'
    P[7]['figure'] = None; P[7]['image'] = None                    # a project with no figure and no image yet
    P[5]['title'] = 'Station météo du site de lancement'               # a translated title, diacritics
    P[2]['result'] = '0 ERC errors'
    P[2]['outcome'] = P[2]['outcome'] * 3                            # a long write-up summary
    P[2]['facts'] = P[2]['facts'] + [('Collaborators', 'Université de Liège, Technische Universität München, The University of Queensland')]

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'live4'
    if out.endswith('-worst'): worst()          # e.g. build7.py live4-ring live4-rover-ring.js (archived variants)
    if len(sys.argv) > 2: ROVER = sys.argv[2]
    (HERE / f'{out}.js').write_text(js())
    V = int((HERE / f'{out}.js').stat().st_mtime)
    h = home().replace('live4.js?v=', f'{out}.js?v=')
    if out.endswith('-worst') or out == 'live4': h = h.replace('</body>', '<nav class="dataswitch" aria-label="Test data (dev only)"><a href="live4.html"' + (' aria-current=page' if out == 'live4' else '') + '>Demo data</a><a href="live4-worst.html"' + (' aria-current=page' if out != 'live4' else '') + '>Worst case</a></nav><style>.dataswitch{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(60px + env(safe-area-inset-bottom,0px));z-index:98;display:flex;background:#e5e5e5;border-radius:8px;padding:3px;font:500 12px system-ui,sans-serif}.dataswitch a{padding:5px 10px;border-radius:6px;color:#333;text-decoration:none}.dataswitch a[aria-current]{background:#fff;box-shadow:0 1px 2px #0002}</style></body>', 1)
    if out == 'live4-bit':   # the bit-character rover (make_bit.py): same autonomy, v3's size and look, so not 'to scale'
        h = h.replace('Here is Theseus V, drawn to scale from its CAD, as it ran at', 'Here is a pocket-sized Theseus V running the autonomy it ran at')
        assert 'to scale' not in h.split('<h1', 1)[-1].split('</section>', 1)[0], 'the bit rover hero still claims it is drawn to scale'
        h = h.replace('<title>Isaac Johan Ziebarth · Live v4</title>', '<title>Isaac Johan Ziebarth · Live v4, bit rover</title>')
    elif out != 'live4': h = h.replace('<title>Isaac Johan Ziebarth · Live v4</title>', f'<title>Isaac Johan Ziebarth · {out} (archived)</title>')
    (HERE / f'{out}.html').write_text(h)
    print(out + '.html', (HERE / f'{out}.html').stat().st_size // 1024, 'KB')
