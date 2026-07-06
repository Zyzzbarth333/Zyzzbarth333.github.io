# Contributing

This is a personal site, but the workflow is kept simple so changes stay
consistent.

## Working locally

    python -m http.server 8000

Open `http://localhost:8000` and edit `index.html` and `assets/css/style.css`
directly. There is no build step or framework.

## Conventions

- Plain, dependency-light HTML and CSS. Keep external scripts to a minimum.
- Keep `<meta charset="UTF-8">` and the viewport meta in the head.
- Navigation is anchor-based within `index.html`; mark the active nav `<li>`
  with `class="active"`.
- External links use `target="_blank"` with `rel="noopener"`.
- Text files are LF (enforced by `.gitattributes`).

## Adding a project

Copy the commented `.project` block in the Projects section of `index.html` and
put its image in `assets/img/`. To embed a whole repository, add it as a
submodule (see the README).

## Publishing

Commit to `main`. GitHub Pages rebuilds and publishes within about a minute.
