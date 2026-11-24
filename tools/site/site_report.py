"""Local site-health report: one static HTML page from diagnose.py's latest.json, private to this laptop.

Usage: python3 -I site_report.py <out-dir>      (reads <out-dir>/latest.json, writes <out-dir>/report.html)
diagnose.py calls write_report() at the end of every run. The page has no scripts and loads nothing, so it opens
straight from the file and works offline. Every value is escaped.
"""
import html
import json
import sys
from datetime import datetime
from pathlib import Path

E = lambda v: html.escape('—' if v is None or v == '' else str(v))
WORD = {'pass': 'Pass', 'warn': 'Needs a look', 'fail': 'Fail', 'info': 'Note', 'skipped': 'Not run'}
FLOOR = 90                                     # Lighthouse scores below this are flagged (diagnose.py uses the same)


def st(cls, words):
    return f'<span class="st st-{cls}">{E(words)}</span>'


def when(iso):
    try:
        return datetime.fromisoformat(iso).astimezone().strftime('%-d %b %Y, %-I:%M %p')
    except (TypeError, ValueError):
        return iso or '—'


def table(rows, cols, empty='None'):
    """cols: (heading, key, kind) where kind is text, num, path, status, yes, flag, score, impact, kind, link."""
    head = ''.join(f'<th{" class=num" if k in ("num", "score") else ""}>{E(h)}</th>' for h, _, k in cols)
    if not rows:
        return f'<div class="scroll"><table><thead><tr>{head}</tr></thead><tbody><tr><td colspan="{len(cols)}" class="note">{E(empty)}</td></tr></tbody></table></div>'
    body = []
    for r in rows:
        cells = []
        for _, key, kind in cols:
            v = r.get(key)
            if kind == 'num':
                cells.append(f'<td class="num">{E(v if v is not None else "not run")}</td>')
            elif kind == 'path':
                cells.append(f'<td class="path">{E(v)}</td>')
            elif kind == 'status':
                cells.append(f'<td>{st(v, WORD.get(v, v))}</td>')
            elif kind == 'yes':
                cells.append(f'<td>{st("skipped", "not run") if v is None else st("pass" if v else "fail", "Yes" if v else "No")}</td>')
            elif kind == 'flag':
                cells.append(f'<td>{st("fail" if v else "pass", "Present" if v else "None")}</td>')
            elif kind == 'score':
                cells.append('<td class="num">—</td>' if v is None else f'<td class="num">{st("pass" if v >= FLOOR else "warn", v)}</td>')
            elif kind == 'impact':
                cells.append(f'<td>{st("fail" if v in ("critical", "serious") else "warn", v)}</td>')
            elif kind == 'kind':
                cells.append(f'<td>{st("warn" if v == "error" else "info", "Error" if v == "error" else "Warning")}</td>')
            elif kind == 'link':
                c, w = {'ok': ('pass', 'Reachable'), 'blocked': ('info', 'Blocks bots'), 'broken': ('fail', 'Broken'),
                        'error': ('warn', 'Error'), 'timeout': ('warn', 'No answer')}.get(v, ('skipped', 'Not checked'))
                cells.append(f'<td>{st(c, w)}</td>')
            elif kind == 'msg':
                cells.append(f'<td class="msg">{E(v)}</td>')
            else:
                cells.append(f'<td>{E(v)}</td>')
        body.append('<tr>' + ''.join(cells) + '</tr>')
    return f'<div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def chart(history, key, title, unit=''):
    """A small line chart: runs joined point to point, a hairline grid, the latest value at its end, a tooltip per run."""
    pts = [(h['at'], h[key]) for h in history if h.get(key) is not None]
    if not pts:
        return f'<figure class="chart"><figcaption>{E(title)}</figcaption><p class="note">No runs yet</p></figure>'
    W, H, L, R, T, B = 460, 160, 40, 56, 10, 22
    vmax = max(v for _, v in pts) or 1
    top = vmax * 1.15
    step = max(1, round(top / 4 / (10 ** (len(str(int(top))) - 1))) * 10 ** (len(str(int(top))) - 1)) if top >= 4 else 1
    ticks = [i * step for i in range(int(top // step) + 1)]
    top = max(top, ticks[-1])
    n = len(pts)
    x = lambda i: L + (W - L - R) * (i / (n - 1) if n > 1 else 0.5)
    y = lambda v: T + (H - T - B) * (1 - v / top)
    g = ''.join(f'<line x1="{L}" x2="{W - R}" y1="{y(t):.1f}" y2="{y(t):.1f}" class="grid"/><text x="{L - 6}" y="{y(t):.1f}" dy="0.32em" text-anchor="end">{t:,g}</text>' for t in ticks)
    line = ' '.join(f'{x(i):.1f},{y(v):.1f}' for i, (_, v) in enumerate(pts))
    dots = ''.join(f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="{2 if n > 30 else 3.5}"><title>{E(f"{v:,g}{unit} · {when(a)}")}</title></circle>' for i, (a, v) in enumerate(pts))
    first, last = when(pts[0][0]), when(pts[-1][0])
    xl = f'<text x="{L}" y="{H - 5}">{E(first)}</text>' + (f'<text x="{W - R}" y="{H - 5}" text-anchor="end">{E(last)}</text>' if n > 1 else '')
    end = f'<text x="{x(n - 1) + 7:.1f}" y="{y(pts[-1][1]):.1f}" dy="0.32em" class="end">{pts[-1][1]:,g}{E(unit)}</text>'
    label = f'{title} over {n} run{"s" if n != 1 else ""}, latest {pts[-1][1]:,g}{unit}'
    return (f'<figure class="chart"><figcaption>{E(title)}</figcaption><svg viewBox="0 0 {W} {H}" role="img" aria-label="{E(label)}">'
            f'{g}<line x1="{L}" x2="{W - R}" y1="{y(0):.1f}" y2="{y(0):.1f}" class="axis"/><polyline points="{line}" class="line"/>{dots}{end}{xl}</svg></figure>')


CSS = """
:root { --bg: #fbfaf7; --fg: #1f1b2e; --muted: #625c74; --line: #e4e0ea; --ok: #1f7a3d; --warn: #9a6200; --bad: #b42318; --ink: #4f37c8; --tip: #ffffff; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root { --bg: #16141c; --fg: #ece9f4; --muted: #a59fb8; --line: #2f2b3a; --ok: #5fc27f; --warn: #e0a43a; --bad: #f2776b; --ink: #a99af0; color-scheme: dark; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg); font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 72rem; margin: 0 auto; padding: 32px max(16px, 3vw) 48px; display: grid; gap: 36px; }
h1 { font: 400 30px/1.15 Georgia, serif; margin: 0; }
h2 { font-size: 18px; margin: 0 0 8px; }
p { margin: 0; max-width: 70ch; }
.lede { font-size: 18px; margin-top: 8px; }
.note, .meta { color: var(--muted); font-size: 13px; }
.meta { margin-top: 6px; }
section { display: grid; gap: 8px; min-width: 0; }
.scroll { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 14px; font-variant-numeric: tabular-nums; }
th, td { text-align: left; vertical-align: top; padding: 5px 14px 5px 0; border-bottom: 1px solid var(--line); }
th { color: var(--muted); font-weight: 600; font-size: 12.5px; white-space: nowrap; }
.num { text-align: right; }
td.path { overflow-wrap: anywhere; min-width: 12ch; }
td.msg { min-width: 24ch; }
.st { white-space: nowrap; }
.st::before { content: ""; display: inline-block; width: 0.6em; height: 0.6em; margin-right: 0.45em; background: currentColor; vertical-align: 0.02em; }
.st-pass { color: var(--ok); } .st-pass::before { border-radius: 50%; }
.st-warn { color: var(--warn); } .st-warn::before { clip-path: polygon(50% 0, 100% 100%, 0 100%); }
.st-fail { color: var(--bad); }
.st-info, .st-skipped { color: var(--muted); } .st-info::before, .st-skipped::before { background: none; border: 1.5px solid currentColor; border-radius: 50%; }
.charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 320px), 1fr)); gap: 20px; }
.chart { margin: 0; }
.chart figcaption { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.chart svg { width: 100%; height: auto; display: block; }
.chart text { fill: var(--muted); font-size: 11px; }
.chart text.end { fill: var(--fg); }
.chart .grid { stroke: var(--line); }
.chart .axis { stroke: var(--muted); stroke-opacity: 0.5; }
.chart .line { fill: none; stroke: var(--ink); stroke-width: 2; stroke-linejoin: round; }
.chart circle { fill: var(--ink); }
details summary { cursor: pointer; color: var(--muted); }
details[open] summary { margin-bottom: 8px; }
code { font-size: 0.92em; }
"""


def write_report(d, path):
    run = d.get('run', {})
    sec = lambda id_, title, note, inner: (f'<section id="{id_}"><h2>{E(title)}</h2>' + (f'<p class="note">{note}</p>' if note else '') + inner + '</section>')
    parts = [f'''<header><h1>Portfolio Site Health</h1>
<p class="lede">In the latest run, <b>{E(run.get("pass"))}</b> checks passed, <b>{E(run.get("warn"))}</b> were flagged for a look and <b>{E(run.get("fail"))}</b> failed.</p>
<p class="meta">Run at {E(when(run.get("at")))} on commit <code>{E(run.get("commit"))}</code>, with {E(run.get("changed_files"))} files changed since that commit. The run took {E(run.get("seconds"))} s. This page lives only on this laptop.</p></header>''']
    parts.append(sec('checks', 'Checks', '', table(d.get('summary', []), [('Check', 'check', 'text'), ('Status', 'status', 'status'), ('Result', 'detail', 'text')])))
    parts.append(sec('issues', 'Issues', 'Failures first, then things to look at, then notes. A file is relative to the site&#x27;s repo.',
                     table(d.get('issues', []), [('Severity', 'severity', 'status'), ('Check', 'check', 'text'), ('File', 'file', 'path'), ('What', 'message', 'msg')])))
    hist = d.get('history', [])
    parts.append(sec('trend', 'Over time', 'Open issues count failures and things to look at, not notes. Home page weight is its HTML plus every local file it loads. Point at a dot for its run.',
                     '<div class="charts">' + chart(hist, 'issues', 'Open issues per run') + chart(hist, 'home_kb', 'Home page weight per run (KB)', ' KB') + '</div>'))
    parts.append(sec('lighthouse', 'Lighthouse', f'Each page scored as a phone on a slow network and CPU, served locally the way GitHub Pages serves it. Scores under {FLOOR} are flagged; a page under it is run three times and shows the median. A page marked noindex, like the 404 page, gets no SEO score.',
                     table(d.get('lighthouse', []), [('Page', 'page', 'path'), ('Performance', 'performance', 'score'), ('Accessibility', 'accessibility', 'score'),
                                                     ('Best practices', 'best_practices', 'score'), ('SEO', 'seo', 'score'), ('Largest paint (s)', 'lcp_s', 'num'),
                                                     ('Layout shift', 'cls', 'num'), ('Blocking time (ms)', 'tbt_ms', 'num'), ('Runs', 'runs', 'num')], 'Not run')))
    parts.append(sec('axe', 'Accessibility (axe)', 'axe-core&#x27;s WCAG 2.2 AA rules on every page and figure, once every section is revealed. Serious and critical problems count as failures. The third-party board viewer is left out.',
                     table(d.get('axe', []), [('Page', 'page', 'path'), ('Rule', 'rule', 'text'), ('Impact', 'impact', 'impact'), ('Elements', 'nodes', 'num'),
                                              ('What', 'help', 'msg'), ('First element', 'target', 'path')], 'No violations')))
    parts.append(sec('html', 'HTML validity', 'The W3C Nu HTML Checker on every page and figure, except the third-party board viewer.',
                     table(d.get('html_files', []), [('File', 'file', 'path'), ('Errors', 'errors', 'num'), ('Warnings', 'warnings', 'num')], 'Not run')
                     + '<details><summary>Every error and warning</summary>'
                     + table(d.get('html_messages', []), [('File', 'file', 'path'), ('Line', 'line', 'num'), ('Kind', 'kind', 'kind'), ('Message', 'message', 'msg')], 'No errors or warnings')
                     + '</details>'))
    parts.append(sec('links', 'External links', 'Checked with lychee and cached for a day. Some sites, LinkedIn among them, refuse automated checks: those are notes to open by hand, and only a 404 or 410 counts as broken.',
                     table(d.get('external_links', []), [('Link', 'url', 'path'), ('Result', 'result', 'link'), ('Code', 'code', 'num'), ('On', 'pages', 'path')], 'No external links')))
    parts.append(sec('pages', 'Pages', '', table(d.get('pages', []), [('Page', 'page', 'path'), ('HTML (KB)', 'html_kb', 'num'), ('With its files (KB)', 'total_kb', 'num'),
                     ('Local files', 'local_files', 'num'), ('External links', 'external_links', 'num'), ('Console errors', 'console_errors', 'num'),
                     ('Design findings', 'design_findings', 'num'), ('Accessibility issues', 'axe_violations', 'num'), ('HTML errors', 'html_errors', 'num')])))
    parts.append(sec('icons', 'Card icons', 'Checked in headless Chrome with a real pointer: each icon should move while hovered, come to rest within its window after the pointer leaves (the anemometer coasts for about 15 s by design), and stay still for visitors who turn motion off.',
                     table(d.get('icons', []), [('Card', 'card', 'text'), ('Moves on hover', 'moves_on_hover', 'yes'), ('Rests after leaving', 'settles_after_leave', 'yes'),
                                                ('Still with motion off', 'still_reduced', 'yes'), ('Rest window (s)', 'rest_window_s', 'num'), ('Status', 'status', 'status')], 'Not run')))
    parts.append(sec('images', 'Images', 'Every image must carry no EXIF, GPS or XMP metadata. Images over 600 KB are flagged for a look.',
                     table(d.get('images', []), [('Image', 'path', 'path'), ('KB', 'kb', 'num'), ('Width', 'width', 'num'), ('Height', 'height', 'num'),
                                                 ('EXIF', 'exif', 'flag'), ('GPS', 'gps', 'flag'), ('XMP', 'xmp', 'flag'), ('Status', 'status', 'status')])))
    parts.append('<details id="rules"><summary>Design checker findings by rule</summary>'
                 + table(d.get('design_rules', []), [('Rule', 'rule', 'text'), ('Findings', 'count', 'num')]) + '</details>')
    parts.append('<p class="note">Made by site-tools/diagnose.py, which reads the site and never changes it. Run it again to refresh this page.</p>')
    page = (f'<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta name="robots" content="noindex"><title>Portfolio Site Health</title><style>{CSS}</style></head><body><main>{"".join(parts)}</main></body></html>\n')
    Path(path).write_text(page)
    return path


if __name__ == '__main__':
    out = Path(sys.argv[1]).expanduser()
    print('wrote', write_report(json.loads((out / 'latest.json').read_text()), out / 'report.html'))
