"""Compare the site's project pages with the CV chat's facts.yaml (its `site:` mapping).

Usage: python3 -I check_facts.py <facts.yaml> <site-repo>
Reports, per project slug: a missing entry, site_safe false (hold the page back), and
dates or public-repo links that differ, plus notes where a published page names a project whose wording is pending
(facts.yaml pending_terms), and a failure wherever a do_not_claim pattern matches a tracked page. It changes nothing. Exit 1 when anything needs a look; notes alone don't count.
"""
import html as htmllib
import re
import subprocess
import sys
from pathlib import Path

import yaml

facts_path, repo = Path(sys.argv[1]), sys.argv[2]
sys.argv = [sys.argv[0], repo, '--drafts']   # build_site reads the repo path from argv; check draft pages too
sys.path.insert(0, str(Path(__file__).parent))
from build_site import PROJECTS          # noqa: E402  (no pages are written on import)

facts_all = yaml.safe_load(facts_path.read_text())
site = facts_all.get('site', {})


def norm_dates(s):
    s = (s or '').replace(' - ', ' – ').strip()
    m = re.fullmatch(r'(\w{3}) – (\w{3}) (\d{4})', s)          # "Jun – Jul 2022"
    return f'{m[1]} {m[3]} – {m[2]} {m[3]}' if m else s


problems = 0
for p in PROJECTS:
    slug, facts = p['slug'], dict(p['facts'])
    e = site.get(slug)
    if e is None:
        print(f'{slug}: no entry in facts.yaml'); problems += 1; continue
    if not e.get('site_safe'):
        why = e.get('hold') or e.get('note') or 'no reason given'
        print(f'{slug}: HOLD{" (draft page)" if p.get("draft") else ""}, site_safe is false ({why})'); problems += 1
    if e.get('dates') and norm_dates(facts.get('When')) != norm_dates(e['dates']):
        print(f'{slug}: dates differ: site "{facts.get("When")}", facts "{e["dates"]}"'); problems += 1
    code = facts.get('Code', '')
    repo_url = (re.search(r'href="([^"]+)"', code) or [None, None])[1]
    if 'public_repo' in e and (repo_url or None) != (e['public_repo'] or None):
        print(f'{slug}: public repo differs: site {repo_url}, facts {e["public_repo"]}'); problems += 1
    if e.get('check_with'):
        print(f'{slug}: note from facts.yaml: check with {e["check_with"]}')
for slug in sorted(set(site) - {p['slug'] for p in PROJECTS}):
    print(f'{slug}: in facts.yaml but has no page')

# Claims that must never appear (facts.yaml do_not_claim, anywhere in the file): each pattern, case-insensitive, over the
# visible text of every HTML page the repo tracks, figures included. A match is a failure: the claim was dropped for a reason.
def do_not_claim(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'do_not_claim':
                for it in (v if isinstance(v, list) else [v]):
                    if isinstance(it, dict) and (it.get('pattern') or it.get('regex')):
                        yield path, it.get('pattern') or it.get('regex'), it.get('why') or it.get('reason') or ''
                    elif isinstance(it, str):
                        yield path, it, ''
            else:
                yield from do_not_claim(v, f'{path}/{k}')
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from do_not_claim(v, f'{path}/{i}')


def visible(text):
    text = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', text, flags=re.S | re.I)
    return re.sub(r'\s+', ' ', htmllib.unescape(re.sub(r'<[^>]+>', ' ', text)))


r_git = subprocess.run(['git', '-C', repo, 'ls-files', '*.html'], capture_output=True, text=True)
tracked = [f for f in r_git.stdout.split() if not f.startswith('tools/')]   # build templates are not pages
if r_git.returncode or not tracked:   # not a checkout, or no pages added to git: nothing would be scanned, so say so and fail
    print(f'no tracked HTML pages to scan in {repo} ({(r_git.stderr.strip() or "git ls-files found none")[:160]})'); sys.exit(2)
texts = {f: visible((Path(repo) / f).read_text(errors='replace')) for f in tracked}
# The home page's cards, result cubes and rover read their words from a JSON block and from the v4 scripts, which the
# visible-text pass skips; scan those too, so a dropped claim cannot come back through the data (code audit, 19 Nov).
_home = (Path(repo) / 'index.html').read_text(errors='replace')
_data = re.search(r'<script type="application/json" id="data">(.*?)</script>', _home, re.S)
def _strings(o):   # only the words: the data's number arrays (flight logs) would match number patterns by accident
    if isinstance(o, str):
        yield o
    elif isinstance(o, (dict, list)):
        for v in (o.values() if isinstance(o, dict) else o):
            yield from _strings(v)
if _data:
    import json as _json0
    texts['index.html (data)'] = ' | '.join(htmllib.unescape(x) for x in _strings(_json0.loads(_data.group(1))))
for js in sorted((Path(repo) / 'assets/js/v4').glob('*.js')):   # the scripts' string literals, not their code
    lits = re.findall(r"'((?:[^'\\\n]|\\.){6,})'|\"((?:[^\"\\\n]|\\.){6,})\"|`((?:[^`\\]|\\.){6,})`", js.read_text(errors='replace'))
    texts[str(js.relative_to(repo))] = ' | '.join(a or b or c for a, b, c in lits)
for path, pat, why in do_not_claim(facts_all):
    try:
        rx = re.compile(pat, re.I)
    except re.error as err:
        print(f'facts.yaml {path.strip("/")}: do_not_claim pattern {pat!r} does not compile ({err})'); problems += 1; continue
    for f, text in texts.items():
        for m in rx.finditer(text):
            ctx = text[max(0, m.start() - 50):m.end() + 40].strip()
            print(f'{f}: DO-NOT-CLAIM {pat!r} matches "...{ctx}..."' + (f' ({str(why)[:80]})' if why else '')); problems += 1

# Wording still waiting on Isaac's answer: facts.yaml lists pending_terms on some entries. A term on a published page is a
# note, not a failure (a project's own page names it), so nothing new is claimed until the answer comes back.
def pending(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'pending_terms':
                yield path, o.get('pending') or o.get('note') or '', v
            else:
                yield from pending(v, f'{path}/{k}')
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from pending(v, f'{path}/{i}')


pages = {f.name: re.sub(r'<[^>]+>', ' ', f.read_text(errors='replace')) for f in [Path(repo) / 'index.html', *sorted((Path(repo) / 'projects').glob('*.html'))]}
for path, why, terms in pending(facts_all):
    for name, text in pages.items():
        hits = [t for t in terms if re.search(r'\b' + re.escape(t) + r'\b', text, re.I)]
        if hits:
            print(f'{name[:-5]}: note: names {", ".join(hits)}, whose wording waits on Isaac\'s answer (facts.yaml {path.strip("/")}{": " + str(why)[:80] if why else ""}). Add no new "designed" claims here until it is settled.')

# Every number the home page states as a result (the card results and the result cubes) must appear in facts.yaml, so a
# corrected figure there cannot leave a stale one on the home page.
if _data:
    import json as _json
    d = _json.loads(_data.group(1))
    raw = re.sub(r'(?<=\d),(?=\d{3})', '', facts_path.read_text())
    def scope(slug):   # the project's own entries in facts.yaml (site.<slug>, and projects whose id starts with its stem)
        site, proj = facts_all.get('site') or {}, facts_all.get('projects') or {}
        words = [w for w in slug.split('-') if len(w) > 3] or [slug]
        items = proj.items() if isinstance(proj, dict) else [(x.get('id', ''), x) for x in proj if isinstance(x, dict)]
        parts = [site.get(slug)] + [v for k, v in items if k == slug or any(w in str(k) for w in words)]
        txt = '\n'.join(yaml.safe_dump(x, allow_unicode=True) for x in parts if x)
        return re.sub(r'(?<=\d),(?=\d{3})', '', txt) or raw
    shown = [(p.get('slug', '?'), p.get('result') or '', scope(p.get('slug', ''))) for p in d.get('projects', [])]
    shown += [(c.get('key', 'cube'), f"{c.get('label', '')} {c.get('sub', '')}", raw) for c in d.get('cubes', [])]
    norm = lambda t: re.sub(r'\s+', ' ', re.sub(r'(?<=\d),(?=\d{3})', '', t)).lower()
    for who, text, where in shown:
        words, w = norm(text).split(' '), norm(where)
        for i, tok in enumerate(words):
            if not re.match(r'[~≈$a-z]{0,2}\d', tok) or re.match(r'[a-z]{3,}', tok) or re.fullmatch(r'0+', tok):   # figures only (not names like HAVOC-2); a zero is a claim the words carry
                continue
            prev, nxt = (words[i - 1] if i else ''), (words[i + 1] if i + 1 < len(words) else '')
            # the number with a neighbouring word must appear in the project's own facts, so a stray "19" in a date
            # cannot stand in for "of 19"; a long, distinctive number may appear on its own
            ok = any(ph and ph in w for ph in (f'{prev} {tok}'.strip(), f'{tok} {nxt}'.strip())) or (len(re.sub(r'\D', '', tok)) >= 4 and re.sub(r'[^\d.]', '', tok) in w)
            if not ok:
                print(f'index: home number "{tok}" ({who}: "{text.strip()[:60]}") is not in facts.yaml with its context'); problems += 1

print('ok' if not problems else f'{problems} to look at')
sys.exit(1 if problems else 0)
