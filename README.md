# Zyzzbarth333.github.io

Personal site published with GitHub Pages at
[zyzzbarth333.github.io](https://zyzzbarth333.github.io). A single static HTML
page with a stylesheet, no build step or framework.

## Structure

| Path | Holds |
|---|---|
| `index.html` | The whole site (Home, Projects, Contact sections) |
| `assets/css/style.css` | Styles |
| `assets/img/` | Images (profile and project photos) |
| `.nojekyll` | Tells Pages to serve the files as-is (no Jekyll build) |

## Local preview

Open `index.html` in a browser, or serve the folder so paths resolve exactly as
they do on Pages:

    python -m http.server 8000

Then visit `http://localhost:8000`.

## Editing

- Everything lives in `index.html`; navigation is anchor-based
  (`#home`, `#projects`, `#contact`) on the one page.
- To add a project, copy the commented `.project` block in the Projects section
  and put its image in `assets/img/`.
- The Contact section shows an email link; a Formspree form template is left
  commented in place if you want a form instead.
- External links use `target="_blank"` with `rel="noopener"`.

## Deployment

Pushing to `main` publishes automatically through GitHub Pages (Settings to
Pages, source: `main`, root). Allow about a minute for the build.

## Featuring other repositories as submodules

Project repositories can be vendored in as git submodules, for example to embed
a project's own pages:

    git submodule add https://github.com/Zyzzbarth333/<repo> projects/<repo>

- GitHub Pages only fetches submodules that are public and referenced over
  HTTPS (as above), not SSH.
- After cloning this repository elsewhere, run
  `git submodule update --init --recursive`.

## Licence

Copyright (c) Isaac Johan Ziebarth. All rights reserved. The code and content of
this site are not licensed for reuse.
