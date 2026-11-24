"""Writes index.html, 404.html and projects/*.html for the portfolio site.

Project wording comes from the CV chat's verified entries (linkedin-updates.md
section 10 and its 12 Nov message) and, for digital-orrery, from the Digital
orrery chat's 12 Nov facts checked against main (b5f4ae6).
Run with: python3 -I build_site.py <repo>
"""
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

REPO = Path(sys.argv[1])
DRAFTS = '--drafts' in sys.argv          # include pages marked draft=True (for review only; never publish a --drafts build)
SITE = 'https://zyzzbarth333.github.io'
# The "Email me" address comes from the owner's shell profile, not this file (export PORTFOLIO_CONTACT_EMAIL=...).
EMAIL = os.environ.get('PORTFOLIO_CONTACT_EMAIL') or sys.exit('Set PORTFOLIO_CONTACT_EMAIL (the site\'s contact address) first.')
LINKS = [
    ('LinkedIn', 'https://www.linkedin.com/in/isaacjohanziebarth/', '<svg class="icon-social" viewBox="0 0 448 512" aria-hidden="true" focusable="false"><path d="M100.28 448H7.4V148.9h92.88zM53.79 108.1C24.09 108.1 0 83.5 0 53.8a53.79 53.79 0 0 1 107.58 0c0 29.7-24.1 54.3-53.79 54.3zM447.9 448h-92.68V302.4c0-34.7-.7-79.2-48.29-79.2-48.29 0-55.69 37.7-55.69 76.7V448h-92.78V148.9h89.08v40.8h1.3c12.4-23.5 42.69-48.3 87.88-48.3 94 0 111.28 61.9 111.28 142.3V448z"/></svg>'),
    ('GitHub', 'https://github.com/Zyzzbarth333', '<svg class="icon-social" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>'),
    ('Printables', 'https://www.printables.com/@Zyzzbarth333', '<svg class="icon-social" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M3.678 4.8 12 9.6v9.6l8.322-4.8V4.8L12 0ZM12 19.2l-8.322-4.8V24Z"/></svg>'),
    ('MakerWorld', 'https://makerworld.com/en/@Zyzzbarth', '<svg class="icon-social" viewBox="0 0 23.7708 24.001" aria-hidden="true" focusable="false"><path d="M17.3515 0L11.8854 2.1609L6.41929 0L0 2.53822V21.4628L6.41929 24.001L11.8854 21.8401L17.3515 24.001L23.7708 21.4628V2.53822L17.3515 0ZM17.3515 1.03184L22.8176 3.19274V11.0018L17.3515 8.84192V1.03184ZM17.3515 9.87471L22.7307 12.001L17.3515 14.1272L11.9723 12.001L17.3515 9.87471ZM6.41929 1.03184L11.8854 3.19274V11.0018L6.41929 8.84192V1.03184ZM6.41929 9.87471L11.7975 12.001L6.41835 14.1272L1.04011 12.001L6.41929 9.87471ZM0.953201 20.8073V12.9982L6.41929 15.1581V22.9682L0.953201 20.8073ZM11.8854 20.8073V12.9982L17.3515 15.1581V22.9682L11.8854 20.8073Z"/></svg>'),
]
E = html.escape


def ver(rel):
    """Cache-busting tag: the first 8 hex digits of the file's hash, so a changed file gets a new URL."""
    import hashlib
    return hashlib.sha256((REPO / rel).read_bytes()).hexdigest()[:8]


# Visitor analytics: GoatCounter, cookie-free. Off until the owner creates the account and sets the site code here.
GOATCOUNTER = 'zyzzbarth333'   # https://zyzzbarth333.goatcounter.com (set up 14 Nov 2026)


def analytics():
    if not GOATCOUNTER:
        return ''
    return f'    <script data-goatcounter="https://{GOATCOUNTER}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>\n'



def robots_meta(noindex, path):
    """A page to index names its canonical URL; a page not to index (the 404) says so instead."""
    return '    <meta name="robots" content="noindex">\n' if noindex else f'    <link rel="canonical" href="{SITE}/{path}">\n'


def ld(data):
    return '    <script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>\n'


def profile_data(desc):
    """schema.org for the home page: the site, the profile page and the person, with stable ids that the project pages
    point back to. Only what the page itself says (SEO audit, 19 Nov 2026)."""
    data = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebSite', '@id': f'{SITE}/#website', 'url': f'{SITE}/', 'name': 'Isaac Johan Ziebarth', 'inLanguage': 'en-AU',
         'publisher': {'@id': f'{SITE}/#person'}},
        {'@type': 'ProfilePage', '@id': f'{SITE}/#profile', 'url': f'{SITE}/', 'name': 'Isaac Johan Ziebarth', 'inLanguage': 'en-AU',
         'isPartOf': {'@id': f'{SITE}/#website'}, 'mainEntity': {'@id': f'{SITE}/#person'}},
        {'@type': 'Person', '@id': f'{SITE}/#person', 'name': 'Isaac Johan Ziebarth', 'url': f'{SITE}/',
         'image': f'{SITE}/assets/img/profile.jpg', 'description': desc,
         'affiliation': {'@type': 'CollegeOrUniversity', 'name': 'The University of Queensland', 'url': 'https://www.uq.edu.au/'},
         'knowsAbout': ['Rover autonomy', 'Rocket avionics', 'Ground stations', 'Embedded C++', 'ROS 2', 'KiCad'],
         'sameAs': [u for _, u, _ in LINKS]},
    ]}
    return ld(data)


def crumbs_data(p):
    """BreadcrumbList matching the visible crumbs: Home, Projects (the home page's list), the page; coursework has no
    middle step."""
    page = f'{SITE}/projects/{p["slug"]}.html'
    items = [('Home', f'{SITE}/')] + ([] if p.get('coursework') else [('Projects', f'{SITE}/#projects')]) + [(p['title'], page)]
    return ld({'@context': 'https://schema.org', '@type': 'BreadcrumbList',
               'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)]})


def search_files():
    """sitemap.xml (the home page and every published project page) and robots.txt pointing at it."""
    urls = [f'{SITE}/'] + [f'{SITE}/projects/{p["slug"]}.html' for p in PROJECTS if not p.get('draft')]
    def lastmod(u):   # the page's last commit, never the build date (a stamp on every URL teaches search engines to ignore it)
        f = 'index.html' if u == f'{SITE}/' else u.split(SITE + '/', 1)[1]
        d = subprocess.run(['git', '-C', str(REPO), 'log', '-1', '--format=%cs', '--', f], capture_output=True, text=True).stdout.strip()
        return f'<lastmod>{d}</lastmod>' if d else ''
    body = ''.join(f'  <url><loc>{E(u)}</loc>{lastmod(u)}</url>\n' for u in urls)
    (REPO / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + '</urlset>\n')
    (REPO / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    return len(urls)

def head(title, desc, prefix, og_image='assets/img/profile.jpg', path='', extra_css='', noindex=False, og_alt='Isaac Johan Ziebarth'):
    share = og_image.endswith('-share.jpg')
    return f'''<!DOCTYPE html>
<html lang="en-AU">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="color-scheme" content="light">
    <title>{E(title)}</title>
    <meta name="description" content="{E(desc)}">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{E(title)}">
    <meta property="og:description" content="{E(desc)}">
    <meta property="og:url" content="{SITE}/{path}">
    <meta property="og:site_name" content="Isaac Johan Ziebarth">
    <meta property="og:locale" content="en_AU">
{robots_meta(noindex, path)}    <meta property="og:image" content="{SITE}/{og_image}">
{'    <meta property="og:image:width" content="1200">' + chr(10) + '    <meta property="og:image:height" content="630">' + chr(10) if share else ''}    <meta property="og:image:alt" content="{E(og_alt)}">
    <meta name="twitter:card" content="{'summary_large_image' if share else 'summary'}">
    <meta name="twitter:image:alt" content="{E(og_alt)}">
    <meta name="theme-color" content="#BB0700">
    <link rel="icon" href="{prefix}favicon.ico" sizes="48x48">
    <link rel="icon" href="{prefix}assets/img/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="{prefix}assets/img/apple-touch-icon.png">
    <link rel="manifest" href="{prefix}site.webmanifest">
    <link rel="preload" href="{prefix}assets/fonts/fraunces-900-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="{prefix}assets/fonts/sanchez-400-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="{prefix}assets/css/style.css?v={ver('assets/css/style.css')}">
{extra_css}    <script>
        // Hide .reveal content only once JS runs; if site.js never loads, show everything.
        document.documentElement.classList.add('js');
        setTimeout(function () {{ if (!window.revealReady) document.documentElement.classList.remove('js'); }}, 2500);
    </script>
{analytics()}</head>
'''


NEW_TAB = ' (opens in a new tab)'


def announce_new_tabs(page):
    """Links with target="_blank" say they open a new tab: in the aria-label when they have one, else in hidden text."""
    def fix(m):
        tag, inner = m.group(1), m.group(2)
        if NEW_TAB in tag or NEW_TAB in inner:
            return m.group(0)
        if 'aria-label="' in tag:
            return re.sub(r'aria-label="([^"]*)"', lambda a: f'aria-label="{a.group(1)}{NEW_TAB}"', tag, count=1) + inner + '</a>'
        return f'{tag}{inner}<span class="visually-hidden">{NEW_TAB}</span></a>'
    return re.sub(r'(<a\b[^>]*\btarget="_blank"[^>]*>)(.*?)</a>', fix, page, flags=re.S)


def header(prefix, current):
    home = f'{prefix}index.html' if prefix else '#top'
    proj = f'{prefix}index.html#projects' if prefix else '#projects'
    cont = f'{prefix}index.html#contact' if prefix else '#contact'
    cw = f'{prefix}projects/coursework.html' if prefix != '../' else 'coursework.html'   # pages in projects/ use '../'
    home_attr = ' aria-current="page"' if current == 'home' else ''
    proj_attr = ' class="is-current"' if current == 'projects' else ''
    cw_attr = ' aria-current="page"' if current == 'coursework' else ''
    social = '\n'.join(
        f'                <li><a href="{u}" target="_blank" rel="noopener" aria-label="{n}" title="{n}">{i}</a></li>'
        for n, u, i in LINKS)
    return f'''<body id="top">
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header{' on-home' if current == 'home' else ''}">
        <div class="header-inner">
            <nav class="main-nav" aria-label="Main">
                <ul class="nav-links">
                    <li><a href="{home}"{home_attr}>Home</a></li>
                    <li><a href="{proj}"{proj_attr}>Projects</a></li>
                    <li><a href="{cw}"{cw_attr}>Coursework</a></li>
                    <li><a href="{cont}">Contact</a></li>
                </ul>
            </nav>
            <a class="site-title" href="{home}">Isaac Johan Ziebarth</a>
            <ul class="social-links">
{social}
            </ul>
        </div>
    </header>
'''


def footer(prefix):
    links = '\n'.join(f'                <li><a href="{u}" target="_blank" rel="noopener">{n}</a></li>' for n, u, _ in LINKS)
    return f'''    <footer class="site-footer">
        <div class="footer-inner">
            <p class="footer-name">Isaac Johan Ziebarth</p>
            <ul class="footer-links">
{links}
            </ul>
        </div>
        <p class="footer-bar">&copy; 2026 Isaac Johan Ziebarth. All rights reserved. <a href="https://github.com/Zyzzbarth333/Zyzzbarth333.github.io" target="_blank" rel="noopener">Site source</a></p>
    </footer>
    <script src="{prefix}assets/js/site.js?v={ver('assets/js/site.js')}" defer></script>
</body>
</html>
'''


# ---------------------------------------------------------------- content

TAGLINE = 'Mechatronic engineering student, UQ · Led UQ Space avionics until November 2026'


SEEKING = ("I'm looking for internships and graduate roles in avionics and embedded systems, robotics and autonomy, "
           "and guidance, navigation and control.")   # PRODUCT.md's confirmed target roles


def tagline_html():
    """The tagline's two halves, one per line, so no separator dot is left hanging at a line end."""
    return ' '.join(f'<span class="tl">{E(t)}</span>' for t in TAGLINE.split(' · '))
BIO = [
    "I'm studying mechatronic engineering at UQ (BE(Hons)/ME, finishing in 2027), and I like building things that have to work outside the lab.",
    "At UQ Space I wrote the autonomy stack and ground control station for Theseus, our rover, and the team placed 1st of 17 at the 2026 Australian Rover Challenge. On the rocket side I wrote the flight firmware for HAVOC-2, our flight computer, and built COSMOS, the ground station we run at launches.",
    "I led the avionics team of about 25 until November 2026. As lead I set up its 4 subteams and wrote the avionics sections of the critical design review for the 2027 rover competition, along with a requirements verification matrix. I handed the lead over to make room for my research assistant role and a Master's placement in Semester 1, 2027. I've stayed on the team as an engineer, and I advise the new Lead and Deputy Lead. I'm still working on the rocket and rover ground control stations, PCB design and the Theseus VI autonomy stack.",
    "I also work part-time as a research assistant in UQ's School of EECS, on PX4 flight-control software and modelling. The part of engineering I enjoy most is modelling: taking a real system and building a model that predicts how it will behave.",
]
# The About section's last paragraph. Only tools in facts.yaml's skills list (KiCad added 14 Nov 2026). Q7 confirmed 14 Nov 2026: "design" holds for boards (OSIRIS). Parts stay "make", since the weather enclosure is only "built".
# Non-breaking spaces keep ROS 2 and Fusion 360 on one line (Fusion 360 split at 380, 440 and 600 px wide).
TOOLS = ("I write C++, Python and C. I build robot and flight software with ROS\u00a02, Nav2, PX4 and Gazebo, model systems in "
         "MATLAB, Simulink, SymPy and Mathematica, and make parts with Fusion\u00a0360 and 3D printing. I design circuit boards in KiCad.")
EXPERIENCE = [
    ('Avionics Engineer', 'UQ Space', 'Nov 2026 – present'),
    ('Research Assistant (part-time)', 'School of EECS, The University of Queensland', 'Sep 2026 – present'),
    ('Lead Avionics Engineer', 'UQ Space', 'Oct 2025 – Nov 2026'),
    ('Avionics Engineer', 'UQ Space', 'Sep 2024 – Oct 2025'),
    ('Winter Research Student', 'School of Mechanical and Mining Engineering, UQ (Errol, the autonomous research car)', 'Jun – Jul 2025'),
    ('Casual Technician', 'Sustainable Minerals Institute, UQ', 'Jan – Feb and Jul – Dec 2024'),
    ('Winter Research Student', 'Sustainable Minerals Institute, UQ', 'Jun – Jul 2023'),
]
EDUCATION = 'Bachelor of Engineering (Honours) and Master of Engineering, Mechatronic Engineering, The University of Queensland. Expected Nov 2027.'
PRIVATE = 'Private: UQ Space team repositories'


def ul(items):
    """items: list of (lead, text). Lead is bolded."""
    lis = '\n'.join(f'                <li><strong>{E(l)}</strong> {E(t)}</li>' if l else f'                <li>{E(t)}</li>' for l, t in items)
    return f'<ul>\n{lis}\n            </ul>'


# The METR4810 bench figure (figures/metr4810) is on hold (Isaac, 19 Nov 2026): it ships only with METR4810_BENCH=1.
METR4810_BENCH = os.environ.get('METR4810_BENCH') == '1'
P = 'projects/'


PROJECTS = [
    dict(
        slug='theseus', card=P + 'theseus-icon.svg', card_alt="LiDAR map of the competition arena with the rover's autonomous path",
        kicker='Team project · UQ Space · 2025–26', title='Theseus V rover autonomy', team=True,
        summary="The autonomy software I wrote in C++ and Python for the rover at the 2026 Australian Rover Challenge, where UQ Space placed 1st of 17.",
        outcome="The ROS 2 autonomy stack I wrote on my own for UQ Space's Theseus V rover. It ran the autonomy task at the 2026 Australian Rover Challenge, where the team placed **1st of 17**.",
        tiles=[('1st of 17', 'ARCh 2026, team result'), ('9', 'ROS 2 packages'), ('82 of 83', 'commits are mine')],
        facts=[('My role', 'Lead avionics engineer. Sole developer of the autonomy stack (82 of 83 commits) and of Theseus GCS, the ground control station (87 of 87 commits)'),
               ('Team', 'Avionics, one of the 6 UQ Space sub-teams that developed Theseus V'),
               ('When', 'Oct 2025 – Apr 2026'),
               ('Tools', 'ROS 2, Nav2, FAST-LIO2, C++, Python, Gazebo, YOLO, React'),
               ('Code', PRIVATE),
               ('Press', 'Interviewed for <a href="https://www.space.gov.au/news-and-media/gen-space-uq-space-winning-2026-australian-rover-challenge" target="_blank" rel="noopener">the Australian Space Agency\'s Gen Space feature</a> (28\u00a0Apr\u00a02026) on the team\'s win')],
        lead=dict(embed='theseus-map.html', ratio=1.12,
                  title="Top-down LiDAR map of the competition arena with the rover's autonomous path and the 2 cubes it detected",
                  cap="The rover's own LiDAR map of the 2026 Australian Rover Challenge (ARCh) arena from above: 150,000 points of its FAST-LIO2 map, darker where the ground is higher, with the autonomous run's path and the 2 cubes it detected. The path joins the run's 6 SLAM keyposes with straight lines, so it is simplified. The map is placed on the arena by matching its crater rims to a ground-truth scan."),
        sections=[
            ('The problem', "<p>In the Australian Rover Challenge's mapping and autonomy task, the rover is dropped into an unknown arena. It has to explore, build a map and report what it finds with nobody driving.</p>"),
            ('What I did', '<h3>Autonomy stack</h3>\n            ' + ul([
                ('', "The stack is 9 ROS 2 packages on two computers. An Orange Pi 5 Plus runs Nav2, FAST-LIO2 LiDAR-inertial odometry from a Livox MID-360 LiDAR, and KISS-SLAM, which turns FAST-LIO2's output into the 2D occupancy map that exploration works from. A Jetson Xavier NX runs YOLO and ArUco detection on the cameras."),
                ('', 'A frontier detector picks the next goal, and a 10-state supervisor runs the mission.'),
                ('', 'For safety I wrote 4 costmap layers in C++ (the maps Nav2 plans around) and a 4-layer geofence that slows, then stops, the rover near the arena boundary.'),
                ('', 'I built a Gazebo arena with placards and randomly placed cubes, so I could test the whole stack in simulation before the hardware was ready.'),
                ('', "The rover doesn't spin in place. Spinning a skid-steer rover can dig its wheels into sand and draw high current, and KISS-ICP, the LiDAR-only odometry I started with, lost track during pure rotation. So the 9-stage recovery sequence I wrote for Nav2 clears the costmap, waits, nudges forward and backs up instead, and the path follower turns in arcs."),
            ]) + '\n            <h3>Theseus GCS</h3>\n            ' + '<p>The ground control station is a React app. Its autonomy tab sends the arena layout, launches the autonomy stack and switches the rover between teleop (remote driving) and auto.</p>'),
        ],
        figures=[dict(embed='theseus-architecture.html', ratio=1.6,
                      title='Block diagram of the Theseus V autonomy stack across the Orange Pi, the Jetson and the rover server, with the placard link that failed at ARCh 2026 in red',
                      cap="How the autonomy stack I wrote fits together, as its code stands: odometry and KISS-SLAM's map feed exploration, the supervisor sends goals to Nav2, and Nav2's velocity passes the geofence and a gate on the rover server before it reaches the drive Pico. The red line is the placard detections, which did not reach the supervisor at ARCh 2026 (see What went wrong)."),
                 dict(embed='theseus-arena.html', ratio=1.45,
                      title='Live replica of the Theseus GCS arena map and autonomy controls, drawn from the real ARCh 2026 arena configuration',
                      cap="A live replica of Theseus GCS's arena map and autonomy controls, drawn from the arena configuration its Arena Config Builder wrote for ARCh 2026: the e-stop edge, the geofence slow zone, the planner's bounds, the five ArUco placards, 28 known obstacles and the start pose. Point at or tap anything for its position (the table under the map lists them all), switch layers off, and step through Send config, Launch stack and Auto (simulation only).")],
        after=[
            ('Result', '<p>At the competition Theseus GCS ran the autonomy and mapping task; the driving tasks used a separate camera feed with less delay.</p>'),
            ('What went wrong', ul([
                ('IMU vibration:', "the MID-360's built-in IMU sits next to the LiDAR's spinning prism motor, and the motor's vibration coupled straight into it. Every LiDAR-inertial odometry we tried on the rover (FAST-LIO2, Point-LIO and DLIO) folds the IMU into its filter, so the extra noise showed up as persistent drift in the odometry, while LiDAR-only KISS-ICP did better on the same data. Before the competition I added an IMU filter node that calibrates the gyro bias at start-up, updates it whenever the rover is stopped and clamps the gyro after a stop, but it couldn't remove vibration while the rover was driving. For Theseus VI we moved to an external IMU on the rigid sensor plate and kept the MID-360's IMU for logging only."),
                ('Placard detections:', "shortly before the competition I switched the ArUco detectors to best-effort QoS, but my topic mux still subscribed to them as reliable. ROS 2 never connects a reliable subscriber to a best-effort publisher, so live placard detections couldn't reach the mission supervisor during the run. I fixed the mux's QoS the day after."),
            ])),
            # Kept on purpose (Isaac, 18 Nov 2026): text only, matching LinkedIn entry 10b. The dedicated Theseus VI page and
            # its renders stay unpublished (site.theseus-vi site_safe: false).
            ('What\'s next', "<p>For Theseus VI I've designed a sensor head that indexes the LiDAR to 10, 15 or 20 degrees, and an avionics bay layout with checked clearances. Nothing is built or tested yet.</p>"),   # Q7 confirmed 14 Nov 2026 for the Avionics work
        ],
        credits="Theseus V is a UQ Space team rover. The page covers the software I wrote for it; the rover itself is the work of UQ Space's aerostructures, avionics, payload, propulsion, recovery and systems engineering sub-teams.",
    ),
    dict(
        slug='havoc2-cosmos', card=P + 'havoc2-icon.svg', card_alt="3D plot of HAVOC-2's first flight trajectory",
        kicker='Team project · UQ Space · 2026', title='HAVOC-2 firmware and COSMOS ground station', team=True,
        summary='The C++ flight firmware I wrote and the ground station I built for UQ Space rockets. On the first flight, to about 540 m, every logged frame passed its checksum.',
        outcome="The C++ flight firmware I wrote for UQ Space's HAVOC-2 flight computer, and COSMOS, the ground station I built, which the team runs at launches. On HAVOC-2's first flight, to about **540 m**, every logged frame passed its cyclic redundancy check (CRC), and every intact radio frame matched the SD card byte for byte.",
        tiles=[('≈540 m', 'first flight apogee'), ('100%', 'logged frames passed CRC'), ('137 → 0.37', 'm/s false pad speed, replayed')],
        facts=[('My role', "Lead avionics engineer until November 2026. Developed HAVOC-2's C++ flight firmware (all 24 firmware commits) from June to November 2026, when the team moved to a consolidated flight computer. Built COSMOS; nobody else has committed to it"),
               ('Team', 'UQ Space avionics team; teammates designed the HAVOC-2 board'),
               ('When', 'HAVOC-2 firmware Jun – Nov 2026; COSMOS May 2026 – present'),
               ('Tools', 'C++, Teensy 4.1, RFD900 radio, Python, React, WebSockets, OpenRocket for Monte Carlo ensembles'),
               ('Code', PRIVATE)],
        og=P + 'havoc2-share.jpg',   # 1200 x 630 shot of the lead figure: recipe in figures/havoc2/share-image.json
        lead=dict(embed='havoc2-flight.html', ratio=2.2, wide=True,
                  title='Interactive plots of HAVOC-2 first flight from its logs: altitude, ground track and boost acceleration, with a linked cursor',
                  cap="HAVOC-2's first flight (Queensland Rocketry Society, 12 July 2026), from the cleaned flight logs. Point at or tap the altitude plot, or use its arrow keys, to read any moment; the ground track and acceleration follow. Solid lines are measured and dashed lines modelled: the ascent track comes from the IMU, the top of the descent from GPS, and the rest of the descent's horizontal path from a wind-drift model. About 9 s went unlogged while the board rebooted after the ejection brownout, so the descent's timing is approximate. Positions are relative to the pad."),
        sections=[
            ('The problem', "<p>The team needed a flight computer that logs a rocket's flight and streams it to the ground reliably, and a ground station that shows the flight live and keeps a record that can be checked afterwards.</p>"),
            ('What I did', '<h3>HAVOC-2 firmware</h3>\n            ' + ul([
                ('', 'The firmware read an IMU, a high-g accelerometer, a barometer, 2 magnetometers and GPS, logged the IMU at 50 Hz to SD, and streamed CRC-checked packets to the ground over an RFD900 radio.'),
                ('', 'After the low velocity estimate on the first flight, I compared 3 replacement designs in replay and chose a complementary filter that blends the barometer with the IMU.'),
                ('', 'To keep the flash stall out of flight, I changed the firmware to write flash only on the ground.'),
                ('', 'I tracked down the magnetometer short that had hidden the IMU.'),
            ]) + '\n            <h3>COSMOS ground station</h3>\n            ' + ul([
                ('', 'The radio, the flight computer on USB, a GPS tracker and the weather station each get their own Python process, which parses its stream and feeds a React page over WebSockets.'),
                ('', 'The page shows flight state, altitude, position and alarms, and speaks flight callouts. The same parser drives a terminal view for launch day.'),
                ('', 'Every session goes into a hash-chained log (each entry is tied to the one before, so any change shows) that can be verified and replayed afterwards.'),
                ('', 'Operator commands are rate limited, and the ones that change settings need confirmation. The tests run in CI on every push.'),
            ])),
        ],
        figures=[dict(embed='havoc2-flight3d.html', ratio=1.15,
                      title='The same flight in 3D at true scale: drag or use the arrow keys to turn it, and replay it',
                      cap="The same flight in 3D, at true scale and relative to the pad, drawn from the same logs and with the same rules: solid lines are measured and dashed lines modelled, with the climb in ink and the descent in orange. The faint line on the grid is its track over the ground. Drag, or use the arrow keys, to turn it, and replay it to follow the rocket at 4 times real speed."),
                 # built by figures/havoc2/build_states.py from HAVOC-fc's flight_state.h/.cpp (501495c); not the
                 # Mugara report's diagram, which disagrees with the code (notes: mugara-diagrams-check-2026-11-18.md)
                 dict(embed='havoc2-states.html', ratio=3.6, wide=True,
                      title="State diagram of HAVOC-2's flight-phase detector, with the threshold for each transition",
                      cap="The flight-phase detector in HAVOC-2's firmware as of October 2026, which I redesigned after the first flight and tuned on its logs and bench captures. It reports the phase in telemetry and fires nothing. |a| is the IMU's measured acceleration magnitude in g, relative to its own reading at rest, sampled at 50 Hz, and v is the vertical velocity from the filter that blends the barometer with the IMU."),
                 dict(embed='cosmos-architecture.html', ratio=1.85,
                      title='Block diagram of COSMOS: one server per device, feeding the React page, the sim service and a hash-chained session log',
                      cap='How I put COSMOS together, as the code stands: one server process per device, one WebSocket per server for telemetry and commands, and a hash-chained session log that can be verified and replayed.'),
                 dict(embed='cosmos-replay.html', ratio=1.75,
                      title='Live replica of the COSMOS header, flight phases and altitude chart, replaying its synthetic demo flight',
                      cap="A small live replica of COSMOS's status pills, flight phases, altitude chart and event log, rebuilt for the site in COSMOS's own style. It replays COSMOS's built-in synthetic demo flight: made-up physics, not a real rocket. Pause it, change the speed or drag the slider.")],
        after=[
            ('Result', ul([
                ('', 'On its first flight, in July 2026, HAVOC-2 flew as the data recorder on a sub-scale rocket that reached about 540 m after an 11.7 g boost.'),
                ('', 'On the replayed flight log, the new estimator cut false speed on the pad from a peak of 137 m/s to 0.37 m/s, and with sensor faults injected it never called apogee early.'),
                ('', "At the 2026 Australian Universities Rocket Competition, COSMOS recorded flight computer data from the launch rail and, about 3 hours before launch, ran a 512-run OpenRocket Monte Carlo ensemble from the weather station's pressure and wind to predict the apogee spread and the landing footprint."),
            ])),
            ('What went wrong', ul([
                ('Brownout:', 'HAVOC-2 browned out at ejection on the first flight. Logging resumed, but about 9 s of the descent went unrecorded while it rebooted.'),
                ('Low velocity estimate:', 'on the first flight the onboard velocity estimate read about 5 times too low.'),
                ('Flash stall:', 'erasing the onboard flash stalled the clock for 225 ms every 5 s.'),
                ('Magnetometer short:', 'a shorted magnetometer breakout took down the I2C bus and hid the IMU behind it.'),
                ('No flight data yet:', 'the new estimator sat on the launch rail at the 2026 competition, but the rocket broke up 2.8 s into the flight and the nosecone holding the recorders has not been found.'),
            ])),
        ],
        credits="HAVOC-2's board was designed by teammates in the UQ Space avionics team; the page covers its firmware and the ground station.",
    ),
    dict(
        slug='osiris', card=P + 'osiris-icon.svg', card_alt='',
        kicker='Personal project · 2026', title='OSIRIS flight computer', team=False,
        summary="My own flight computer design in KiCad. The V0 bench board's schematic passes KiCad's electrical rules check; its layout check still flags one short I have to fix, and firmware comes after.",
        outcome="My own flight computer design, kept apart from UQ Space's boards as a learning project. The first board, V0, is a 4-layer bench model whose schematic passes KiCad's electrical rules check (ERC) with **0 errors**. Its design rules check (DRC) still flags one short, a power track over a ground pad, which the next revision fixes.",
        tiles=[('63 × 74 mm', '4-layer V0 board'), ('0', 'ERC errors'), ('70', 'parts placed')],
        specs=[('Board', '63 × 74 mm, 4 layers (V0)'), ('Controller', 'Plug-in STM32F411 module'), ('Sensors', 'ISM330IS IMU, BMP581 barometer'), ('Power', 'INA228 monitor, 3.3 V buck, 2S–4S input with fuse, TVS and reverse-polarity FET'), ('Storage', 'microSD'), ('Parts', '70 placed: 52 on top, 18 underneath')],
        board=dict(image=P + 'osiris-v0-top.jpg', alt='Top view of the OSIRIS V0 board with numbered markers on its main parts', parts=[
            ('IMU', 'ISM330IS six-axis IMU', 67.71, 46.54, 'top'),
            ('Barometer', 'BMP581 pressure sensor', 34.46, 46.34, 'top'),
            ('Power monitor', 'INA228 current and voltage monitor', 55.82, 54.28, 'top'),
            ('3.3 V buck', 'TPS54302 regulator with a 4.7 µH inductor', 46.47, 24.99, 'top'),
            ('Battery input', 'XT30, 2S to 4S, behind a fuse, a TVS diode and a reverse-polarity FET', 51.23, 78.78, 'top'),
            ('Module sockets', 'Two 20-pin rows for the plug-in STM32F411 module', 40.77, 49.99, 'top'),
            ('microSD', 'Hirose socket on the underside', 58.29, 28.55, 'bottom'),
        ]),
        facts=[('My role', 'Sole designer'),
               ('When', 'May 2026 – present'),
               ('Tools', 'KiCad, STM32F411, ISM330IS, BMP581, INA228'),
               ('Code', 'Private repository for now')],
        lead=None, board_lead=True, og=P + 'osiris-v0-top.jpg',   # the numbered top view leads the page
        sections=[
            ('The problem', "<p>I wanted to learn flight computer design from the ground up, on a board of my own.</p>"),
            ('What I built', ul([
                ('', 'V0 is a 63 × 74 mm, 4-layer carrier board I designed in KiCad. It takes a plug-in STM32F411 module.'),
                ('', 'The board carries an ISM330IS IMU, a BMP581 barometer, an INA228 power monitor, a 3.3 V buck regulator and a microSD socket.'),
                ('', 'A fuse, a TVS diode and a reverse-polarity FET protect the 2S to 4S battery input.'),
                ('', 'The second board is a larger design around a bare STM32H743, with GNSS, Ethernet, 4 pyro channels and an eFuse.'),
            ])),
        ],
        figures=[dict(embed='osiris-v0-ibom.html', ratio=1.6, open=True, wide=True, fixed=True, desktop_only=True,
                      phone_note='The interactive bill of materials needs a wider screen than a phone.',
                      title='Interactive bill of materials for OSIRIS V0: hover a part in the list to light it on the board',
                      cap='Interactive bill of materials (BoM) for V0, generated with my eng-tools kit: hover or click a row to light that part on the board, front and back. 70 parts on 45 BoM lines.'),
                 dict(embed='osiris-v0-kicad.html', ratio=1.5,
                      title='OSIRIS V0 board and schematic in KiCanvas: open either to pan, zoom and select parts',
                      cap="V0's KiCad files, the board and its six schematic sheets, opened in your browser with KiCanvas. Open the board or the schematic to pan, zoom and select parts and nets. The viewer and the files load only when you open one.")],
        after=[
            ('Result', "<p>The second board's schematic passes ERC as well; its routing is unfinished.</p>"),
            ('What went wrong', '<p>A design review found that the USB and battery supplies could fight each other on V0. I work around it with a bench rule for now, and the fix is planned for the next revision.</p>\n'
                                '            <p>The layout check also flags a short: a 0.8 mm VSYS track on the top layer runs over the ground pad of capacitor C7. I missed it when I first claimed the board was clean.</p>'),
            ("What's next", ul([
                ('', 'The next revision separates the USB and battery supplies properly.'),
                ('', 'The VSYS track moves off C7, so the layout check passes too.'),
                ('', 'I have not written firmware for either board yet.'),
            ])),
        ],
        credits=None,
    ),
    dict(
        # Cleared 13 Nov 2026: Isaac confirmed it was done in their own time on their own laptop, with no UQ hours or licences and
        # nothing shared with the RA drone project. Keep the 32-state estimator, the 3.1 m figure and the in-flight drag
        # estimator off the page regardless. Facts: CV chat's other-projects-facts.md, 10 Nov 2026.
        slug='airbrakes', card=P + 'airbrakes-icon.svg', card_alt='The FHC-1 airbrake module, a cylindrical bay with four flaps',
        kicker='UQ Space · simulation study · 2026', title='Airbrake control simulation', team=True,
        summary="Four apogee controllers flown on 200 simulated flights of UQ Space's Hera rocket, after fixing the rocket model they fly on.",
        outcome="A Python simulation for airbrakes that trim a rocket's apogee to a target; I wrote it and its controllers for UQ Space. On the 177 of 200 simulated flights of the team's Hera rocket where a 2,900 m target was reachable, three of the four controllers missed it by about **4 m RMS** (root mean square) with perfect state knowledge, against 21.4 m for bang-bang. Everything is simulation: no airbrake has been built.",
        facts=[('My role', "Wrote the simulation and the controllers, and reviewed the team's original rocket model"),
               ('When', 'Oct 2026 – present'),
               ('Tools', 'Python, RocketPy, OpenRocket, six-degree-of-freedom (6-DOF) Monte Carlo simulation'),
               ('Code', 'Not published')],
        lead=dict(embed='airbrakes-controllers.html', ratio=1.75,
                  title='Apogee miss for each of four controllers on the 177 reachable simulated flights, one dot per flight',
                  cap="Each controller flew the same 200 randomised 6-DOF flights of Hera to a 2,900 m target. Each dot is one of the 177 flights where the target was reachable: 22 fell short even with the brakes shut, and 1 overshot with them fully open. Point at or tap a dot to see that flight under all four controllers. The controllers had perfect state knowledge and the brake drag is an assumed model, so the study compares controllers; it doesn't predict a real flight."),
        sections=[
            ('The problem', "<p>Airbrakes let a rocket shed speed during its coast so it reaches a target apogee instead of overshooting it. Before building any hardware, the team needed to know which controller to fly and what it would take to fly it well.</p>"),
            ('What I did', ul([
                ('', "I fixed the model first: the team's RocketPy model of Hera matched OpenRocket only because several of its errors cancelled. After my fixes I verified it against OpenRocket, and it agrees to within 0.3% on three reference cases. That is model against model, not against a flight."),
                ('', "I wrote four controllers, target solve, PI (proportional-integral), bang-bang and model predictive control (MPC), and flew each on the same 200 randomised 6-DOF flights at 10 Hz, with actuator lag and the competition's deployment rules."),
                ('', '213 test functions in 12 files cover the model and the controllers.'),
            ])),
        ],
        figures=[],
        after=[
            ('Result', "<p>Over the 177 flights where the target was reachable, with the controllers given perfect state knowledge, the RMS miss was 3.7 m for PI, 3.9 m for target solve, 4.0 m for MPC and 21.4 m for bang-bang. The top three are within 0.25 m of each other, so tuning mattered more than the choice of controller.</p>"),
            ('What went wrong', ul([
                ('No brake data yet:', "the brake drag is an assumed flat-plate model, because there is no wind-tunnel or computational fluid dynamics (CFD) data, so the brakes' real authority is uncertain."),
                ('The model flies low:', "real flights of the team's rockets went 2.6 to 5.8% higher than their simulations, so the model needs correcting against flight data before it can predict one."),
            ])),
        ],
        credits="Hera's original RocketPy model and the team's earlier airbrake hardware are teammates' work. The card shows FHC-1, the airbrake module chosen for the team, which has not been built. The page covers the simulation and controllers I wrote.",
        credits_html=("Hera's original <a href=\"https://github.com/RocketPy-Team/RocketPy\" target=\"_blank\" rel=\"noopener\">RocketPy</a> (MIT) model and the team's earlier airbrake hardware are teammates' work. "
                      "The card shows FHC-1, the airbrake module chosen for the team, which has not been built. The page covers the simulation and controllers I wrote."),
    ),
    dict(
        slug='digital-orrery', card=P + 'orrery-icon.svg', card_alt='Schematic of an Earth to Mars transfer arc around the Sun',
        kicker='Personal project · 2025–26', title='Digital orrery and transfer planner', team=False,
        summary="A solar system and transfer planner I built for the browser in TypeScript and JavaScript. Its transfer solver gave no bad arcs across a 14,240-cell Earth to Mars grid.",
        outcome="A 3D solar system and mission-planning simulator I built, which runs in the browser. I verified its orbital mechanics core against NASA/JPL's CSPICE toolkit, and its porkchop planner runs on a Lambert solver that gives **no bad arcs** across a 14,240-cell Earth to Mars grid.",
        tiles=[('130', 'automated checks pass'), ('0 of 14,240', 'bad Lambert arcs'), ('≈1e-14', 'agreement with CSPICE')],
        facts=[('My role', 'Sole developer'),
               ('When', 'Jun 2025 – present'),
               ('Tools', 'TypeScript, React, Three.js, Vite, astronomy-engine, NASA SPICE (CSPICE and DE442), Web Workers'),
               # the orrery itself is live as a Pages project site (Isaac's OK via the Digital orrery chat, 19 Nov 2026)
               # (repo link first: check_facts reads the first link as the public repo)
               ('Code', '<a href="https://github.com/Zyzzbarth333/digital-orrery" target="_blank" rel="noopener">Public on GitHub</a> (MIT licence) · '
                        '<a href="https://zyzzbarth333.github.io/digital-orrery/" target="_blank" rel="noopener">Open the orrery</a> '
                        '(it streams several hundred megabytes as you explore, so it is heavy on mobile data)')],
        lead=dict(embed='orrery-porkchop.html', ratio=0.95,
                  title='Live launch windows and porkchop plot for Venus, Mars and Jupiter, worked out in your browser by the orrery\'s own trajectory search and Lambert solver',
                  cap="Worked out live in your browser by the orrery's own code, copied unchanged from its public repository. Its trajectory search lists the best direct launch window in each opportunity from 2026 to 2040, for the planet you pick, and picking one draws that window's porkchop. Every Δv is counted the way NASA's Trajectory Browser counts it: injection from a 200 km Earth orbit, plus the burn that slows the craft to escape speed at closest approach to the planet. For Mars in 2026 the best is 4.28 km/s, leaving 1 November on a 310-day arc. Point at or tap the plot, or use its arrow keys, to see any transfer drawn from above the Sun. The table shows NASA's own figure wherever its browser lists the same opportunity, and a dash where it doesn't. Planet positions come from astronomy-engine, the library the orrery uses."),
        sections=[
            ('The problem', '<p>Planning a trip between planets means solving Lambert\'s problem across a grid of launch and arrival dates (a porkchop plot), then flying the result under the gravity of the Sun and planets. Both steps can fail quietly when the numerics are wrong.</p>'),
            ('What I built', ul([
                ('', 'The 3D solar system is a TypeScript and React front end on Three.js and Vite, drawn at true scale and true positions with real lighting: inverse-square sunlight, NASA albedos and eclipse umbra and penumbra.'),
                ('', 'The orbital core has two-body propagation, orbital elements and a universal-variable Lambert solver. Its Kepler propagation and Lambert solver agree with NASA\'s CSPICE (DE442) to between 1e-14 and 1e-13.'),
                ('', 'The porkchop planner runs on that Lambert solver to find launch windows.'),
                ('', 'In the n-body kernel, spacecraft fly under the Sun, 8 planets and the Moon, with a 4th-order Yoshida integrator. The physics is plain JavaScript running in a Web Worker.'),
                ('', 'All 130 automated checks pass, across 4 test files: orbital mechanics, porkchop, n-body and the spacecraft kernel.'),
            ])),
        ],
        figures=[],
        after=[
            ('Mars right now', '''<p class="live-sky">Today Mars is <strong data-live="dist">–</strong> million km from Earth, so light takes <strong data-live="light">–</strong> minutes to cross one way, and it sits <strong data-live="elong">–</strong> from the Sun in our sky.</p>
            <script type="module">
                import * as A from "../assets/vendor/astronomy-engine-2.1.19/astronomy.min.js";
                const set = (k, v) => document.querySelectorAll(`[data-live="${k}"]`).forEach((el) => (el.textContent = v));
                function update() {
                    const t = new Date();
                    const v = A.GeoVector(A.Body.Mars, t, true);
                    const km = Math.hypot(v.x, v.y, v.z) * A.KM_PER_AU;
                    set("dist", (km / 1e6).toFixed(1));
                    set("light", (km / 299792.458 / 60).toFixed(1));
                    set("elong", A.Elongation(A.Body.Mars, t).elongation.toFixed(0) + "°");
                }
                update();
                setInterval(update, 60000);
            </script>'''),
            ('Result', ul([
                ('', 'In a development run on a 14,240-cell Earth to Mars grid, the Lambert solver gave 0 failures and 0 wrong arcs, each checked by an independent adaptive integrator. The automated test runs a 920-cell grid checked the same way.'),
                ('', "Two-body propagation matches NASA/JPL's CSPICE toolkit to 2e-14 on elliptic orbits, 4e-15 on hyperbolic ones and 2.4e-13 near parabolic, and orbital elements match Curtis's worked examples."),
                ('', "On Mars Science Laboratory's real 2011 launch and arrival dates, with DE440 planet states, the planner gives C3 = 10.69 km²/s² for a 253.6-day Type I arc, and astronomy-engine agrees to 1e-4."),
                ('', 'A 400 km Earth orbit flown in the n-body kernel stays within 0.2 km of the two-body solution over a day.'),
            ])),
            ('What went wrong', '<p>Before I hardened the Lambert solver, about 21% of the arcs on the 14,240-cell Earth to Mars grid came out bad, nearly all of them transfers longer than 180°. After hardening, none failed or went wrong.</p>'),
            ("What's next", ul([
                ('', "The integrator's step follows the local dynamical time but has no error control yet."),
                ('', 'The gravity model uses point masses only, with no gravity-field harmonics, solar radiation pressure, drag or relativity yet.'),
                ('', "The Lambert solver is zero-revolution only, and there is no n-body targeting or capture burn yet, so a planned arc doesn't arrive exactly."),
                ('', 'Real surface maps, Cassini-measured Saturn rings and daily NASA imagery of Earth are built on a branch but not merged yet.'),
            ])),
            ('Earlier version', '<p>An earlier Python version, <a href="https://github.com/Zyzzbarth333/interplanetryMissionPlanner" target="_blank" rel="noopener">interplanetryMissionPlanner</a> (2025, archived), is also public.</p>'),
        ],
        credits=None,
    ),
    dict(
        slug='weather-station', card=P + 'weather-station-icon.svg', card_alt='Weather station enclosure design with the lid off, showing the boards inside',
        kicker='Team project · UQ Space · 2026', title='Launch-site weather station', team=True,
        summary='My C++ firmware rewrite for the station that fed wind and pressure into our last pre-launch apogee prediction at the 2026 Australian Universities Rocket Competition. All 98,218 checksummed rows on its memory card passed, bench tests included.',
        outcome='A weather station UQ Space sets up at the launch site, so the pre-flight apogee prediction can use wind and pressure measured on site. I wrote its first design and rewrote most of its firmware. At the 2026 Australian Universities Rocket Competition it logged about 7 hours over 2 days, and all **98,218** checksummed rows on its card, bench tests included, passed.',
        tiles=[('98,218', 'CRC-checked rows, bench tests included, all passed'), ('≈7 h', 'logged at AURC 2026'), ('1 Hz', 'logging rate')],
        specs=[('Controller', 'Arduino Mega 2560'), ('Sensors', 'DFRobot SEN0186 wind and rain kit, BME280'), ('Radio', 'Heltec WiFi LoRa 32 V3, 915 MHz'), ('Logging', 'microSD at 1 Hz; CRC-16 and sequence number on every row'), ('Power', 'USB power bank, 10 to 20 Ah'), ('Enclosure', '3D printed; the Fusion design specifies ASA')],
        facts=[('My role', "Lead avionics engineer. Wrote the first design and parts list, rewrote most of the firmware and sourced the parts. Wrote 30 of the repository's 39 commits. A teammate built the prototype"),
               ('Team', 'UQ Space avionics team'),
               ('When', 'Jun – Oct 2026'),
               ('Tools', 'Arduino Mega, Heltec LoRa (915 MHz), BME280, C++, Fusion 360'),
               ('Code', PRIVATE)],
        lead=(P + 'weather-station-open.jpg', 'Render of the weather station enclosure with the lid off, showing the Arduino Mega, LoRa board and sensors',
              'Enclosure design in Fusion 360, lid off, showing the Arduino Mega (blue), the Heltec LoRa board and the sensors.'),
        sections=[
            ('The problem', "<p>The team's pre-flight apogee prediction needs the wind and pressure at the launch site on the day.</p>"),
            ('What I did', ul([
                ('', 'An Arduino Mega reads a wind and rain kit and a BME280, and writes every sample to SD first.'),
                ('', 'A Heltec LoRa board relays about every second row on 915 MHz to a second board at the ground station.'),
                ('', 'My firmware rewrite appends to the log, keeps sampling and transmitting when the SD card or a sensor drops out, and puts a 16-bit cyclic redundancy check (CRC-16) and a sequence number on every row.'),
                ('', "I built the station's 3D-printed enclosure, which housed it at the 2026 Australian Universities Rocket Competition."),
            ])),
        ],
        figures=[dict(embed='weather-station-exploded.html', ratio=1.2,
                      title='Interactive exploded view of the weather station: hover or focus to take it apart',
                      cap="Hover over or tap a part, or tab in and use the arrow keys, to take the station apart and name each part; the Arduino Mega, which runs the firmware I rewrote, is the board outlined in red. Drawn from the enclosure's Fusion design, with each board where the CAD puts it: the Arduino Mega and the SEN0186 adapter on the floor, the microSD breakout between them, the Heltec LoRa board raised on its headers with its antenna through the lid, and the BME280 on the right wall behind a vent.")],
        after=[
            ('Result', '<p>The station logged at 1 Hz, and its pressure and wind went into our last pre-launch prediction.</p>'),
            ('What went wrong', '<p>The prototype deleted its log on every boot, and a loose SD card or sensor wire stopped the radio as well. Fixing those two faults set the priorities for the rewrite.</p>'),
        ],
        credits='A teammate built the prototype. The station is a UQ Space avionics team project.',
    ),
    dict(
        # Cleared 18 Nov 2026 (CV chat, site.errol): built only from facts.yaml's winter-research-2025 claims and site.errol.
        # Name the School only; never the supervisor, other students, the lab's repo, network setup or IP addresses.
        # The screenshot is cropped to leave out the GPS panel, whose accuracy figures must not be captioned.
        slug='errol', card=P + 'errol-icon.svg', card_alt='',
        kicker='UQ Winter Research Program · 2025', title='Operator tools for Errol, an autonomous research car', team=False,
        summary="Foxglove operator tools for Errol, the UQ School of Mechanical and Mining Engineering's autonomous research car, plus a ROS 2 simulator to test them away from the car.",
        outcome="The operator tools I built for Errol, the UQ School of Mechanical and Mining Engineering's autonomous research car, during the 2025 UQ Winter Research Program: **10** custom TypeScript panels in 4 Foxglove layouts, tested against a simulator of 15 sensor and drive-by-wire topics and used to replay the car's recorded drives.",
        facts=[('My role', 'Winter research student. I built the Foxglove operator tools and a ROS 2 simulator for the car, and fixed two of its LiDAR faults'),
               ('When', 'Jun – Jul 2025'),
               ('Tools', 'TypeScript, Foxglove, ROS 2, Linux (systemd, dnsmasq), Ouster LiDAR'),
               ('Code', 'Private: held by the lab')],
        # The lead starts Lichtblick (the open-source fork of Foxglove, MPL-2.0, built with a small patch) with Isaac's own
        # panels and layout, replaying a real drive: figures/errol/build_lichtblick.py. Isaac chose to publish the built
        # panels (18 Nov 2026); their source stays private.
        lead=dict(embed='errol-lichtblick.html', ratio=1.64, wide=True, fixed=True, open='lichtblick/errol.html',
                  desktop_only=True, phone_note='The replay runs a full desktop app, which needs a wider screen than a phone.',
                  title="Replay of a recorded Errol drive in Lichtblick with my Foxglove panels: GPS array status, LiDAR point cloud around the car, campus map and vehicle dashboard",
                  cap="My Foxglove layout, with my GPS Array Monitor and Vehicle Dashboard panels, running in Lichtblick, the open-source fork of Foxglove, and replaying 45 s of a drive recorded on Errol on 24 July 2025 in real time: the status of the five GNSS receivers, the Ouster LiDAR's point cloud around the car, its track on the campus map, and the speed, gear, steering, indicators, brake and throttle from the drive-by-wire reports. Start it, then press Play; drag the 3D view to turn it. The Layouts menu also has my full three-tab operation layout."),
        og=P + 'errol-foxglove.jpg',
        sections=[
            ('The car', "<p>Errol is a Lexus RX 450h fitted with Ouster OS1-128 and RoboSense BP32 LiDARs, a NovAtel PwrPak7D and four u-blox ZED-F9P GNSS receivers, and PACMod3 drive-by-wire, all on ROS 2.</p>"),   # context facts, facts.yaml winter-research-2025 (18 Nov)
            ('What I did', ul([
                ('', "I built 10 Foxglove panels in TypeScript, arranged in 4 layouts, for the car's LiDAR, GNSS and drive-by-wire data."),
                ('', 'I wrote a ROS 2 simulator of 15 sensor and drive-by-wire topics, so the panels could be tested without the car.'),
                ('', "The Ouster LiDAR driver's buffers were overrunning. I stopped it with a systemd service that switches the CPU out of powersave mode."),
                ('', 'The LiDAR sometimes failed to start. I fixed it by giving the LiDAR a permanent MAC-based DHCP lease through dnsmasq.'),
            ])),
        ],
        figures=[('projects/errol-foxglove.jpg', "The real layout in Foxglove, replaying a drive: a LiDAR point cloud of campus buildings, a street map and the vehicle dashboard panel",
                  "The real layout in Foxglove, replaying one of Errol's drives on the UQ St Lucia campus.")],
        after=[],
        credits="Errol belongs to the UQ School of Mechanical and Mining Engineering. The page covers the tools I built for it during the 2025 UQ Winter Research Program. The replay runs Lichtblick (Mozilla Public License 2.0), and its car model is derived from the Lexus in Autoware's sample vehicle (Apache License 2.0). Map tiles from OpenStreetMap.",
        credits_html=('Errol belongs to the UQ School of Mechanical and Mining Engineering. The page covers the tools I built for it during the 2025 UQ Winter Research Program. '
                      'The replay runs <a href="https://github.com/lichtblick-suite/lichtblick" target="_blank" rel="noopener">Lichtblick</a> v1.31.0 '
                      '(Mozilla Public License 2.0; <a href="../lichtblick/SOURCE.md">its source and my changes</a>), '
                      'and its car model is derived from the Lexus in <a href="https://github.com/autowarefoundation/sample_vehicle_launch" target="_blank" rel="noopener">Autoware\'s sample vehicle</a> (Apache License 2.0). '
                      'Map tiles &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors.'),
    ),
    dict(
        # facts.yaml metr4810 and site.metr4810 (18 Nov 2026). Never: a completed tunnel, the demo scores, the September
        # tendon design, or any steering angle (none on record). Team of 4: role only, no teammate names; the rig,
        # electronics and firmware base are teammates' work, so the test-rig photo (their boards) is left out.
        slug='metr4810', card=P + 'metr4810-icon.svg', card_alt='The steered cutter pod, rendered from its CAD, entering a foam block',
        kicker='METR4810 · team of 4 · 2026', title='A steered cutter pod for a tunnel-boring robot', team=True,
        summary='A tunnel-boring robot for METR4810 at UQ, where a rig pushes an arm through three foam blocks and my steered cutter pod on its end follows the curve.',
        outcome='The machine bored through both end blocks at the final demonstration, but the pod would not steer deep in the bend, so the two passes did not meet; I traced it to an under-torqued steering servo.',
        facts=[('My role', 'Steering and navigation lead in a team of 4; I designed the steered cutter pod'),
               ('When', 'Jul – Oct 2026'),
               ('Tools', 'Fusion 360, 3D printing'),
               ('Files', 'Not published')],
        lead=(P + 'metr4810-pod-section.webp', "Labelled section through the cutter pod: the servo and its gear hood, the hinge on an M6 bolt between bearings, the pod body around its gearmotor, the nose, spindle and cutter head",
              'Section through the pod in Fusion 360: the arm and servo on the left, the steered hinge, then the pod body, its gearmotor and the cutter head.'),
        sections=[
            ('The problem', '<p>A rig pushes an arm through three foam blocks, and the cutter on the end of the arm has to bore a tunnel that follows a curve, so the head must steer as it advances.</p>'),
            ('What I did', ul([
                ('', "I replaced the team's first concept, 18 joints along the arm, with a single steered hinge just behind the cutter."),
                ('', 'I designed the hinge, the servo gear drive and the cutter head in Fusion 360.'),
                ('', "I derived the pod's steering schedule from the tunnel's geometry."),
                ('', 'A week-11 redesign of the cutter head cut its mass from 16.0 g to 6.7 g.'),
            ])),
        ],
        # The bench figure (figures/metr4810/build.mjs, 19 Nov 2026; the team's rig, arm and apparatus model shown with Isaac's OK) tells the outcome above: both end blocks bored, the
        # passes miss, the servo short of torque. Its angles and sizes are illustrative and it states no number.
        figures=([dict(embed='metr4810-bore.html', ratio=1.6,
                      title='Interactive drawing of the machine on the course apparatus, from the CAD: the two boring passes, the steering gauge and the miss',
                      cap="Move or drag across the bench, or tab in and use the arrow keys, to run the two passes. The arm rides straight on the rig's rails, so only the pod's hinge steers. On the gauge, the dashed needle is the steering the bend asks for and the red needle is what the servo held: deep in the bend it stalls at its torque limit, the red stops, so the tunnel runs wide of the dashed bore path. The rig then moves to the far portal for pass 2, and the two tunnel ends pass each other without meeting. Drawn from the CAD: my pod, the team's push rig and arm, and the team's model of the course apparatus. The steering angles are illustrative.")] if METR4810_BENCH else []) + [
                 (P + 'metr4810-pod-render.webp', 'Render of the cutter pod: the black servo and gear hood at the back, the white printed hinge and pod body, and the cutter head at the front',
                  'The pod as designed, rendered in Fusion 360.')],
        after=[
            ('Result', ul([
                ('', 'At the final demonstration the machine bored through both end blocks.'),
                ('', 'The pod would not steer deep in the bend, so the two passes did not meet.'),
            ])),
            ('What went wrong', ul([
                ('Steering torque:', 'my failure analysis traced it to the steering servo, which had too little torque for the side load from cutting.'),
            ])),
        ],
        credits=("METR4810 was a team project at UQ. The rig, the arm, the electronics and the base firmware are teammates' work, and so is the model of the course apparatus; the page covers the cutter pod I designed."
                 if METR4810_BENCH else "METR4810 was a team project at UQ. The rig, the electronics and the base firmware are teammates' work; the page covers the cutter pod I designed."),
    ),
    # The crank arm is coursework only (Isaac, 19 Nov 2026): its write-up lives in the coursework entry below, and
    # projects/crank-arm.html is a redirect to it.
    dict(
        slug='camera-mount', card=P + 'camera-mount-icon.svg', card_alt='Printed black mount holding a white security camera on a timber post',
        kicker='Personal project · 2022', title='Ball joint and mount for a security camera', team=False, earlier=True,
        summary='A 3D-printed replacement for a worn camera mount, designed in Fusion 360, printed and fitted within 4 weeks in mid-2022, then published on Printables.',
        outcome='The ball joint and screw mount on my eufyCam 2C Pro security camera had worn out, so I designed a replacement in Fusion 360 and 3D printed it. From the first sketch to fitting it took under 4 weeks, in mid-2022.',
        tiles=[('2', 'printed parts'), ('1 mm', 'inner-thread offset'), ('PLA', 'Polymaker PolyMAX')],
        specs=[('Parts', 'Ball joint and threaded base'), ('Size', 'Ball joint 21 × 21 × 29 mm; base 40 × 40 × 15 mm'), ('Material', 'Polymaker PolyMAX PLA'), ('Thread', "Metric dimensions for the camera's imperial thread"), ('Files', 'Published on Printables')],
        facts=[('My role', 'Design and print'),
               ('When', 'Jun – Jul 2022'),
               ('Tools', 'Fusion 360, FDM printing, Polymaker PolyMAX PLA'),
               ('Files', '<a href="https://www.printables.com/model/288064-ball-joint-and-mount-for-an-anker-eufycam-2c-pro-w" target="_blank" rel="noopener">On Printables</a>')],
        lead=dict(embed='camera-mount-3d.html', ratio=1.333,
                  title='Interactive 3D model of the two printed parts: drag or use the arrow keys to turn it',
                  cap='The two printed parts in 3D, the slotted ball joint and the threaded base, loaded from the STL files published on Printables. Drag, or tab in and use the arrow keys, to turn them.'),
        og='eufycam.jpg',
        sections=[
            ('What I built', ul([
                ('', 'The parts are printed in Polymaker PolyMAX PLA, which I chose for its strength.'),
                ('', "I converted the camera's imperial outer thread dimensions to metric so the printed part screws onto it."),
                ('', "I tightened the ball joint's groove so the camera holds its position and stops drifting."),
                ('', 'I offset the inner thread by 1 mm so the parts lock tight when screwed together.'),
            ])),
        ],
        figures=[('eufycam.jpg', 'The printed mount holding the camera under a timber eave', 'The printed mount in use, July 2022.')],
        after=[('Result', '<p>The printed mount went into use in July 2022, and the model is published on Printables for anyone with the same camera.</p>')],
        credits=None,
    ),
    dict(
        slug='engg1100', card=P + 'engg1100-icon.svg', card_alt="The team's small four-wheeled firefighting vehicle with a clear electronics cover",
        kicker='First-year team project · 2022', title='Remote-controlled firefighting vehicle', team=True, earlier=True,
        summary='I led a team of 6 and was its only structure designer. We put out 5 of the 6 targets and spent A$140 of the A$200 budget.',
        outcome='My first-year team build for ENGG1100 Professional Engineering at UQ. At the demonstration we put out **5 of the 6** targets, and the vehicle cost **A$140** against a A$200 cap.',
        tiles=[('5 of 6', 'targets put out'), ('A$140', 'of the A$200 cap'), ('6', 'people; I led the team')],
        facts=[('My role', 'Team leader, and the only member of the structure subsystem'),
               ('Team', 'Team of 6'),
               ('When', 'Feb – Jun 2022'),
               ('Tools', 'Fusion 360, 3D printing, Arduino, C++')],
        lead=(P + 'engg1100-vehicle.jpg', 'The vehicle in its final design: two corrugated plastic decks on threaded rods, a clear water reservoir with the pump inside, a hose up to a nozzle on pan-and-tilt servos, and AA cells and an Arduino between the decks',
              "Our team's vehicle with its final design in place, May 2022: two decks on threaded rods, the clear reservoir with the pump inside, the hose up to my printed nozzle on pan-and-tilt servos, and the Arduino and AA cells between the decks."),
        sections=[
            ('The problem', '<p>Build a small remote-controlled vehicle that drives along a test rig and puts out 6 heat-source targets in a run of no more than 5 minutes, using water it carries on board, under an A$200 budget and a 4 kg mass limit.</p>'),
            ('What I did', ul([
                ('', 'For the chassis, I compared 3 materials with a weighted decision matrix and chose 5 mm corrugated polypropylene, which the final vehicle used.'),
                ('', 'I designed and 3D printed several versions of the hose nozzle, trading water use against accuracy and pressure.'),
                ('', "To get past the dead electronics, I rebuilt the first prototype on an Arduino, taught myself enough C++ to drive it by remote control, and built the circuit that links power and control to the drive motors."),
            ])),
        ],
        figures=[(P + 'engg1100-nozzle.jpg', 'Render of several 3D-printed nozzle versions and an angled hose fitting', 'Nozzle versions I designed and printed.')],
        after=[('What went wrong', ul([
                   ('Dead electronics:', "about a week before the milestone the first prototype's motor driver and Pico gave no output, and its back wheels were mounted at different angles."),
                   ('Water tank:', 'the 500 mL reservoir could not hold enough water once the pump displaced some of it. Its 1 L replacement cracked when we drilled it.'),
                   ('Spray:', "the fish-tank pump gave weak, uneven streams, and the printed nozzle's layer lines hurt the spray."),
                   ('On the day:', 'current draw upset one servo, and the pan-and-tilt could not turn a full circle, so we put out 5 of the 6 targets.'),
                   ('Late parts:', 'the pump and hose arrived about a week late.'),
               ]))],
        credits='Built by our team of 6. Design decisions went to a group vote.',
    ),
    dict(
        # Coursework, 18 Nov 2026: the CV chat's pick of 9 (facts.yaml projects, with each entry's "never" rule kept) and
        # the LinkedIn texts it checked. Held: aero4470-reentry (Q12). Skipped: mech3200, engg1700. No marks, no course
        # material, schlieren or facility images, no names. Images: the CV workspace's linkedin-images/, as WebP.
        slug='coursework', card=None, coursework=True,
        kicker='UQ coursework · 2025 – 2026', title='Selected coursework', team=False,
        summary='Nine pieces of coursework from my UQ degree: propulsion, hypersonics, control, robotics, functional safety, computer vision and design for metal 3D printing.',
        outcome='Nine pieces of coursework from my degree at UQ, newest first. Each says whether it was mine alone or a team effort, and what my part was.',
        facts=[('Courses', 'AERO4450, AERO4470, METR6203, METR4202, METR4201, METR3100, ELEC4630, MATE7015'),
               ('When', '2025 – 2026'),
               ('Tools', 'Python, MATLAB and Simulink, ROS 2, fastai, Fusion 360')],
        index=[('Scramjet cycle with nitrous augmentation', 'AERO4450 · 2026'),
               ('Reflected shock tunnel analysis', 'AERO4470 · 2026'),
               ('Cold gas thruster against nozzle theory', 'AERO4450 · 2026'),
               ('Titanium crank arm for metal 3D printing', 'MATE7015 · 2026'),
               ('Control design for three rigs', 'METR6203 · 2025'),
               ('Autonomous exploration and marker search', 'METR4202 · 2025'),
               ('Furuta pendulum balance controller', 'METR4201 · 2025'),
               ('Functional safety case for a LiDAR check', 'METR3100 · 2025'),
               ('Road signs and rice leaf disease', 'ELEC4630 · 2025')],
        lead=None,
        sections=[
            ('Scramjet cycle with nitrous augmentation',
             '<p class="meta">AERO4450 Aerospace Propulsion · 2026 · Part 1 on my own, final report in a team of 2</p>\n'
             "            <p>A 1-D cycle analysis of a scramjet that burns part of its hydrogen with on-board nitrous oxide to keep thrust up at higher Mach numbers. The combustion part was mine alone: in Python I worked out the heat release of hydrogen burning with nitrous oxide, 164.6 MJ/kg. For the final report, where I did most of the work, we built the cycle model and matched the lecture's Mach 10 example to within 7.2% on thrust. Without nitrous the critical Mach number was 10.65; at Mach 13, burning about 11% of the hydrogen with nitrous oxide restored the brief's 0.5 thrust margin. It is a simulation of a fictional scenario.</p>",
             [('coursework/scramjet-margin-isp.webp', 'Two plots against flight Mach number from 8 to 15: thrust margin and specific impulse, each with and without nitrous augmentation',
               'Thrust margin and specific impulse against flight Mach number, with and without augmentation.')]),
            ('Reflected shock tunnel analysis',
             '<p class="meta">AERO4470 Hypersonics · 2026 · my own report on shots taken for our class group</p>\n'
             "            <p>An analysis of shots taken for our class group in UQ's Drummond reflected shock tunnel with a Mach 7 nozzle, at fills of 15 and 85 kPa. In Python I calibrated the wall pressure transducers in place, detected shock arrival automatically and measured shock Mach numbers of 3.676 ± 0.088 and 2.671 ± 0.047, carrying the uncertainty through every step. The measured plate pressures, 6.39 ± 1.15 and 12.39 ± 1.36 kPa, sat within one standard deviation of both the equilibrium and the calorically perfect predictions.</p>",
             [('coursework/shock-tunnel-plate-pressure.webp', 'Two traces of plate pressure against time, one for each fill pressure, with the useful test window shaded on each',
               'Pressure on the test plate at both fills, with the test windows marked.')]),
            ('Cold gas thruster against nozzle theory',
             '<p class="meta">AERO4450 Aerospace Propulsion · 2026 · lab in a group of 8</p>\n'
             '            <p>Firing a small cold gas thruster into back pressures from 1.35 to 81.35 kPa and comparing its thrust with isentropic nozzle theory, using the Summerfield criterion for flow separation. I did most of the analysis and wrote the notebook behind every figure and table, including the thrust-stand calibration (R² 0.995). Measured thrust ran 44 to 86% below theory, and repeat firings scattered by up to 0.8 N, more than the instrument uncertainty.</p>',
             [('coursework/cold-gas-thrust.webp', 'Measured thrust points with error bars well below the falling line of isentropic theory, against back pressure from 0 to 100 kPa',
               'Measured thrust against isentropic nozzle theory across the back-pressure range.')]),
            ('Titanium crank arm for metal 3D printing',
             '<p class="meta">MATE7015 Additive Manufacturing · Sep – Oct 2026 · on my own · Fusion 360, static FEA, FDM printing in ASA</p>\n'
             '            <p>A left bicycle crank arm in Ti-6Al-4V that I designed in Fusion 360 for laser powder bed fusion. At the 1800 N test load my static study peaks at 408 MPa, a safety factor of 2.11, and the arm weighs 251.4 g, 21% lighter than my solid starting design. It is a design only: the titanium arm has not been built.</p>\n'
             '            <p>Crank arms are usually forged, so every length needs its own dies. Printed in titanium, crank length could be a single model parameter, so a rider with a leg-length difference could get a custom arm, if the design suits the process.</p>\n'
             '            ' + ul([
                 ('', 'Crank length is one parameter of the model.'),
                 ('', 'The arm is hollow and needs no supports inside: a closed internal cavity with 2 mm skins and ends 50° above horizontal, so the arm builds upright from the bottom bracket boss with no supports inside it. I chose the process partly for its fine resolution, which the thin skins need.'),
                 ('', 'Two 3.5 mm holes let the unfused powder out. My first holes, in the top skin, raised the peak stress to 591 MPa, so I moved them to the side wall.'),
                 ('', 'In my static study, at the 1800 N fatigue test load from BS EN ISO 4210-8, the peak von Mises stress is 408 MPa, a safety factor of 2.11 on the 860 MPa heat-treated minimum yield.'),
                 ('', "I printed 3 full-size ASA prototypes of earlier versions on my own printer. A 98.7% shrinkage setting brought the last one's bores within 0.3% of the CAD."),
                 ('Over my weight target:', 'at 251.4 g the arm is 76 g heavier than my stretch target, the 175 g Shimano arm.'),
                 ('Not built or tested:', 'the titanium arm exists only as a design and a static study; no fatigue test has been run.'),
             ]),
             [(P + 'crank-arm-section.webp', 'Section along the crank arm showing the closed internal cavity, its thin skins and its angled ends',
               'Section along the arm: the closed internal cavity, its 2 mm skins and the ends angled 50° above horizontal, so it prints without internal supports.'),
              (P + 'crank-arm-render.webp', 'Render of the final crank arm with its two powder-escape holes in the side wall',
               'The final design rendered in Fusion 360 (not built), with the 2 powder-escape holes in the side wall.')]),
            ('Control design for three rigs',
             '<p class="meta">METR6203 Control Engineering 2 · 2025 · two team assignments and one on my own</p>\n'
             '            <p>On a gyro-actuated inverted pendulum I was responsible for the MATLAB and Simulink model, the LQR capture controller and integration, with Stateflow switching between an energy-based swing-up and balance. In simulation it swung up in about 1.1 s and was caught, but we ran out of time to get the swing-up working on the rig. On a Quanser 3-DOF helicopter I built the linearised hover model and the Simulink model that joins the observer, controller and plant, and the controller flew under joystick control. On my own, I designed a state feedback controller and observer for a linearised Whipple bicycle; in simulation its step response overshot by 3.4%.</p>',
             [('coursework/gyro-pendulum-stateflow.webp', 'Stateflow chart with three states, swing up, capture and swing down, and the angle conditions that move between them',
               'The Stateflow logic I wrote for the gyro pendulum: swing up, capture once it is near upright, and swing down to retry.')]),
            ('Autonomous exploration and marker search',
             '<p class="meta">METR4202 Robotics and Automation · 2025 · team of 4</p>\n'
             "            <p>A TurtleBot3 had to explore a map it had never seen and find the ArUco markers placed around it, with nobody driving. It maps with SLAM Toolbox and drives with Nav2. As the team's integration lead I wrote the exploration and recovery side: a frontier detector that scores each frontier by how much unknown space a ray cast says it would reveal, goal ranking and blacklisting, stuck detection with recovery, and a coverage monitor. I made 81 of the team's 101 commits.</p>",
             [('coursework/metr4202-architecture.webp', 'Node diagram: SLAM Toolbox feeds the frontier detector and exploration monitor, which drive a Nav2 controller, alongside ArUco marker detection',
               'How the nodes fit together: mapping, my frontier detector and exploration monitor, marker detection and Nav2.')]),
            ('Furuta pendulum balance controller',
             '<p class="meta">METR4201 Control Engineering 1 · 2025 · on my own, in simulation</p>\n'
             "            <p>Balancing an inverted pendulum on a motor-driven rotating arm. I derived the motor and gearbox model by hand, checked it in MATLAB, and placed a PID controller's zeros on the root locus. In simulation it met the brief's limits of 0.2 s peak time and 20% overshoot, with 0.040 s and 16.3%. An outer PD loop with a low-pass filter then held the arm at its set angle with no drift. It is a simulated design, on the course's nonlinear Simulink model rather than the rig.</p>",
             [('coursework/furuta-step-response.webp', 'Step response of the pendulum angle rising to its set point inside the shaded region allowed by the peak-time and overshoot limits',
               'Simulated step response against the peak-time and overshoot limits.')]),
            ('Functional safety case for a LiDAR check',
             '<p class="meta">METR3100 Control System Implementation · 2025 · team of 5; I did the analysis and wrote the report</p>\n'
             '            <p>A fictional mine wanted a LiDAR check to catch partly dumped ore cars before they derail. Event trees over 249,660 cars a year showed the human supervisor alone still let 8 derailments a year through, and that the LiDAR needed 97.5% detection with a 0.018% false-flag rate, which is SIL 1. A 1oo2 voting design cut derailments to 0.2 a year but used all 365 unnecessary re-dumps the brief allowed. An STPA found 7 unsafe control actions and 16 loss scenarios, and I recommended a 300 ms command timing limit.</p>',
             [('coursework/ore-car-event-tree.webp', 'Event tree from 249,660 ore cars a year through the supervisor and the LiDAR, ending in yearly counts of re-dumps, unnecessary re-dumps and derailments',
               "Event tree for the 1oo2 design over a year of ore cars. Steve is the human supervisor in the course's fictional case.")]),
            ('Road signs and rice leaf disease',
             '<p class="meta">ELEC4630 Computer Vision and Deep Learning · 2025 · on my own</p>\n'
             "            <p>For road signs I built a MATLAB bank of 3,268 templates across 7 sign shapes, found candidates with colour masks and edges, and scored each match on template overlap and chamfer distance; on the course's 10 or so test photos it found the yellow diamond signs more than 90% of the time. On a Kaggle rice leaf disease task in fastai, tuning took a ResNet26d from 88.1% to 97.0%, and my best ConvNeXt Large scored 98.387%, just short of the brief's 98.846% benchmark.</p>",
             [('coursework/rice-lr-finder.webp', 'Loss against learning rate on a log scale, falling to a minimum near 0.1, with two suggested starting points marked',
               'Learning-rate finder for the ConvNeXt classifier, with its suggested starting points.')]),
        ],
        figures=[], after=[],
        credits="Team entries say what my part was; the rest was my teammates'. Course briefs, rigs, the shock tunnel and the course models belong to UQ.",
    ),
]
# Search titles past 60 characters lost the name; meta descriptions past 160 were cut mid-sentence (SEO audit, 19 Nov
# 2026). Each is a shortening of the page's own words, nothing new.
SEO_TITLE = {'errol': 'Errol operator tools and ROS 2 simulator', 'metr4810': 'Steered cutter pod, tunnel-boring robot',
             'camera-mount': 'Security camera ball joint and mount'}
SEO_DESC = {
    'havoc2-cosmos': 'The C++ flight firmware and ground station I built for UQ Space rockets. On the first flight, to about 540 m, every logged frame passed its checksum.',
    'digital-orrery': 'A solar system and transfer planner I built for the browser in TypeScript. Its transfer solver gave no bad arcs across a 14,240-cell Earth to Mars grid.',
    'weather-station': 'My C++ firmware rewrite for the weather station that fed our last pre-launch apogee prediction at the 2026 rocket competition. All 98,218 rows passed.',
    'errol': "Foxglove operator tools for Errol, UQ's autonomous research car, plus a ROS 2 simulator to test them away from the car.",
    'osiris': "My own flight computer design in KiCad. The V0 board's schematic passes KiCad's electrical rules check; its layout check still flags one short to fix.",
}
# Held pages (Theseus VI, eng-tools) live in a private file outside the repo and join only a --drafts build.
_PRIV = Path(os.environ.get('PORTFOLIO_PRIVATE', Path.home() / '.config/portfolio-build')) / 'drafts_private.py'
if _PRIV.exists():
    import importlib.util
    _spec = importlib.util.spec_from_file_location('drafts_private', _PRIV); _mod = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_mod)
    PROJECTS += _mod.DRAFTS
HELD = [p for p in PROJECTS if p.get('draft')]
PROJECTS = [p for p in PROJECTS if DRAFTS or not p.get('draft')]


def svg_size(path):
    """Width and height from an SVG's viewBox, for the img tag."""
    m = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', path.read_text())
    return (round(float(m.group(1))), round(float(m.group(2)))) if m else (600, 600)


def figure(f, prefix, lead=False):
    """f = (src, alt, caption[, interactive_html]). A 4th item makes a wide figure linked to its viewer.
    A dict {'embed', 'title', 'cap', 'ratio'} embeds an interactive figure page from assets/figures/."""
    if isinstance(f, dict) and 'code' in f:
        return f'''        <figure class="figure figure-code">
            <pre><code>{f['code']}</code></pre>
            <figcaption>{E(f['cap'])}</figcaption>
        </figure>
'''
    if isinstance(f, dict):
        cls = 'figure figure-embed' + (' wide' if f.get('wide') else '')
        fixed = ' data-fixed' if f.get('fixed') else ''
        url = f"{prefix}assets/figures/{f['embed']}"
        # desktop_only: an embed that can't work on a phone. Its frame loads (site.js) only on wider screens; phones get a note
        # and a link to open it full size instead.
        desk = f.get('desktop_only')
        src_attr = 'data-src' if desk else 'src'
        # open=True links the figure page full size; a string links that site path instead (e.g. an app the figure starts).
        full = prefix + f['open'] if isinstance(f.get('open'), str) else url
        note = (f'\n            <p class="embed-phone-note">{E(f["phone_note"])} <a class="pill" href="{full}" target="_blank" rel="noopener">Open it full size</a></p>'
                if desk else '')
        return f'''        <figure class="{cls}"{' data-desktop-only' if desk else ''}>
            <iframe {src_attr}="{url}?v={ver('assets/figures/' + f['embed'])}" title="{E(f['title'])}" loading="lazy" style="--ratio:{f['ratio']}"{fixed}></iframe>{note}
            <figcaption>{E(f['cap'])}{(' <a class="fig-open" href="' + full + '" target="_blank" rel="noopener">Open it full size</a>') if f.get('open') else ''}</figcaption>
        </figure>
'''
    src, alt, cap = f[:3]
    link = f[3] if len(f) > 3 else None
    path = REPO / 'assets/img' / src
    w, h = Image.open(path).size if path.suffix != '.svg' else svg_size(path)
    rel = f'{prefix}assets/img/{src}'
    attrs = ' fetchpriority="high"' if lead else ' loading="lazy"'
    cls = 'figure' + (' wide' if link else '') + ('' if lead else ' reveal')
    fig_w = min(w, 480 if h > w else w)
    style = f' style="--fig-w:{fig_w}px"' if fig_w < 832 and not link else ''
    img = f'<img src="{rel}" alt="{E(alt)}" width="{w}" height="{h}"{attrs} decoding="async">'
    if link:
        href = f'{prefix}assets/diagrams/{link}'
        img = f'<a class="fig-link" href="{href}" target="_blank" rel="noopener" aria-label="{E(alt)} (opens the interactive diagram)">{img}</a>'
        cap_html = f'{E(cap)} <a class="fig-open" href="{href}" target="_blank" rel="noopener">Open the interactive diagram</a>'
    else:
        cap_html = E(cap)
    return f'''        <figure class="{cls}"{style}>
            {img}
            <figcaption>{cap_html}</figcaption>
        </figure>
'''


def bold_numbers(p):
    """The outcome sentence, with each **headline number** set in bold."""
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', E(p['outcome']))


def specs_html(p):
    if not p.get('specs'):
        return ''
    rows = ''.join(f'<tr><th scope="row">{E(k)}</th><td>{E(v)}</td></tr>' for k, v in p['specs'])
    return f'            <h2 id="specifications">Specifications</h2>\n            <table class="spec">{rows}</table>\n'


def board_html(p, prefix, lead=False):
    b = p.get('board')
    if not b:
        return ''
    marks = ''.join(
        f'<button type="button" class="bm-mark{" bm-under" if side == "bottom" else ""}" data-part="{i}" style="left:{x}%;top:{y}%" aria-label="{i}. {E(n)}: {E(d)}">{i}</button>'
        for i, (n, d, x, y, side) in enumerate(b['parts'], 1))
    cards = ''.join(
        f'<li class="bm-card" data-part="{i}" tabindex="0"><span class="bm-num">{i}</span><span class="bm-name">{E(n)}</span><span class="bm-detail">{E(d)}</span></li>'
        for i, (n, d, x, y, side) in enumerate(b['parts'], 1))
    w, h = Image.open(REPO / 'assets/img' / b['image']).size
    return f'''            <h2 id="meet-the-board">Meet the board</h2>
            <p>Point at a part, or tab through the list, to find it on V0. Number 7 sits on the underside.</p>
        </div>
        <div class="board-map reveal">
            <div class="bm-figure"><img src="{prefix}assets/img/{b['image']}" alt="{E(b['alt'])}" width="{w}" height="{h}"{' fetchpriority="high"' if lead else ' loading="lazy"'} decoding="async">{marks}</div>
            <ol class="bm-list">{cards}</ol>
        </div>
        <div class="prose">
'''


def slug(h):
    return re.sub(r'[^a-z0-9]+', '-', re.sub(r'<[^>]+>|&[a-z]+;', '', h).lower()).strip('-')


def section_html(pairs):
    """(heading, html) pairs; a third item, a list of figure tuples, puts figures inside that section (coursework)."""
    out = ''
    for h, b, *figs in pairs:
        out += f'            <h2 id="{slug(h)}">{h}</h2>\n            {b}\n'
        out += ''.join(figure(f, '../') for f in (figs[0] if figs else []))
    return out


def on_page(p):
    """Local navigation for a long project page: links to its section headings, in page order."""
    heads = (['Meet the board'] if p.get('board_lead') else []) + [s[0] for s in p['sections']]
    if p.get('specs'): heads.append('Specifications')
    if p.get('board') and not p.get('board_lead'): heads.append('Meet the board')
    heads += [s[0] for s in p['after']]
    if p['credits']: heads.append('Credits')
    links = ''.join(f'<li><a href="#{slug(h)}">{E(h)}</a></li>' for h in heads)
    return f'        <nav class="on-page" aria-label="On this page"><span>On this page:</span><ul>{links}</ul></nav>\n'


def project_page(p, nxt):
    prefix = '../'
    def dd(k, v):
        if k == 'Tools':
            return E(v)
        return v
    wide = {'Press'}   # rows long enough to need the facts box's full width (style.css: .facts div.wide)
    facts = '\n'.join(f'            <div{" class=\"wide\"" if k in wide else ""}><dt>{k}</dt><dd>{dd(k, v)}</dd></div>' for k, v in p['facts'])
    if p.get('board_lead'):   # the board explorer is the page's lead figure
        lead = '        <div class="prose">\n' + board_html(p, prefix, lead=True) + '        </div>\n'
    else:
        lead = figure(p['lead'], prefix, lead=True) if p['lead'] else ''
    figs = ''.join(figure(f, prefix) for f in p['figures'])
    # credits are plain text; credits_html, when set, is trusted HTML so the credits can link their sources (IEEE rule)
    tail = (f'            <h2 id="credits">Credits</h2>\n            <p>{p.get("credits_html") or E(p["credits"])}</p>\n'
            if p['credits'] else '')
    body = f'''    <main id="main" class="project-page">
        <a class="back" href="../index.html#projects">&larr; All projects</a>
        <header class="project-head">
            <h1>{E(p["title"])}</h1>
            <p class="meta">{E(p["kicker"])}</p>
            <p class="outcome">{bold_numbers(p)}</p>
        </header>
        <dl class="facts">
{facts}
        </dl>
{on_page(p)}{lead}        <div class="prose">
{section_html(p["sections"])}{specs_html(p)}{'' if p.get('board_lead') else board_html(p, prefix)}        </div>
{figs}        <div class="prose">
{section_html(p["after"])}{tail}        </div>
        <nav class="page-nav" aria-label="More projects">
            <a class="pill pill-outline" href="../index.html#projects">&larr; All projects</a>
            <a class="pill" href="{nxt["slug"]}.html">Next: {E(nxt["title"])} &rarr;</a>
        </nav>
    </main>
'''
    share = REPO / 'assets/img/projects' / f'{p["slug"]}-share.jpg'
    og = (P + share.name) if share.exists() else p.get('og') or (p['lead'][0] if isinstance(p['lead'], tuple) and not p['lead'][0].endswith('.svg') else 'profile.jpg')
    out = head(f'{SEO_TITLE.get(p["slug"], p["title"])} · Isaac Ziebarth', SEO_DESC.get(p['slug'], p['summary']), prefix,
               og_image=f'assets/img/{og}', path=f'projects/{p["slug"]}.html', extra_css=crumbs_data(p),
               og_alt=f'{p["title"]}: {p["kicker"]}' if share.exists() else p['title']) + header(prefix, 'coursework' if p.get('coursework') else 'projects') + body + footer(prefix)
    (REPO / 'projects').mkdir(exist_ok=True)
    (REPO / 'projects' / f'{p["slug"]}.html').write_text(announce_new_tabs(out))


def icon_svg(rel):
    """Inline a card icon so CSS can animate its parts on hover."""
    svg = (REPO / 'assets/img' / rel).read_text().strip()
    return ' '.join(line.strip() for line in svg.splitlines())


def index_page():
    bio = '\n'.join(f'                <p>{E(t)}</p>' for t in BIO)
    exp = '\n'.join(
        f'                <li><span><span class="role">{E(r)}</span><span class="org">{E(o)}</span></span><span class="when">{E(w)}</span></li>'
        for r, o, w in EXPERIENCE)
    # Projects flagged earlier=True (the two oldest) leave the main grid for a smaller Earlier work row under it, so the
    # grid stays the feature card plus six. Their pages, the sitemap and the Next: chain are unchanged.
    main = [p for p in PROJECTS if not p.get('earlier') and not p.get('coursework')]
    older = [p for p in PROJECTS if p.get('earlier')]
    # The coursework page has no card: a compact list under Earlier work links to each of its entries.
    cw = next((p for p in PROJECTS if p.get('coursework')), None)
    cw_list = (f'''            <h3 id="coursework-title" class="earlier-title reveal">Coursework</h3>
            <ul class="coursework-list reveal" aria-labelledby="coursework-title">
''' + '\n'.join(f'                <li><a href="projects/{cw["slug"]}.html#{slug(h)}">{E(h)}</a><span class="meta">{E(m)}</span></li>'
                     for h, m in cw['index']) + '''
            </ul>
''') if cw else ''
    cards = '\n'.join(f'''                <li class="card{' card-wide' if i == 0 else ''} reveal" style="--i:{i % 3}">
                    <span class="icon iso" data-theme="light" aria-hidden="true">{icon_svg(p["card"])}</span>
                    <h3><a href="projects/{p["slug"]}.html">{E(p["title"])}</a></h3>
                    <p class="meta">{E(p["kicker"])}</p>
                    <p class="summary">{E(p["summary"])}</p>
                    <span class="pill" aria-hidden="true">Tell me more</span>
                </li>''' for i, p in enumerate(main))
    # The small cards keep the card class, so site.js still plays their icons on hover or focus. No pill: the title's
    # link still covers the whole card.
    small = '\n'.join(f'''                <li class="card reveal" style="--i:{i}">
                    <span class="icon iso" data-theme="light" aria-hidden="true">{icon_svg(p["card"])}</span>
                    <h4><a href="projects/{p["slug"]}.html">{E(p["title"])}</a></h4>
                    <p class="meta">{E(p["kicker"])}</p>
                    <p class="summary">{E(p["summary"])}</p>
                </li>''' for i, p in enumerate(older))
    earlier = f'''            <h3 id="earlier-title" class="earlier-title reveal">Earlier work</h3>
            <ul class="earlier-grid" aria-labelledby="earlier-title">
{small}
            </ul>
''' if older else ''
    body = f'''    <main id="main">
        <section class="hero" aria-labelledby="name-title">
            <img src="assets/img/profile.jpg" alt="Isaac Johan Ziebarth" class="profile-pic" width="800" height="800" fetchpriority="high">
            <h1 id="name-title" class="hero-name">Isaac Johan Ziebarth</h1>
            <p class="tagline">{tagline_html()}</p>
            <p class="hero-proof">My rover team placed <strong>1st of 17</strong> at the 2026 Australian Rover Challenge. I graduate in <strong>2027</strong>.</p>
            <p class="hero-seek">{E(SEEKING)}</p>
            <p class="hero-actions"><a class="pill pill-light" href="#projects">See my projects</a> <a class="pill pill-ghost" href="mailto:{E(EMAIL)}">Email me</a></p>
        </section>
        <section class="section" id="projects" aria-labelledby="projects-title">
            <h2 id="projects-title" class="reveal">Projects</h2>
            <p class="section-intro reveal">My own builds and my part in team projects. Team pages say what I did and credit the rest of the team.</p>
            <ul class="project-grid">
{cards}
            </ul>
{earlier}{cw_list}        </section>
        <section class="section about" id="about" aria-labelledby="about-title">
            <h2 id="about-title" class="reveal">About me</h2>
            <div class="bio reveal">
{bio}
                <p class="tools">{E(TOOLS)}</p>
            </div>
        </section>
        <section class="section band-red" id="experience" aria-labelledby="experience-title">
            <h2 id="experience-title" class="reveal">Experience</h2>
            <ul class="experience reveal">
{exp}
            </ul>
            <p class="edu reveal">{E(EDUCATION)}</p>
        </section>
        <section class="section contact" id="contact" aria-labelledby="contact-title">
            <h2 id="contact-title" class="reveal">Contact</h2>
            <p class="reveal">Email me at <a href="mailto:{EMAIL}">{EMAIL}</a>, or find me on <a href="https://www.linkedin.com/in/isaacjohanziebarth/" target="_blank" rel="noopener">LinkedIn</a>.</p>
        </section>
    </main>
'''
    desc = 'Mechatronic engineering student at UQ who led UQ Space\'s avionics team until November 2026: rover autonomy, rocket avionics and ground stations.'
    (REPO / 'index.html').write_text(announce_new_tabs(head('Isaac Johan Ziebarth · Avionics and rover autonomy', desc, '', extra_css=f'    <link rel="stylesheet" href="assets/css/iso-kit.css?v={ver("assets/css/iso-kit.css")}">\n' + profile_data(desc)) + header('', 'home') + body + footer('')))


def not_found_page():
    # Pages serves 404.html from any path, so links are root-absolute here.
    body = '''    <main id="main" class="project-page">
        <header class="project-head">
            <h1>That page isn't here</h1>
            <p class="outcome">The link may be old, or the page may have moved.</p>
        </header>
        <nav class="page-nav" aria-label="Where next">
            <a class="pill" href="/index.html#projects">See my projects</a>
            <a class="pill pill-outline" href="/index.html">Go to the home page</a>
        </nav>
    </main>
'''
    out = head('Page not found · Isaac Johan Ziebarth', 'Page not found.', '/', path='404.html', noindex=True) + header('/', None) + body + footer('/')
    (REPO / '404.html').write_text(announce_new_tabs(out))


# Pages that moved: the old URL stays as a small redirect, so links and bookmarks keep working.
MOVED = {'crank-arm': ('coursework.html#titanium-crank-arm-for-metal-3d-printing', 'Titanium crank arm for metal 3D printing')}


def moved_pages():
    for slug, (to, title) in MOVED.items():
        (REPO / 'projects' / f'{slug}.html').write_text(f'''<!DOCTYPE html>
<html lang="en-AU">
<head>
    <meta charset="UTF-8">
    <title>{E(title)} · Isaac Johan Ziebarth</title>
    <meta name="robots" content="noindex">
    <link rel="canonical" href="{SITE}/projects/{to}">
    <meta http-equiv="refresh" content="0; url={to}">
</head>
<body>
    <p>This page has moved to <a href="{to}">my coursework</a>.</p>
</body>
</html>
''')


if __name__ == '__main__':
    if not DRAFTS:                         # a normal build removes any draft pages a --drafts build left behind
        for p in HELD:
            (REPO / 'projects' / f"{p['slug']}.html").unlink(missing_ok=True)
    index_page()
    for i, p in enumerate(PROJECTS):
        project_page(p, PROJECTS[(i + 1) % len(PROJECTS)])
    not_found_page()
    moved_pages()
    n_urls = search_files()
    print('wrote index.html, 404.html and', len(PROJECTS), 'project pages; sitemap of', n_urls, 'URLs')
