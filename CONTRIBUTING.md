# Contributing

This is a personal site, but the workflow is kept simple so changes stay
consistent.

## Working locally

    python3 -m http.server 8000

Open `http://localhost:8000`. There is no build step on Pages.

## Conventions

- Plain, dependency-light HTML, CSS and JavaScript. Keep external scripts to a
  minimum.
- Keep `<meta charset="UTF-8">` and the viewport meta in every page's head.
- Colours, fonts and spacing come from the tokens at the top of
  `assets/css/style.css`. Body text stays at WCAG AA contrast (4.5:1) on its
  background.
- Motion is optional: every animation has a `prefers-reduced-motion` fallback,
  and content never depends on JavaScript to become visible.
- External links use `target="_blank"` with `rel="noopener"`.
- Text files are LF (enforced by `.gitattributes`).

## Adding a project

Give it a page in `projects/` on the shared template, a card on the home page and
an icon in `assets/img/projects/`. Strip all metadata from photos before adding
them. Every claim on a page should be one the author has checked.

## Publishing

Commit to `main`. GitHub Pages rebuilds and publishes within about a minute.
