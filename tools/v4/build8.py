"""Prototype project pages + card-to-page view transitions (19 Nov 2026).

Writes vt/<slug>.html for the 11 projects (the architecture plan's page template: breadcrumb, icon hero, type line,
result, live figure, write-up outline, next-project link, five-item header) and live4-vt.html: Live v4 with each card
title turned into a real link to its page. Navigation uses native cross-document view transitions
(@view-transition { navigation: auto }): the clicked card's icon and title are named on `pageswap`, the project
page names its hero the same way, so the browser morphs one into the other; `pagereveal` names the matching card on
the way back. Browsers without support just navigate. Run from the repo root: python3 -I .impeccable/mocks/proto/build8.py
"""
import html
import html as H
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import content as C  # noqa: E402

E = html.escape
ORDER = ['theseus', 'havoc2-cosmos', 'osiris', 'airbrakes', 'digital-orrery', 'weather-station', 'errol',
         'metr4810', 'camera-mount', 'engg1100']   # crank-arm is coursework only (19 Nov 2026)
D = C.load()
P = {p['slug']: p for p in D['projects']}
HOME = '../live4-vt.html'

VT_CSS = """
@view-transition { navigation: auto; }
/* Morph timing: the hero icon and title travel on the house ease-out; the rest of the page crossfades quickly. */
::view-transition-group(hero-icon), ::view-transition-group(hero-title) { animation-duration: 420ms; animation-timing-function: cubic-bezier(0.23, 1, 0.32, 1); }
::view-transition-old(root), ::view-transition-new(root) { animation-duration: 200ms; }
::view-transition-old(hero-title), ::view-transition-new(hero-title) { height: 100%; width: auto; object-fit: contain; object-position: left center; }
/* Titles differ in size and wrap, so a crossfade ghosts: drop the old snapshot and scale the new one from the card. */
::view-transition-old(hero-title) { display: none; }
::view-transition-new(hero-title) { animation: none; }
@media (prefers-reduced-motion: reduce) { ::view-transition-group(*), ::view-transition-old(*), ::view-transition-new(*) { animation: none !important; } }
"""

PAGE_CSS = VT_CSS + """
@font-face{font-family:Fraunces;src:url(/assets/fonts/fraunces-900-latin.woff2) format("woff2");font-weight:900;font-display:swap}
@font-face{font-family:Sanchez;src:url(/assets/fonts/sanchez-400-latin.woff2) format("woff2");font-weight:400;font-display:swap}
:root{--paper:#ECEAE4;--paper2:#E1DED5;--panel:#F5F4F0;--cream:#FFF7DA;--ink:#1E2126;--mute:#5D626B;--ind:#2E1499;--red:#BB0700;--yel:#FFC908;--org:#FF5102;--leaf:#3E9B5F;
  --head:'Chivo Mono',ui-monospace,monospace;--body:Sanchez,Georgia,serif;--mono:'Chivo Mono',ui-monospace,monospace;
  --stripe:linear-gradient(90deg,var(--yel) 0 20%,var(--org) 20% 40%,var(--red) 40% 60%,var(--ind) 60% 80%,var(--leaf) 80%)}
*{box-sizing:border-box}
html{background:var(--paper);color:var(--ink);font:400 17px/1.6 var(--body)}
body{margin:0}
a{color:var(--ind)}
.vh{position:absolute;left:-9999px}.vh:focus{left:12px;top:12px;z-index:9;background:var(--yel);color:var(--ink);padding:8px 12px}
header.top{position:sticky;top:0;z-index:5;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:0 28px;height:56px;background:var(--panel);border-bottom:2px solid var(--ink)}
header.top .nm{display:flex;align-items:center;gap:12px;font:700 1.1rem var(--head);letter-spacing:.01em;text-transform:uppercase;color:var(--ink);text-decoration:none}
header.top .mk{display:grid;place-items:center;width:30px;height:30px;border:2px solid var(--ink);font:700 11px var(--mono)}
header.top nav{display:flex;gap:2px}
header.top nav a{font:600 13px var(--mono);color:var(--mute);text-decoration:none;padding:8px 10px}
header.top nav a:hover,header.top nav a[aria-current]{color:var(--ink);background:var(--paper2)}
.stripe{height:6px;background:var(--stripe)}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px 80px}
.crumbs ol{list-style:none;display:flex;flex-wrap:wrap;gap:8px;margin:22px 0 26px;padding:0;font:600 12px var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--mute)}
.crumbs li+li::before{content:"›";margin-right:8px}
.crumbs a{color:var(--mute);text-decoration:none}.crumbs a:hover{color:var(--ink);text-decoration:underline}
.crumbs [aria-current]{color:var(--ink)}
.panel{position:relative;background:var(--panel);border:2px solid var(--ink);box-shadow:6px 6px 0 var(--ink)}
.panel::before{content:"";position:absolute;left:-2px;right:-2px;top:-2px;height:6px;background:var(--stripe)}
.hero{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:40px;align-items:start}
.hero.solo{grid-template-columns:1fr}
.hero-ic{background:var(--cream);aspect-ratio:1;display:grid;place-items:center}
.hero-ic .icon{display:block;width:84%;aspect-ratio:1}
.hero-ic .ic-bg,.next .ic-bg{fill:#FFF7DA}   /* icons.css only fills it inside .card */
.type{font:600 13px var(--mono);color:var(--mute);margin:6px 0 10px}
h1{font:900 clamp(2.4rem,4.6vw,4rem)/.98 Fraunces,Georgia,serif;letter-spacing:-.01em;margin:0 0 14px;width:fit-content}
.res{font:600 15px var(--mono);color:var(--red);margin:0 0 16px}
.out{margin:0 0 22px;max-width:60ch}
.facts{display:grid;grid-template-columns:auto 1fr;gap:6px 18px;margin:0;padding:16px 0 0;border-top:2px solid var(--ink)}
.facts dt{font:600 11px var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--mute);padding-top:3px}
.facts dd{margin:0}
.fig{margin-top:56px}
.bar{display:flex;justify-content:space-between;align-items:baseline;gap:16px;padding:16px 20px 12px;border-bottom:2px solid var(--ink)}
.bar b{font:700 1.1rem var(--head);text-transform:uppercase;letter-spacing:0}
.bar span{font:500 12px var(--mono);color:var(--mute)}
.fig iframe,.fig img{display:block;width:100%;height:min(72svh,640px);border:0;background:#fff;object-fit:contain}
.wu{margin-top:40px;padding:22px 24px 26px}
.wu h2{font:900 1.8rem/1 Fraunces,Georgia,serif;margin:4px 0 14px}
.wu ol{margin:0 0 20px;padding-left:1.3em;columns:2;column-gap:40px}
.wu .toc{margin:0 0 8px;padding:12px 0 14px 1.3em;border-bottom:2px solid var(--ink)}
.wu .body{max-width:880px}
.wu .prose h2{font:900 1.6rem/1.05 Fraunces,Georgia,serif;margin:34px 0 10px}
.wu .prose p,.wu .prose li{max-width:68ch}
.wu .prose .meta{font:600 13px var(--mono);color:var(--mute)}
.wu .figure{margin:26px 0;max-width:var(--fig-w,100%)}
.wu .figure img{display:block;max-width:100%;height:auto;border:2px solid var(--ink);background:#fff}
.wu .figure figcaption{font:500 13px/1.5 var(--mono);color:var(--mute);margin-top:8px;max-width:72ch}
.wu .figure-embed iframe{display:block;width:100%;aspect-ratio:var(--ratio,1.5);border:2px solid var(--ink);background:#fff}
.wu .figure-code pre{overflow:auto;background:var(--ink);color:#fff;padding:14px 16px;font:500 13px/1.5 var(--mono)}
.wu .embed-phone-note{display:none}
@media (max-width:700px){.wu .figure-embed[data-desktop-only] iframe{display:none}.wu .embed-phone-note{display:block}}
.cwidx{margin-top:44px}
.wu.cw .prose h2{border-top:2px solid var(--ink);padding-top:30px;margin-top:46px}.wu.cw .prose h2:first-child{border-top:0;padding-top:0;margin-top:10px}
.wu .old{margin:30px 0 0;font:500 12px var(--mono)}.wu .old a{color:var(--mute)}
.btn{display:inline-block;font:700 13px var(--head);text-transform:uppercase;letter-spacing:.04em;padding:12px 18px;border:2px solid var(--ink);background:var(--ind);color:#fff;text-decoration:none}
@media (hover:hover){.btn:hover{background:var(--ink)}}
.next{margin-top:56px}
.next a{display:flex;align-items:center;gap:20px;padding:18px 22px;text-decoration:none;color:var(--ink)}
.next .icon{width:84px;aspect-ratio:1;flex:none;background:var(--cream);border:2px solid var(--ink)}
.next small{display:block;font:600 12px var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--mute)}
.next b{font:900 1.5rem/1.1 Fraunces,Georgia,serif}
.next a:hover{background:var(--cream)}
footer{border-top:2px solid var(--ink);padding:22px 28px;font:500 12px var(--mono);color:var(--mute);background:var(--panel)}
@media (max-width:820px){.hero{grid-template-columns:1fr;gap:24px}.hero-ic{max-width:420px}.wu ol{columns:1}header.top nav a{padding:8px 5px;font-size:11px}header.top .nm{font-size:1rem}}
@media (max-width:520px){header.top{height:auto;flex-wrap:wrap;row-gap:2px;padding:8px 14px 6px}header.top nav{width:100%;overflow-x:auto;scrollbar-width:none;margin:0 -6px}header.top nav a{white-space:nowrap;padding:10px 7px;font-size:12px}}   /* phones: the links wrap onto a second row rather than disappear */
"""

NAV = [('Projects', HOME + '#projects'), ('Systems', HOME + '#systems'), ('Coursework', 'coursework.html'),
       ('About', HOME + '#about'), ('Contact', HOME + '#contact')]

ARCHIVE = '/.impeccable/mocks/archive-live'   # the old live site, unpacked from origin/main 9b79ef3 (19 Nov 2026)


# Fit the lead figure to its content; site.js fits the embedded figures and loads desktop-only frames on wide screens.
FIT_JS = """<script>
// The lead figure's frame takes its figure's whole height, and keeps taking it as the figure grows (a solver that fills in
// a table, fonts arriving), so it never shows a scrollbar of its own (Isaac, 19 Nov 2026), and shrinks to a short one so
// no blank box sits under it. Embedded figures further down are fitted by site.js. Frames stop after 40 resizes so a
// figure sized in vh units cannot chase its own frame; one still growing then gets its scrollbar back, never cut off.
document.querySelectorAll('.fig.panel iframe').forEach(f => {
  let n = 0;
  const fit = () => { try { const d = f.contentDocument, r = d.documentElement; if (!d.body) return; r.style.overflow = 'hidden';
    const bm = parseFloat(getComputedStyle(d.body).marginTop) + parseFloat(getComputedStyle(d.body).marginBottom);
    const h = Math.ceil(Math.max(d.body.scrollHeight, d.body.getBoundingClientRect().height) + bm);   // the figure's own height, up or down
    if (Math.abs(h - f.clientHeight) > 1 && h > 120) { if (n++ < 40) { f.style.height = h + 'px'; f.style.aspectRatio = 'auto'; } else r.style.overflow = ''; } } catch (e) {} };
  const hook = () => { fit(); try { const d = f.contentDocument, ro = new ResizeObserver(fit); ro.observe(d.documentElement); ro.observe(d.body); if (d.fonts) d.fonts.ready.then(fit); } catch (e) {} };
  f.addEventListener('load', hook); try { if (f.contentDocument && f.contentDocument.readyState === 'complete' && f.contentDocument.URL !== 'about:blank') hook(); } catch (e) {}
});
</script>"""

def lead_desktop_only(slug):
    """True when the live page's lead figure only loads on wide screens (a full app); the new page then keeps that
    figure, with its phone note, instead of putting it in the eager figure panel."""
    s = (C.ROOT / 'projects' / f'{slug}.html').read_text()
    m = re.search(r'<figure\b[^>]*>', s[s.index('<main'):])
    return bool(m and 'data-desktop-only' in m.group(0))


def body_of(slug):
    """The live page's write-up (everything after its facts and on-page nav), for the new page: the lead figure is
    dropped (the figure panel above shows it), paths made absolute, and the scroll-reveal class removed."""
    s = (C.ROOT / 'projects' / f'{slug}.html').read_text()
    m = s[s.index('<main'):s.index('</main>')]
    i = m.find('class="on-page"')
    body = m[m.index('</nav>', i) + 6:] if i > 0 else m[m.index('</dl>') + 5:]
    if slug != 'coursework' and not lead_desktop_only(slug):   # a desktop-only lead (Errol's replay app) stays in the write-up
        body = re.sub(r'^\s*<figure\b.*?</figure>', '', body, count=1, flags=re.S)
    body = re.sub(r'<nav class="page-nav".*?</nav>', '', body, flags=re.S)   # the new page has its own next-project panel
    body = (body.replace('../assets/', '/assets/').replace('../lichtblick/', '/lichtblick/')
            .replace('href="../index.html', f'href="{HOME}').replace(' reveal"', '"'))
    return body


def head_of(slug):
    """Title, meta line, outcome and facts straight from the live page (for pages content.py doesn't cover)."""
    s = (C.ROOT / 'projects' / f'{slug}.html').read_text()
    g = lambda pat: re.search(pat, s, re.S).group(1).strip()
    facts = re.findall(r'<dt>(.*?)</dt><dd>(.*?)</dd>', g(r'<dl class="facts">(.*?)</dl>'))
    return {'title': g(r'<h1>(.*?)</h1>'), 'meta': g(r'<p class="meta">(.*?)</p>'), 'outcome': g(r'<p class="outcome">(.*?)</p>'), 'facts': facts}


def coursework():
    """The coursework page isn't a project card, so content.py doesn't carry it: take its head from the live page."""
    h = head_of('coursework')
    s = (C.ROOT / 'projects' / 'coursework.html').read_text()
    secs = [re.sub(r'<[^>]+>', '', t) for t in re.findall(r'<h2 id="[^"]+">(.*?)</h2>', s)]
    strip = lambda t: html.unescape(re.sub(r'<[^>]+>', '', t))
    return {'slug': 'coursework', 'title': strip(h['title']), 'meta': strip(h['meta']), 'outcome': strip(h['outcome']), 'result': '',
            'facts': [(strip(k), strip(v)) for k, v in h['facts']], 'icon': '', 'sections': secs}


def page(slug):
    p = P[slug] if slug in P else coursework()
    i = ORDER.index(slug) if slug in ORDER else -1
    nxt = P[ORDER[(i + 1) % len(ORDER)]]
    if p.get('figure') and lead_desktop_only(slug):
        fig = ('', '')
    elif p.get('figure'):
        fig = (f'<iframe src="{E(p["figure"])}" title="Live figure: {E(p["title"])}" loading="lazy"></iframe>',
               p['figure'].rsplit('/', 1)[-1])
    elif p.get('image'):
        fig = (f'<img src="{E(p["image"])}" alt="{E(p["title"])}">', p['image'].rsplit('/', 1)[-1])
    else:
        fig = ('', '')
    facts = ''.join(f'<dt>{E(k)}</dt><dd>{v}</dd>' for k, v in p.get('facts', []))   # values are the live page's own markup
    secs = ''.join(f'<li>{E(s)}</li>' for s in p.get('sections', []))
    cur = ' aria-current="page"'
    here = 'Coursework' if slug == 'coursework' else 'Projects'
    # the coursework page opens with a card for each piece (Isaac, 19 Nov 2026); the cards are its index
    cw_index = f'<section class="cwidx" aria-label="All coursework">{C.cw_cards(D["coursework"], lazy=False)}</section>' if slug == 'coursework' else ''
    # a side index (Isaac, 24 Nov 2026): this page's sections, then every project (or every piece of coursework), so a
    # reader can jump within the page or across to the next topic; sticky beside the write-up on wide screens, a plain
    # list above it on narrow ones
    wbody = body_of(slug)
    heads = [(i, re.sub(r'<[^>]+>', '', t)) for i, t in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', wbody, re.S)]
    here_list = ''.join(f'<li><a href="#{i}">{E(H.unescape(t))}</a></li>' for i, t in heads)
    others = ''.join(f'<li><a href="{q}.html"{" aria-current=page" if q == slug else ""}>{E(P[q]["title"])}</a></li>' for q in ORDER if q in P)
    toc = (f'<nav class="rail" aria-label="On this page"><p class="rail-h">On this page</p><ol>{here_list}</ol>'
           + ('' if slug == 'coursework' else f'<p class="rail-h">Projects</p><ol class="rail-all">{others}</ol>')
           + '</nav>') if heads else ''
    nav = ''.join(f'<a href="{h}"{cur if n == here else ""}>{n}</a>' for n, h in NAV)
    crumb = '' if slug == 'coursework' else f'<li><a href="{HOME}#projects">Projects</a></li>'   # the home page has no coursework section to link
    hero_ic = f'<div class="hero-ic panel" style="view-transition-name:hero-icon">{p["icon"]}</div>' if p['icon'] else ''
    fig_panel = f'<section class="fig panel" aria-label="Live figure"><div class="bar"><b>Live figure</b><span>{E(fig[1])}</span></div>{fig[0]}</section>' if fig[0] else ''
    return f"""<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#F5F4F0">
<title>{E(p['title'])} · Isaac Johan Ziebarth (prototype)</title>
<meta name="robots" content="noindex">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chivo+Mono:wght@500;600&display=swap">
<link rel="stylesheet" href="/assets/css/iso-kit.css"><link rel="stylesheet" href="../icons.css">
<style>{PAGE_CSS}</style>
<link rel="stylesheet" href="../polish.css">
{RAIL_STYLE}
</head><body>
<a class="vh" href="#main">Skip to content</a>
<header class="top"><a class="nm" href="{HOME}"><span class="mk">IJZ</span>Isaac Johan Ziebarth</a><nav aria-label="Main">{nav}</nav></header>
<div class="stripe"></div>
<main id="main" class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{HOME}">Home</a></li>{crumb}<li aria-current="page">{E(p['title'])}</li></ol></nav>
<section class="hero{'' if p['icon'] else ' solo'}" aria-labelledby="t">
  {hero_ic}
  <div class="hero-tx">
    <p class="type">{E(p['meta'])}</p>
    <h1 id="t" style="view-transition-name:hero-title">{E(p['title'])}</h1>
    <p class="res">{E(p['result'])}</p>
    <p class="out">{E(p['outcome'])}</p>
    <dl class="facts">{facts}</dl>
  </div>
</section>
{fig_panel}{cw_index}
<section class="wu panel{' cw' if slug == 'coursework' else ''}{' has-rail' if toc else ''}" aria-labelledby="wu"><h2 id="wu">The full write-up</h2>{toc}
  <div class="body">{wbody}</div>
  <p class="old"><a href="{ARCHIVE}/projects/{slug}.html">This page on the old site</a></p></section>
<nav class="next panel" aria-label="Next project"><a href="{nxt['slug']}.html" rel="next">{nxt['icon']}<span><small>Next project</small><b>{E(nxt['title'])}</b></span></a></nav>
</main>
{FIT_JS}{RAIL_CSS}
<footer>Prototype page for the real build: the template from the 19 Nov architecture plan. © Isaac Johan Ziebarth. All rights reserved.</footer>
</body></html>
"""


RAIL_STYLE = """<style>
.rail{font:500 13px/1.45 var(--mono);margin:0 0 18px}.rail-h{font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--mute);margin:0 0 6px;font-size:12px}
.rail ol{list-style:none;margin:0 0 16px;padding:0;display:grid;gap:2px}.rail a{display:block;padding:5px 8px;color:var(--ink);text-decoration:none;border-left:2px solid transparent}
.rail a:hover{background:var(--paper2,#E1DED5)}.rail a[aria-current]{border-left-color:var(--ink);font-weight:600;background:transparent}
.rail-all a[aria-current=page]{color:var(--ind,#2E1499)}
@media (min-width:1100px){.wu.has-rail{display:grid;grid-template-columns:230px minmax(0,1fr);column-gap:36px}.wu.has-rail>h2{grid-column:1/-1}.wu.has-rail>.old{grid-column:2}
.rail{position:sticky;top:76px;align-self:start;max-height:calc(100svh - 96px);overflow:auto;margin:0}}
@media (max-width:1099px){.rail-all,.rail-h+.rail-all{display:none}.rail ol{grid-template-columns:repeat(auto-fill,minmax(200px,1fr))}}
</style>"""


RAIL_CSS = """<script>
(function(){const links=[...document.querySelectorAll('.rail ol:first-of-type a[href^="#"]')];if(!links.length||!('IntersectionObserver' in window))return;
const by=new Map(links.map(a=>[a.getAttribute('href').slice(1),a]));let cur=null;
const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){const a=by.get(e.target.id);if(a&&a!==cur){if(cur)cur.removeAttribute('aria-current');a.setAttribute('aria-current','true');cur=a;}}});},{rootMargin:'-15% 0px -70% 0px'});
by.forEach((a,id)=>{const h=document.getElementById(id);if(h)io.observe(h);});})();
</script>"""


HOME_JS = """
<script>
/* Card-to-page view transitions (prototype). Card titles are real links to vt/<slug>.html; the dialog stays for the
   side panel's Open button only. Names go on the clicked card just for the transition, since each name must be unique. */
(() => {
  const slugOf = u => { try { return (new URL(u, location.href).pathname.match(/\\/vt\\/([\\w-]+)\\.html$/) || [])[1]; } catch (e) { return null; } };
  const name = (slug, on) => { const c = document.querySelector(`.pcard[data-slug="${slug}"]`); if (!c) return null;
    c.querySelector('.icon').style.viewTransitionName = on ? 'hero-icon' : ''; c.querySelector('h3').style.viewTransitionName = on ? 'hero-title' : ''; return c; };
  // The live script opens the dialog for any [data-open] click; let card links navigate instead.
  document.addEventListener('click', e => { if (e.target.closest('a[data-open]')) e.stopPropagation(); }, true);
  addEventListener('pageswap', e => { if (!e.viewTransition) return; const s = slugOf(e.activation && e.activation.entry.url); if (!s) return;
    name(s, true); e.viewTransition.finished.finally(() => name(s, false)); });
  addEventListener('pagereveal', e => { if (!e.viewTransition) return; const f = navigation.activation && navigation.activation.from; const s = f && slugOf(f.url); if (!s) return;
    name(s, true); e.viewTransition.finished.finally(() => name(s, false)); });
})();
</script>
"""

HOME_CSS = """<style>""" + VT_CSS + """
.pcard h3 a{all:unset;cursor:pointer}
.pcard h3 a::after{content:"";position:absolute;inset:0}
.pcard:has(h3 a:focus-visible){outline:2px solid var(--ink);outline-offset:4px}
.pcard h3 a:focus-visible{outline:0!important}
</style>"""


def main():
    out = HERE / 'vt'
    out.mkdir(exist_ok=True)
    for slug in ORDER + ['coursework']:
        (out / f'{slug}.html').write_text(page(slug))
    s = (HERE / 'live4.html').read_text()
    n = 0
    def link(m):
        nonlocal n; n += 1
        return f'<h3><a href="vt/{m.group(1)}.html" data-open="{m.group(1)}">{m.group(2)}</a></h3>'
    s = re.sub(r'<h3><button type="button" data-open="([\w-]+)">(.*?)</button></h3>', link, s)
    s = s.replace('</head>', HOME_CSS + '</head>', 1).replace('</body>', HOME_JS + '</body>', 1)
    s = s.replace('<title>', '<title>VT · ', 1)
    (HERE / 'live4-vt.html').write_text(s)
    print(f'{len(ORDER)} project pages and coursework in vt/, live4-vt.html with {n} card links')


if __name__ == '__main__':
    main()
