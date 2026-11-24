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

print('ok' if not problems else f'{problems} to look at')
sys.exit(1 if problems else 0)
