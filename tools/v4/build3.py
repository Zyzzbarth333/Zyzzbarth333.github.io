"""Merged prototype: one site that fuses every reference the user picked.

  theatre poster (hero, dated border, halftone portrait, loud type)  + Meguri press (paper, seals, editions)
  + Trailhead stack (Now / Next-up widgets, the project stack)        + NASA-punk console (beige panels, screws, amber readouts)
  + six-pack instruments (results as gauges)                          + emergency broadcast (on-air bulletin, one red arrow)
  + mid-century / solarpunk (palette; greenhouse-green nominal lamps)  + variable-font specimen (live width axis on the headline)

python3 -I build3.py -> merged.html beside this file. Local only.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build2 as B  # noqa: E402

D, P, MAIN, e, fill, gauge, bio, YEAR, TOOLS = B.D, B.P, B.MAIN, B.e, B.fill, B.gauge, B.bio, B.YEAR, B.TOOLS
B.PROTOS[:] = [('merged', 'Merged'), ('trailhead', 'Trailhead'), ('meguri', 'Meguri'), ('console', 'Console'), ('poster', 'Poster')]

CSS = """
:root{
 --paper:#F4ECD8;--paper2:#EADFC5;--cream:#FFF6DE;--ink:#1D1736;--ind:#2E1499;--red:#BB0700;--org:#FF5102;--yel:#FFC908;
 --teal:#1F6B5C;--leaf:#5BBF6A;--panel:#DDD6C6;--panel-hi:#EAE4D7;--panel-lo:#D2CAB7;--seam:#A39A86;--seam2:#7D7564;--engrave:#70220D;
 --win:#121110;--amber:#FFB22E;
 --disp:Archivo,system-ui,sans-serif;--head:Fraunces,Georgia,serif;--body:Sanchez,Georgia,serif;--lab:'Barlow Condensed',Arial Narrow,sans-serif;--crt:'VT323',monospace}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 var(--body);
 background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='.85' numOctaves='2' seed='7'/%3E%3CfeColorMatrix values='0 0 0 0 .35 0 0 0 0 .27 0 0 0 0 .18 0 0 0 .07 0'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)'/%3E%3C/svg%3E")}
a{color:inherit}
.lab{font:600 12px/1 var(--lab);letter-spacing:.2em;text-transform:uppercase}
.eng{font:600 12px/1 var(--lab);letter-spacing:.2em;text-transform:uppercase;color:var(--engrave)}
.win{background:var(--win);border-radius:3px;box-shadow:inset 0 2px 6px #000,0 1px 0 #fff6;color:var(--amber);font:400 24px/1 var(--crt);padding:7px 11px;text-shadow:0 0 8px #ffb22e66;display:inline-block}
.panel{background:linear-gradient(180deg,var(--panel-hi),var(--panel) 30%,var(--panel-lo));border:1px solid var(--seam2);box-shadow:inset 0 1px 0 #fff8,inset 0 -2px 0 #0001,0 2px 0 #0003;position:relative;border-radius:3px}
.scr{position:absolute;width:9px;height:9px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#f4efe3,#8d8574 70%);box-shadow:0 0 0 1px #6f6858}
.scr::after{content:"";position:absolute;left:1px;right:1px;top:4px;height:1px;background:#5a5446;transform:rotate(35deg)}
.s1{left:8px;top:8px}.s2{right:8px;top:8px}.s3{left:8px;bottom:8px}.s4{right:8px;bottom:8px}
.k{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:42px;padding:0 14px;background:linear-gradient(var(--panel-hi),#d6cebd);border:1px solid var(--seam2);border-radius:4px;
 box-shadow:0 3px 0 #8d8574,inset 0 1px 0 #fff;font:700 14px var(--lab);letter-spacing:.16em;text-transform:uppercase;text-decoration:none;color:var(--ink);cursor:pointer}
.k:hover,.k:focus-visible{background:linear-gradient(#fff3d9,var(--yel));outline:0}
.k:active{transform:translateY(2px);box-shadow:0 1px 0 #8d8574}
.k.go{background:linear-gradient(#ff7a3d,var(--org));box-shadow:0 3px 0 #7a2c0f,0 0 16px #ff7a3d55}
.k.ind{background:var(--ind);color:#fff;box-shadow:0 3px 0 #170a52;border-color:#170a52}
.k.ind:hover,.k.ind:focus-visible{background:var(--red);border-color:var(--red)}
.lamp{display:inline-flex;align-items:center;gap:7px;font:600 11px var(--lab);letter-spacing:.16em;text-transform:uppercase}
.lamp i{width:12px;height:12px;border-radius:50%;background:radial-gradient(circle at 40% 35%,#dcffd2,var(--leaf) 55%,#2f7a3a);box-shadow:0 0 9px var(--leaf)}
.lamp.amb i{background:radial-gradient(circle at 40% 35%,#fff0c9,var(--amber) 55%,#a86a00);box-shadow:0 0 9px var(--amber)}
.stamp{display:inline-block;border:2.5px solid var(--red);color:var(--red);font:600 11px/1.2 var(--lab);letter-spacing:.12em;text-align:center;padding:7px 10px;text-transform:uppercase;transform:rotate(-4deg);background:#fff3}
.stamp b{display:block;font:900 20px/1 var(--head);letter-spacing:0}

/* broadcast bulletin (emergency broadcast) */
.bulletin{display:flex;align-items:stretch;background:var(--red);color:#fff;border-top:5px solid transparent;border-bottom:5px solid transparent;
 border-image:repeating-linear-gradient(-45deg,#fff 0 11px,var(--red) 11px 22px) 5;overflow:hidden}
.bulletin .tag{flex:none;background:#fff;color:var(--red);font:700 14px/1 var(--lab);letter-spacing:.2em;padding:9px 14px;display:flex;align-items:center;gap:9px}
.bulletin .tag i{width:9px;height:9px;border-radius:50%;background:var(--red);animation:blink 1.2s steps(2) infinite}
.crawl{white-space:nowrap;font:700 15px/34px var(--lab);letter-spacing:.14em;text-transform:uppercase;animation:crawl 46s linear infinite;padding-left:22px}
@keyframes crawl{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@keyframes blink{50%{opacity:.15}}

/* top bar: Meguri seal + console readouts + keys */
.top{position:sticky;top:0;z-index:30;display:flex;align-items:center;gap:14px;padding:8px 18px;border-radius:0;border-width:0 0 1px}
.seal{display:flex;align-items:center;gap:12px;text-decoration:none;padding-right:16px;border-right:1px solid var(--seam)}
.seal i{width:44px;height:44px;border:3px solid var(--red);outline:1px solid var(--red);outline-offset:2px;color:var(--red);display:grid;place-items:center;font:normal 900 16px var(--head);background:var(--cream)}
.seal b{font:800 19px/1 var(--disp);font-stretch:118%}
.seal span{display:block;margin-top:4px}
.readouts{display:flex;gap:12px;align-items:center}
.ro{display:flex;flex-direction:column;gap:4px}
.ro .win{font-size:22px;min-width:96px;text-align:right}
.top nav{margin-left:auto;display:flex;gap:8px}

/* hero: theatre poster with dated border; Trailhead widgets on the right */
.sheet{display:grid;grid-template-columns:86px minmax(0,1fr) 300px;border-bottom:3px solid var(--ink)}
.dates{background:var(--cream);display:flex;flex-direction:column;border-right:3px solid var(--ink)}
.dates div{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;border-bottom:2px solid var(--ink);padding:8px 4px;font:700 11px/1.15 var(--lab);letter-spacing:.08em;text-transform:uppercase}
.dates div b{font:800 26px/1 var(--disp);font-stretch:112%;color:var(--red)}
.dates div:last-child{border-bottom:0}
.dates div.hot{background:var(--red);color:var(--cream)}.dates div.hot b{color:var(--yel)}
.stage{position:relative;overflow:hidden;padding:30px 34px 30px;background:var(--yel);min-height:600px}
.sun{position:absolute;right:-4%;bottom:-18%;width:52%;aspect-ratio:1;border-radius:50%;background:repeating-radial-gradient(circle,var(--org) 0 9px,transparent 9px 24px);opacity:.3}
.arc{position:absolute;left:-8%;bottom:-30%;width:60%;aspect-ratio:1;border-radius:50%;background:var(--teal);opacity:.16}
.kick{position:relative;z-index:2;display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 14px}
.kick .lab{background:var(--ink);color:var(--yel);padding:6px 9px}
.name{position:relative;z-index:2;max-width:66%;margin:0;font-family:var(--disp);font-weight:800;font-size:clamp(3.6rem,8.6vw,8.4rem);line-height:.86;text-transform:uppercase;color:var(--ind);
 font-stretch:var(--w,118%);letter-spacing:-.005em;text-shadow:5px 5px 0 var(--cream);transition:font-stretch .3s}
.name span{display:block}.name .o{color:var(--red)}
.ribbon{position:relative;z-index:2;display:inline-block;background:var(--red);color:var(--cream);font:800 clamp(1.2rem,2.3vw,1.9rem)/1 var(--disp);font-stretch:112%;text-transform:uppercase;
 padding:10px 16px;transform:rotate(-2deg);margin:18px 0 0;box-shadow:6px 6px 0 var(--ind)}
.lede{position:relative;z-index:2;max-width:38ch;font-size:1.08rem;margin:20px 0 18px;background:var(--cream);padding:12px 16px;border:2px solid var(--ink);box-shadow:4px 4px 0 var(--ink)}
.cta{position:relative;z-index:2;display:flex;flex-wrap:wrap;gap:10px}
.portrait{position:absolute;right:4%;top:34px;width:min(31%,370px);z-index:1;margin:0}
.portrait .ph{position:relative;aspect-ratio:1;border-radius:50%;overflow:hidden;border:4px solid var(--ink);box-shadow:10px 10px 0 var(--ind)}
.portrait img{width:100%;height:100%;object-fit:cover;filter:grayscale(1) contrast(1.4) brightness(1.08);transition:filter .4s}
.portrait .ph::after{content:"";position:absolute;inset:0;background:radial-gradient(circle,var(--ind) 30%,transparent 33%) 0 0/6px 6px;mix-blend-mode:screen;opacity:.85;transition:opacity .4s}
.portrait .ph::before{content:"";position:absolute;inset:0;background:var(--ind);mix-blend-mode:lighten;z-index:1;transition:opacity .4s}
.portrait:hover img{filter:none}.portrait:hover .ph::after,.portrait:hover .ph::before{opacity:0}
.portrait .stamp{position:absolute;left:-14px;top:12%;z-index:3;transform:rotate(-8deg)}
.widgets{background:var(--cream);border-left:3px solid var(--ink);display:flex;flex-direction:column}
.wd{border-bottom:2px solid var(--ink)}
.wd:last-child{border-bottom:0;flex:1}
.wh{display:flex;justify-content:space-between;align-items:center;padding:9px 14px;border-bottom:1.5px solid var(--ink)}
.wb{padding:12px 14px;font-size:.92rem;line-height:1.45}
.wb b{display:block;font:900 1.05rem/1.2 var(--head)}
.wb + .wb{border-top:1px dashed #1d173655}
.clock{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 14px}
.clock .win{font-size:34px}

/* six-pack */
.six{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;padding:24px 26px;margin:26px 26px 0}
.gauge{margin:0;text-align:center}
.gauge svg{width:100%;max-width:150px}
.gauge .bez{fill:#1b1a17;stroke:#5c564a;stroke-width:2}.gauge .face{fill:#121110}.gauge .tk line{stroke:#e9e3d6;stroke-width:1.2}
.gauge .gl{fill:#b9ad92;font:600 7px var(--lab);letter-spacing:.14em;text-anchor:middle;text-transform:uppercase}
.gauge .gv{fill:var(--amber);font:400 15px var(--crt);text-anchor:middle}
.gauge .gu{fill:#b9ad92;font:600 5.5px var(--lab);letter-spacing:.12em;text-anchor:middle}
.gauge .needle{transform-origin:50px 50px;transform:rotate(calc(var(--a) + 90deg));transition:transform 1.6s cubic-bezier(.3,1.4,.5,1)}
.gauge .needle path{stroke:var(--leaf);stroke-width:2.4;stroke-linecap:round}.gauge .needle circle{fill:#d9d2c0}
.gauge.zero .needle{transform:rotate(-135deg)}
.gauge figcaption{font:600 12px/1.3 var(--lab);letter-spacing:.12em;text-transform:uppercase;color:var(--engrave);margin-top:6px}

/* flagship: Meguri edition + console screen + broadcast arrow */
.wrap{max-width:1440px;margin:0 auto;padding:0 0 100px}
.sec-h{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;margin:64px 26px 22px;padding-top:16px;border-top:3px solid var(--ink)}
.sec-h h2{font:900 clamp(2.4rem,4.6vw,4rem)/.95 var(--head);margin:0}
.sec-h p{margin:0;text-align:right}
.flag{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.3fr);gap:0;margin:0 26px;border:3px solid var(--ink);background:var(--cream);position:relative}
.flag .ed{padding:28px;border-right:3px solid var(--ink);display:flex;flex-direction:column}
.flag .ed h3{font:900 2.3rem/1 var(--head);margin:10px 0}
.flag .res{display:flex;gap:10px;align-items:center;margin:6px 0 14px}
.flag .res .win{font-size:34px}
.flag .ed p{margin:0 0 12px}
.flag .tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:0;margin-top:auto;border-top:2px solid var(--ink)}
.flag .tiles a{display:block;text-decoration:none;padding:10px 10px 0;border-right:2px solid var(--ink)}
.flag .tiles a:last-child{border-right:0}
.flag .tiles img{width:100%;aspect-ratio:1.3;object-fit:cover;margin-top:6px;border:1.5px solid var(--ink)}
.flag .tiles b{font:900 .98rem/1.1 var(--head);display:block}
.flag .tiles a:hover b,.flag .tiles a:focus-visible b{color:var(--red)}
.flag .mon{padding:14px;background:var(--panel);position:relative}
.screen{background:#0d0c0b;border-radius:10px;padding:10px;box-shadow:inset 0 0 0 3px #2a2722;height:100%;min-height:500px;position:relative}
.screen iframe{border:0;position:absolute;inset:10px;width:calc(100% - 20px);height:calc(100% - 20px);border-radius:6px;background:#fff}
.arrow{display:flex;align-items:center;gap:8px;justify-content:flex-end;margin:-8px -8px 0 0}
.arrow svg{width:84px;height:48px;filter:drop-shadow(3px 3px 0 var(--ink))}

/* playbill of projects */
.bill{list-style:none;margin:0 26px;padding:0;display:grid;grid-template-columns:repeat(4,1fr);border-top:3px solid var(--ink);border-left:3px solid var(--ink)}
.bill li{position:relative;border-right:3px solid var(--ink);border-bottom:3px solid var(--ink);background:var(--cream);padding:14px 16px 16px;display:flex;flex-direction:column}
.bill li:nth-child(4n+2){background:#FFF0C2}.bill li:nth-child(4n+3){background:#F3E7CF}
.bill .k1{display:flex;justify-content:space-between;align-items:center}
.bill .bay{background:#fbf7ec;border:1.5px solid var(--ink);margin:10px 0;padding:4px}
.bill .icon{display:block;width:76%;margin:0 auto;aspect-ratio:1}
.bill h3{font:800 1.28rem/1 var(--disp);font-stretch:108%;text-transform:uppercase;margin:4px 0 6px}
.bill h3 button{all:unset;cursor:pointer}.bill h3 button::after{content:"";position:absolute;inset:0}
.bill h3 button:focus-visible{outline:4px solid var(--red);outline-offset:4px}
.bill .m{font-size:.85rem;margin:0 0 10px;color:#3d365a}
.bill .rr{margin-top:auto;display:flex;justify-content:space-between;align-items:center;gap:8px}
.bill .rr .win{font-size:20px}
.bill li:hover,.bill li:focus-within{background:var(--yel)}
.bill li.lead{grid-column:span 2;grid-row:span 2;background:var(--org)}
.bill li.lead .icon{width:64%}.bill li.lead h3{font-size:2.3rem}.bill li.lead .m{color:var(--ink);font-size:1rem}

/* coursework terminal (Nostromo) */
.term{margin:0 26px;background:var(--win);border-radius:10px;box-shadow:inset 0 0 0 3px #2a2722;padding:20px 24px;color:var(--amber);font:400 22px/1.35 var(--crt);text-shadow:0 0 6px #ffb22e55}
.term ul{list-style:none;margin:0;padding:0;columns:2;column-gap:40px}
.term li{break-inside:avoid;padding:3px 0}
.term a{text-decoration:none;display:grid;grid-template-columns:110px 1fr}
.term a:hover,.term a:focus-visible{background:var(--amber);color:var(--win);text-shadow:none;outline:0}
.term .hd{color:var(--leaf);margin:0 0 10px}

/* about: Meguri studio + service record */
.studio{display:grid;grid-template-columns:1.35fr 1fr;gap:26px;margin:0 26px}
.studio .txt{background:var(--cream);border:3px solid var(--ink);padding:26px 30px}
.studio .txt p{margin:0 0 13px}
.studio .rec{padding:24px 26px}
.rec table{width:100%;border-collapse:collapse;font-size:.92rem}
.rec td{border-top:1px solid var(--seam);padding:8px 4px;vertical-align:top}
.rec td:first-child{font:600 13px var(--lab);letter-spacing:.08em;white-space:nowrap;color:var(--engrave)}
.rec b{display:block;font:900 1rem var(--head)}
.chips{display:flex;flex-wrap:wrap;gap:7px;margin:10px 0 0}
.chips span{font:600 12px var(--lab);letter-spacing:.1em;text-transform:uppercase;border:1.5px solid var(--ink);padding:5px 8px;background:var(--paper)}
.tx{margin:64px 26px 0;padding:36px;display:flex;align-items:center;gap:22px;flex-wrap:wrap;background:var(--ind);color:var(--cream);border:8px solid;border-image:repeating-linear-gradient(-45deg,var(--yel) 0 14px,var(--ink) 14px 28px) 8}
.tx h2{font:800 clamp(2.2rem,4.6vw,4rem)/1 var(--disp);font-stretch:125%;text-transform:uppercase;margin:0;color:var(--yel);flex:1 1 360px}

/* project file dialog (console monitor) */
dialog.file{width:min(1240px,calc(100vw - 24px));max-height:calc(100vh - 24px);padding:12px;border:0;border-radius:12px;background:#2B2823;overflow:auto}
dialog.file::backdrop{background:#1d1736b0}
.file .inner{display:grid;grid-template-columns:minmax(260px,390px) 1fr;gap:12px}
.file .side{padding:24px;background:var(--cream);border:3px solid var(--ink);border-radius:3px}
.file h3{font:900 2rem/1.02 var(--head);margin:8px 0}
.file .win{font-size:24px;margin:4px 0 12px}
.file .scr2{background:#0d0c0b;border-radius:10px;padding:10px;min-height:560px;position:relative}
.file .scr2 iframe,.file .scr2 img{position:absolute;inset:10px;width:calc(100% - 20px);height:calc(100% - 20px);border:0;border-radius:6px;background:#fff;object-fit:contain}
.file dl{margin:10px 0;font-size:.9rem}.file dl div{border-top:1px solid #1d173633;padding:6px 0}
.file dt{font:600 12px var(--lab);letter-spacing:.14em;text-transform:uppercase;color:var(--engrave)}.file dd{margin:0}
.file .bar{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap}

@media (max-width:1200px){.sheet{grid-template-columns:70px minmax(0,1fr)}.widgets{grid-column:1/-1;border-left:0;border-top:3px solid var(--ink);display:grid;grid-template-columns:repeat(3,1fr)}
 .wd{border-bottom:0;border-right:2px solid var(--ink)}.six{grid-template-columns:repeat(3,1fr)}.bill{grid-template-columns:repeat(3,1fr)}.readouts .ro:nth-child(2){display:none}}
@media (max-width:900px){.flag,.studio,.file .inner{grid-template-columns:1fr}.flag .ed{border-right:0;border-bottom:3px solid var(--ink)}.arrow{display:none}.screen{min-height:420px}
 .bill{grid-template-columns:repeat(2,1fr)}.readouts{display:none}.portrait{position:relative;right:auto;top:auto;width:70%;max-width:340px;margin:26px auto 0}.name{max-width:none}}
@media (max-width:640px){.top{flex-wrap:wrap;gap:8px;padding:8px 10px}.seal{border:0;padding:0}.seal i{width:36px;height:36px;font-size:13px}.seal b{font-size:16px}.seal span{display:none}
 .top nav{margin:0;width:100%;overflow-x:auto}.top nav .k{min-height:34px;font-size:12px;padding:0 9px;letter-spacing:.1em}
 .sheet{grid-template-columns:1fr}.dates{display:none}.stage{padding:22px 16px;min-height:0}.widgets{grid-template-columns:1fr}.wd{border-right:0;border-bottom:2px solid var(--ink)}
 .six{grid-template-columns:repeat(2,1fr);margin:18px 12px 0;padding:16px}.sec-h{margin:48px 12px 16px;flex-direction:column;align-items:flex-start}.sec-h p{text-align:left}
 .flag,.bill,.term,.studio{margin-left:12px;margin-right:12px}.bill{grid-template-columns:1fr}.bill li.lead{grid-column:auto;grid-row:auto}.bill li.lead h3{font-size:1.8rem}
 .term ul{columns:1}.term a{grid-template-columns:1fr}.tx{margin:48px 12px 0;padding:24px}.flag .tiles{grid-template-columns:1fr 1fr 1fr}.file .scr2{min-height:380px}.crawl{font-size:13px}}
@media (prefers-reduced-motion:reduce){.crawl{animation:none;white-space:normal;line-height:1.4;padding:6px 14px}.bulletin .tag i{animation:none}.gauge .needle,.name{transition:none}}
"""


def merged():
    scr = '<span class="scr s1"></span><span class="scr s2"></span><span class="scr s3"></span><span class="scr s4"></span>'
    t = MAIN[0]
    years = [('2022', 'First build'), ('2023', 'Research'), ('2024', 'UQ Space'), ('2025', 'Errol'), ('2026', '1st of 17'), ('2027', 'Graduate')]
    dates = ''.join(f'<div{" class=hot" if y == "2026" else ""}><b>{y[2:]}</b>{e(w)}</div>' for y, w in years)
    crawl = ' ★ '.join(['On air', 'Available for 2027 graduate roles and internships', 'Avionics and embedded systems',
                        'Robotics and autonomy', 'Guidance, navigation and control', 'Theseus V: 1st of 17, ARC 2026',
                        'HAVOC-2 first flight: about 540 m, every frame passed']).upper()
    six = (gauge('Rover rank', '1st', 1.0, 'OF 17', 'ARC 2026') + gauge('Apogee', '540', 540 / 600, 'METRES', 'HAVOC-2') +
           gauge('DRC faults', '0', 0.0, 'OSIRIS V0', 'KiCad checks') + gauge('Sim flights', '200', 200 / 250, 'AIRBRAKES', '4 controllers') +
           gauge('Rows OK', '98,218', 0.99, 'WX STATION', 'All passed') + gauge('Lighter', '21%', 0.21 / 0.3, 'CRANK ARM', 'Ti, printed'))
    status = {'osiris': ('On bench', 'amb'), 'digital-orrery': ('Live', '')}
    bill = []
    for i, p in enumerate(P):
        st, cls = status.get(p['slug'], (p['short'][2].title(), ''))
        bill.append(f"""<li class="card{' lead' if i == 0 else ''}"><div class="k1"><span class="lab">No. {i + 1:02d} · {e(YEAR[p['slug']])}</span><span class="lamp {cls}"><i></i>{e(st)}</span></div>
<div class="bay">{p['icon']}</div><h3><button type="button" data-open="{p['slug']}">{e(p['title'])}</button></h3><p class="m">{e(p['outcome'] if i == 0 else p['meta'])}</p>
<div class="rr"><span class="win">{e(p['short'][1])}</span></div></li>""")
    term = ''.join(f'<li><a href="{c["href"]}"><span>{e(c["meta"].split(" · ")[0])}</span><span>{e(c["title"].upper())}</span></a></li>' for c in D['coursework'])
    rec = ''.join(f'<tr><td>{e(w)}</td><td><b>{e(r)}</b>{e(o)}</td></tr>' for r, o, w in D['experience'])
    body = fill("""<div class="bulletin" role="region" aria-label="Availability"><span class="tag"><i></i>ON AIR</span><div class="crawl" aria-hidden="true">@@CRAWL@@ ★ @@CRAWL@@ ★ </div><span class="vh">@@CRAWL@@</span></div>
<header class="panel top">@@SCR@@<a class="seal" href="#top"><i>IJZ</i><span><b>Isaac Johan Ziebarth</b><span class="eng">Mechatronic engineering · UQ</span></span></a>
<div class="readouts"><div class="ro"><span class="eng">Brisbane</span><span class="win" id="clock">--:--</span></div><div class="ro"><span class="eng">To graduation</span><span class="win" id="tminus">T-000 D</span></div></div>
<nav aria-label="Main"><a class="k" href="#work">Projects</a><a class="k" href="#coursework">Coursework</a><a class="k" href="#about">About</a><a class="k go" href="#contact">Contact</a></nav></header>
<main id="main" class="wrap">
<section class="sheet" id="top" aria-labelledby="me"><div class="dates" aria-label="Timeline">@@DATES@@</div>
<div class="stage" id="stage"><div class="sun" aria-hidden="true"></div><div class="arc" aria-hidden="true"></div>
<p class="kick"><span class="lab">Engineering portfolio</span><span class="lamp"><i></i>Seeking 2027 roles</span></p>
<h1 class="name" id="me"><span>Isaac</span><span>Johan</span><span class="o">Ziebarth</span></h1>
<p class="ribbon">Flight software · Autonomy · Boards</p>
<p class="lede">I write robot and flight software, design the boards it runs on and build the ground stations that read it back. Graduating from UQ in 2027.</p>
<div class="cta"><a class="k ind" href="#work">See the work</a><a class="k go" href="mailto:@@EMAIL@@">Email me</a><a class="k" href="@@LI@@">LinkedIn</a><a class="k" href="@@GH@@">GitHub</a></div>
<figure class="portrait"><div class="ph"><img src="/assets/img/profile.jpg" alt=""></div><span class="stamp"><b>1st of 17</b>ARC 2026</span></figure></div>
<aside class="widgets" aria-label="Status">
<div class="wd"><div class="wh"><span class="lab">Today</span><span class="lab">Brisbane</span></div><div class="clock"><span class="win" id="clock2">--:--</span><span class="lab" id="date"></span></div></div>
<div class="wd"><div class="wh"><span class="lab">Now</span><span class="lamp"><i></i>Nominal</span></div>
<div class="wb"><b>Research assistant</b>PX4 flight control and modelling, UQ School of EECS</div>
<div class="wb"><b>Avionics engineer, UQ Space</b>Ground stations, PCBs and the Theseus VI autonomy stack</div></div>
<div class="wd"><div class="wh"><span class="lab">Next up</span><span class="lab">2027</span></div>
<div class="wb"><b>Graduating November 2027</b>BE(Hons)/ME, mechatronics. Open to internships and graduate roles in avionics, autonomy and GNC.</div>
<div class="wb"><a class="k go" style="width:100%" href="#contact">Get in touch</a></div></div></aside></section>
<section class="panel six" aria-label="Results at a glance">@@SCR@@@@SIX@@</section>
<div class="sec-h" id="flagship"><h2>Current edition</h2><p class="lab">Flagship · @@T_YEAR@@</p></div>
<section class="flag" aria-labelledby="fh">
<div class="ed"><div class="arrow" aria-hidden="true"><span class="lab" style="color:var(--red)">Live arena map</span><svg viewBox="0 0 110 64"><path d="M2 32 H76" stroke="#BB0700" stroke-width="18"/><path d="M68 4 L108 32 L68 60 Z" fill="#BB0700"/></svg></div><span class="eng">@@T_META@@</span><h3 id="fh">@@T_TITLE@@</h3><div class="res"><span class="win">1ST OF 17</span><span class="stamp" style="transform:rotate(3deg)"><b>Placed</b>ARC 2026</span></div>
<p>@@T_OUT@@</p><div class="cta" style="margin-bottom:18px"><a class="k ind" href="@@T_HREF@@">Read the write-up</a><button class="k" type="button" data-open="@@T_SLUG@@">Open file</button></div>
<div class="tiles"><a href="/projects/theseus.html"><span class="lab">Map</span><b>FAST-LIO2 cloud</b><img src="/assets/figures/theseus-map-cloud.webp" alt="" style="object-position:40% 40%"></a>
<a href="/projects/havoc2-cosmos.html"><span class="lab">Flight data</span><b>540 m, logged</b><img src="/assets/img/projects/havoc2-share.jpg" alt="" style="object-position:0 0"></a>
<a href="/projects/osiris.html"><span class="lab">Board</span><b>OSIRIS V0</b><img src="/assets/img/projects/osiris-v0-top.jpg" alt=""></a></div></div>
<div class="mon">@@SCR@@<div class="screen"><iframe src="@@T_FIG@@" title="Live figure: @@T_TITLE@@"></iframe></div></div></section>
<div class="sec-h" id="work"><h2>The playbill</h2><p class="lab">@@NP@@ projects · open one for its live figure</p></div>
<ul class="bill">@@BILL@@</ul>
<div class="sec-h" id="coursework"><h2>Training record</h2><p class="lab">Coursework · @@NC@@ graded reports</p></div>
<div class="term"><p class="hd">&gt; QUERY COURSEWORK --ALL ... @@NC@@ RECORDS</p><ul>@@TERM@@</ul></div>
<div class="sec-h" id="about"><h2>The engineer</h2><p class="lab">About · service record</p></div>
<div class="studio"><div class="txt">@@BIO@@<div class="chips">@@CHIPS@@</div></div>
<section class="panel rec" aria-label="Service record">@@SCR@@<span class="eng">Service record</span><table>@@REC@@</table><p style="font-size:.88rem;margin-top:12px">@@EDU@@</p></section></div>
<section class="tx" id="contact" aria-labelledby="txh"><h2 id="txh">Open a channel.</h2><a class="k go" href="mailto:@@EMAIL@@">Email me</a><a class="k" href="@@LI@@">LinkedIn</a><a class="k" href="@@GH@@">GitHub</a></section>
</main>
<dialog class="file" aria-labelledby="f-title"><div class="inner"><div class="side"><span class="eng" id="f-meta"></span><h3 id="f-title"></h3><span class="win" id="f-res"></span>
<p id="f-out"></p><div id="f-facts"></div><div class="bar"><a class="k ind" id="f-full" href="#">Full write-up</a><button class="k" type="button" id="f-prev">Prev</button><button class="k" type="button" id="f-next">Next</button><button class="k" type="button" id="f-close">Close</button></div></div>
<div class="scr2" id="f-live"></div></div></dialog>""", CRAWL=e(crawl), SCR=scr, EMAIL=D['email'], LI=D['linkedin'], GH=D['github'], DATES=dates, SIX=six,
                T_YEAR=e(YEAR[t['slug']]), T_META=e(t['meta']), T_TITLE=e(t['title']), T_OUT=e(t['outcome']), T_HREF=t['href'], T_SLUG=t['slug'],
                T_FIG=t['figure'], NP=len(P), BILL=''.join(bill), NC=len(D['coursework']), TERM=term, BIO=bio(4),
                CHIPS=''.join(f'<span>{x}</span>' for x in TOOLS), REC=rec, EDU=e(D['edu']))
    js = """
const tick=()=>{ const d=new Date(); const hm=d.toLocaleTimeString('en-AU',{hour:'2-digit',minute:'2-digit',hour12:false,timeZone:'Australia/Brisbane'});
 document.getElementById('clock').textContent=hm; document.getElementById('clock2').textContent=hm;
 document.getElementById('date').textContent=d.toLocaleDateString('en-AU',{weekday:'short',day:'numeric',month:'short',timeZone:'Australia/Brisbane'});
 const days=Math.ceil((new Date('2027-11-30T00:00:00+10:00')-d)/864e5); document.getElementById('tminus').textContent='T-'+String(days).padStart(3,'0')+' D'; };
tick(); setInterval(tick,20000);
const gs=[...document.querySelectorAll('.gauge')]; if(!RM){ gs.forEach(g=>g.classList.add('zero'));
 const io=new IntersectionObserver(es=>es.forEach(x=>{ if(x.isIntersecting){ setTimeout(()=>x.target.classList.remove('zero'),150); io.unobserve(x.target);} }),{threshold:.5}); gs.forEach(g=>io.observe(g)); }
// variable-font specimen: the name's width axis follows the pointer across the poster
const stage=document.getElementById('stage'), nm=document.getElementById('me');
if(!RM && matchMedia('(pointer:fine)').matches){ stage.addEventListener('pointermove',ev=>{ const r=stage.getBoundingClientRect(); const f=(ev.clientX-r.left)/r.width;
 nm.style.setProperty('--w',(75+f*50).toFixed(0)+'%'); }); stage.addEventListener('pointerleave',()=>nm.style.removeProperty('--w')); }
const dlg=document.querySelector('dialog.file'); let cur=0;
function show(i){ cur=(i+PROJ.length)%PROJ.length; const p=PROJ[cur];
 document.getElementById('f-meta').textContent=p.meta; document.getElementById('f-title').textContent=p.title;
 document.getElementById('f-res').textContent=p.result.toUpperCase(); document.getElementById('f-out').textContent=p.outcome;
 document.getElementById('f-facts').innerHTML=factsHTML(p); document.getElementById('f-live').innerHTML=figureHTML(p); document.getElementById('f-full').href=p.href; }
document.querySelectorAll('[data-open]').forEach(b=>b.addEventListener('click',()=>{ show(PROJ.findIndex(p=>p.slug===b.dataset.open)); dlg.showModal(); }));
document.getElementById('f-prev').onclick=()=>show(cur-1); document.getElementById('f-next').onclick=()=>show(cur+1);
document.getElementById('f-close').onclick=()=>dlg.close(); dlg.addEventListener('close',()=>document.getElementById('f-live').innerHTML='');
"""
    fonts = 'family=Archivo:wdth,wght@62..125,700..800&family=Barlow+Condensed:wght@600;700&family=VT323'
    return B.page('Isaac Johan Ziebarth · Merged', fonts, CSS, body, js)


if __name__ == '__main__':
    out = HERE / 'merged.html'
    out.write_text(merged().replace('<a href="merged.html">', '<a href="merged.html" aria-current="page">', 1))
    print(out.name, f'{out.stat().st_size / 1024:.0f} KB')
    # refresh the other studies so their switchers list the merged page too
    for fn in (B.trailhead, B.meguri, B.console, B.poster):
        h, name = fn()
        (HERE / f'{name}.html').write_text(h.replace(f'<a href="{name}.html">', f'<a href="{name}.html" aria-current="page">', 1))
