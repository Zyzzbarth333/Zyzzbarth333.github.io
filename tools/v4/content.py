"""Extract the live site's real content into one dict for the direction prototypes (read-only)."""
import html, json, re
from pathlib import Path
ROOT = Path.home() / 'Zyzzbarth333.github.io'
FIG = {'theseus': 'theseus-map.html', 'havoc2-cosmos': 'havoc2-flight.html', 'osiris': 'osiris-v0-kicad.html',
       'airbrakes': 'airbrakes-controllers.html', 'digital-orrery': 'orrery-porkchop.html',
       'weather-station': 'weather-station-exploded.html', 'errol': 'errol-lichtblick.html',
       'camera-mount': 'camera-mount-3d.html'}
IMG = {'metr4810': 'metr4810-pod-section.webp', 'crank-arm': 'crank-arm-section.webp', 'engg1100': 'engg1100-vehicle.jpg'}
TAGS = {'theseus': ['autonomy'], 'havoc2-cosmos': ['avionics'], 'osiris': ['avionics'], 'airbrakes': ['gnc'],
        'digital-orrery': ['gnc', 'software'], 'weather-station': ['avionics'], 'errol': ['autonomy', 'software'],
        'metr4810': ['mechanical'], 'crank-arm': ['mechanical'], 'camera-mount': ['mechanical'], 'engg1100': ['mechanical']}
SHORT = {'theseus': ('THESEUS V', '1ST OF 17', 'PLACED'), 'havoc2-cosmos': ('HAVOC-2', '540 M FLOWN', 'FLOWN'),
         'osiris': ('OSIRIS', 'ERC CLEAN', 'ON BENCH'), 'airbrakes': ('AIRBRAKES', '200 SIM RUNS', 'DONE'),
         'digital-orrery': ('ORRERY', '14240 CELLS', 'LIVE'), 'weather-station': ('WX STATION', '98218 ROWS OK', 'FLOWN'),
         'errol': ('ERROL', 'ROS 2 SIM', 'DONE'), 'metr4810': ('METR4810', 'STEERED POD', 'BUILT'),
         'crank-arm': ('CRANK ARM', '21% LIGHTER', 'DONE'), 'camera-mount': ('CAM MOUNT', '4 WEEKS', 'FITTED'),
         'engg1100': ('ENGG1100', '5 OF 6 OUT', 'DONE')}
RESULT = {'theseus': '1st of 17', 'havoc2-cosmos': 'about 540 m, every frame passed', 'osiris': '0 ERC errors',
          'airbrakes': '200 simulated flights', 'digital-orrery': '0 bad arcs in 14,240 cells',
          'weather-station': '98,218 rows passed', 'errol': 'ROS 2 simulator + operator tools',
          'metr4810': 'steered cutter pod', 'crank-arm': '21% lighter', 'camera-mount': 'fitted in 4 weeks',
          'engg1100': '5 of 6 targets out'}

# METR4810: the icon rebuilt from the real v195 meshes on 19 Nov (portfolio/figures/icons, metr4810_parts.py); its
# render layers live in proto/icons-mesh/ until the real site build copies them to assets/img/projects/.
# Theseus: the live body render includes the Theseus VI mount (not for publication); the prototypes use the render
# without it until the live site is fixed.
LAYER_OVERRIDE = {'theseus': ['theseus-body.webp']}
ICON_OVERRIDE = {'metr4810': Path(__file__).resolve().parent / 'icon-override/metr4810-icon.svg'}

def text(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s))).strip()

def fix(s):
    return s.replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/')

def load():
    s = (ROOT / 'index.html').read_text()
    projects = []
    for m in re.finditer(r'<li class="card[^"]*"[^>]*>(.*?)</li>', s, re.S):
        li = m.group(1)
        a = re.search(r'<a href="projects/([\w-]+)\.html">(.*?)</a>', li)
        if not a:
            continue
        slug = a.group(1)
        icon = re.search(r'(<span class="icon iso".*?</svg></span>)', li, re.S).group(1)
        p = {'slug': slug, 'href': f'vt/{slug}.html',   # the new project pages (build8.py); the old ones are in mocks/archive-live
              'title': text(a.group(2)),
             'meta': text(re.search(r'<p class="meta">(.*?)</p>', li).group(1)),
             'summary': text(re.search(r'<p class="summary">(.*?)</p>', li, re.S).group(1)),
             'icon': fix(icon), 'earlier': '<h4>' in li, 'tags': TAGS.get(slug, []),
             'short': SHORT.get(slug), 'result': RESULT.get(slug, ''),
             'figure': f'/assets/figures/{FIG[slug]}' if slug in FIG else None,
             'image': f'/assets/img/projects/{IMG[slug]}' if slug in IMG else None}
        pg = (ROOT / 'projects' / f'{slug}.html').read_text()
        o = re.search(r'<p class="outcome">(.*?)</p>', pg, re.S)
        p['outcome'] = text(o.group(1)) if o else p['summary']
        # values keep their markup (links such as the code repository, and their hidden 'opens in a new tab' labels)
        p['facts'] = [(text(dt), fix(re.sub(r'\s+', ' ', dd).strip())) for dt, dd in re.findall(r'<dt>(.*?)</dt><dd>(.*?)</dd>', pg, re.S)]   # every row (the Theseus Press row is the sixth)
        p['sections'] = [text(h) for h in re.findall(r'<h2 id="[^"]+">(.*?)</h2>', pg)]
        # the figure's own shape, so the home page's preview panel can fit it: the embed's --ratio on the live page, or
        # the image's pixel size
        p['ratio'] = None
        if slug in FIG:
            r = re.search(r'<iframe [^>]*' + re.escape(FIG[slug]) + r'[^>]*--ratio:([\d.]+)', pg)
            p['ratio'] = float(r.group(1)) if r else None
        elif slug in IMG:
            from PIL import Image
            w, h = Image.open(ROOT / 'assets/img/projects' / IMG[slug]).size
            p['ratio'] = round(w / h, 3)
        for layer in LAYER_OVERRIDE.get(slug, []):   # a corrected render layer (prototype only)
            p['icon'] = p['icon'].replace(f'/assets/img/projects/{layer}', f'/.impeccable/mocks/proto/icons-mesh/{layer}')
        if slug in ICON_OVERRIDE and ICON_OVERRIDE[slug].exists():   # a newer icon than the live site's (prototype only)
            svg = ICON_OVERRIDE[slug].read_text().replace('href="assets/img/projects/', 'href="/.impeccable/mocks/proto/icons-mesh/')
            p['icon'] = re.sub(r'<svg.*</svg>', lambda _: svg, p['icon'], count=1, flags=re.S)
        projects.append(p)
    cw = [{'title': text(t), 'href': 'vt/' + h.split('/', 1)[1], 'meta': text(mt)} for h, t, mt in
          re.findall(r'<li><a href="(projects/coursework\.html#[^"]+)">(.*?)</a><span class="meta">(.*?)</span></li>', s)]
    # the coursework page gives each piece its course, year, who did it and its first figure (the cards' thumbnail);
    # a piece without a figure there (the crank arm) uses its project page's image
    cwp = (ROOT / 'projects' / 'coursework.html').read_text()
    for part in re.split(r'(?=<h2 id=")', cwp[cwp.find('<div class="prose">'):cwp.find('</main>')])[1:]:
        h = re.search(r'<h2 id="([^"]+)">', part)
        c = next((c for c in cw if c['href'].endswith('#' + h.group(1))), None) if h else None
        if not c:
            continue
        m = re.search(r'<p class="meta">(.*?)</p>', part)
        bits = [x.strip() for x in text(m.group(1)).split('·')] if m else []
        c['id'] = h.group(1)
        c['code'], c['course'] = (bits[0].split(' ', 1) + [''])[:2] if bits else ('', '')
        c['year'] = bits[1] if len(bits) > 1 else ''
        c['who'] = bits[2] if len(bits) > 2 else ''
        img = re.search(r'<img src="\.\./([^"]+)"', part)
        c["img"] = "/" + img.group(1) if img else None
    for c in cw:
        if c.get('img') is None and 'crank arm' in c['title'].lower():
            c['img'] = f"/assets/img/projects/{IMG['crank-arm']}"
    about = [text(x) for x in re.findall(r'<div class="bio reveal">(.*?)</div>', s, re.S)[0].split('</p>') if text(x)]
    exp = [tuple(text(x) for x in e) for e in re.findall(
        r'<span class="role">(.*?)</span><span class="org">(.*?)</span></span><span class="when">(.*?)</span>', s)]
    edu = text(re.search(r'<p class="edu[^"]*">(.*?)</p>', s).group(1))
    email = re.search(r'mailto:([^"]+)"', s).group(1)
    linkedin = re.search(r'href="(https://www\.linkedin\.com[^"]+)"', s).group(1)
    return {'projects': projects, 'coursework': cw, 'about': about, 'experience': exp, 'edu': edu,
            'email': email, 'linkedin': linkedin, 'github': 'https://github.com/Zyzzbarth333',
            # the 3D-printing profiles from the live site's footer (v4 had dropped them; Isaac, 19 Nov 2026)
            'printables': re.search(r'href="(https://www\.printables\.com/[^"]+)"', s).group(1),
            'makerworld': re.search(r'href="(https://makerworld\.com/[^"]+)"', s).group(1)}

if __name__ == '__main__':
    d = load()
    print(len(d['projects']), len(d['coursework']), len(d['about']), len(d['experience']))
    for p in d['projects']:
        print(p['slug'], p['earlier'], bool(p['figure']), p['facts'][:1], p['sections'][:3])


def cw_cards(cw, page='', lazy=True):
    """The coursework cards (the home page's Coursework section and the index at the top of the coursework page):
    the piece's first figure, course code and year, title, and who did it, linking to its write-up."""
    out = []
    for c in cw:
        img = f'<span class="th"><img src="{html.escape(c["img"])}" alt=""{' loading="lazy"' if lazy else ''} decoding="async"></span>' if c.get('img') else '<span class="th"></span>'
        out.append(f'<li class="cwcard"><a href="{page}#{c.get("id", "")}">{img}<span class="cc">{html.escape(c.get("code", ""))} · {html.escape(c.get("year", ""))}</span>'
                   f'<b>{html.escape(c["title"])}</b><span class="who">{html.escape(c.get("who", ""))}</span></a></li>')
    return '<ul class="cwgrid">' + ''.join(out) + '</ul>'


# Smaller projects, shown as a row of short cards under the main grid (from facts.yaml site entries, 24 Nov 2026).
# Credits follow each entry's note in facts.yaml; no figures that facts.yaml does not have.
ALSO = [
    {'title': 'Belt-driven Ender 3 V2', 'kicker': 'Personal project · Apr 2023 – present',
     'text': 'An Ender 3 V2 rebuilt with a belt-driven dual Z, linear rails and a Klipper host, tuned with an accelerometer. Input shaping settled at 45.5 Hz on X and 46.8 Hz on Y.',
     'link': ('https://github.com/Zyzzbarth333/3d-printing-configs', 'Configs and slicer profiles on GitHub'),
     'credit': 'Built mostly from community designs: <a href="https://github.com/kevinakasam/BeltDrivenEnder3">Kevin Akasam\'s BeltDrivenEnder3</a> and the <a href="https://www.printables.com/model/39322-hero-me-gen7-platform-release4">HERO ME Gen7</a> toolhead.'},
    {'title': 'Armour optimiser for a combat robot', 'kicker': 'UQ MARS Robowars · Jan 2025',
     'text': 'A Python tool that ranks layered armour for a combat robot against hammer, spinner and saw weapons under weight and cost limits. The team\'s robot fought at Robowars, World Science Festival Queensland, in March 2025.',
     'link': ('https://github.com/Zyzzbarth333/battlebot-armour-optimiser', 'Code on GitHub')},
    {'title': 'Gridfinity for two IKEA Alex units', 'kicker': 'Personal project · Nov 2026 – present',
     'text': 'Gridfinity storage for two IKEA Alex drawer units, with new baseplate tiles sized to the drawers and every slot tied to the parts inventory. Drawer L1 is printed and in use; the first pair of the new 294.5 mm tiles is fit-tested.',
     'img': ('/assets/img/projects/gridfinity-alex.webp', 'Render of two drawer units with their top drawers open, showing coloured and grey Gridfinity bins on the new baseplates'),
     'credit': 'Bins: <a href="https://www.printables.com/model/592545">Pred\'s Gridfinity bin with label</a> (CC BY-NC 4.0); drawer L1 keeps an IKALEX plate. The baseplates and the drawer model are my own geometry.'},
    {'title': 'Parts inventories in git', 'kicker': 'Workshop and UQ Space · Jun 2026 – present',
     'text': 'Version-controlled parts inventories for my workshop and for UQ Space, edited as a spreadsheet and checked in git and CI. The UQ Space inventory holds 569 items across 11 sections, validated on every push.'},
    {'title': 'An engineering assistant that stays on my laptop', 'kicker': 'Personal project · Nov 2026 – present',
     'text': "An engineering assistant that runs entirely on my laptop's GPU, so repositories and documents never leave the machine. Ongoing."},
]


def also_html():
    """The row of short cards for the smaller projects."""
    import html as _h
    E = _h.escape
    out = []
    for a in ALSO:
        img = f'<img src="{a["img"][0]}" alt="{E(a["img"][1])}" loading="lazy" decoding="async">' if a.get('img') else ''
        link = f'<a class="more" href="{a["link"][0]}">{E(a["link"][1])}</a>' if a.get('link') else ''
        credit = f'<p class="credit">{a["credit"]}</p>' if a.get('credit') else ''
        out.append(f'<li class="also-card{" has-img" if img else ""}">{img}<p class="k">{E(a["kicker"])}</p><h3>{E(a["title"])}</h3><p>{E(a["text"])}</p>{credit}{link}</li>')
    return '<div class="also"><h3 class="also-h">Also building</h3><ul class="also-grid">' + ''.join(out) + '</ul></div>'
