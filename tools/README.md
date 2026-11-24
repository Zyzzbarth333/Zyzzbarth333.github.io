# Build tools

Everything that builds the site from its sources. The pages, styles and figures in the rest of the repo are their
output, so edit these and rebuild rather than editing the output by hand.

| Folder | What it does |
|---|---|
| `site/` | `build_site.py` writes every page's content and head (titles, descriptions, structured data, sitemap); `build_v4.py` then lays the pages out in the v4 design; `make_share.py` draws the 1200 x 630 share cards; `check_facts.py` checks every claim against the facts file; `diagnose.py` is the health check (links, images, accessibility, Lighthouse, HTML, console). |
| `v4/` | The v4 page builders that `build_v4.py` stages and runs: content, the home page, the project pages, the rover arena (`live4-rover.js`), the systems panels, the 3D inset, and their CSS. |
| `figures/` | One builder per interactive figure under `assets/figures/` (the arena map, the flight replay, the porkchop planner, the exploded weather station, the KiCad viewer and so on), and the card icons. |

## Rebuild

```sh
export PORTFOLIO_CONTACT_EMAIL=...          # the contact address the pages show
python3 tools/site/make_share.py .          # only when a card's art, title or result changes
python3 tools/site/build_site.py .
python3 tools/site/build_v4.py .
python3 tools/site/check_facts.py <facts.yaml> .
python3 tools/site/diagnose.py . <out-dir> --headless --facts <facts.yaml>
```

`build_v4.py` reads the pages `build_site.py` just wrote, so always run the two in that order.

## What stays outside the repo

Held pages and anything not for publication live in a private folder, `~/.config/portfolio-build` (or
`$PORTFOLIO_PRIVATE`): `drafts_private.py` (held project pages, joined only by `build_site.py --drafts`),
`icons_private.mjs` (held card icons) and `paths.json` (this machine's paths: the facts file, the Anatomy kit, the
headless driver and the design checker). The tools run without the private folder; they skip what needs it.
