# Contributing

This is a personal site, but changes follow one workflow so the pages stay consistent and every claim stays
checked.

## Workflow

1. Branch from an up-to-date `main`, naming the branch for the change: `feat/...`, `fix/...` or `docs/...`.
2. Change the build script or figure builder that writes the file, not the HTML here, then rebuild.
3. Check before opening a pull request:
   - every claim against the author's verified facts;
   - accessibility (axe, WCAG 2.2 AA), HTML validity, links and Lighthouse;
   - the changed pages at phone width (390 px) and desktop width (1280 px).
4. Open a pull request into `main`, and merge it once the checks pass and the author has approved it.
   GitHub Pages republishes `main` within about a minute.

## Commits

- Headers follow Conventional Commits and complete "If I apply this commit, it will...": lower case after the
  colon, no full stop, for example `fix(figures): the replay's speed button names the speed it shows`.
- Bodies are short paragraphs wrapped near 72 characters: what was wrong, what happens now, and the files or
  values involved.

## Conventions

- Plain, dependency-light HTML, CSS and JavaScript, with every library self-hosted in `assets/vendor/`.
- Every page keeps `<meta charset="UTF-8">` and the viewport meta in its head.
- Colours, fonts and spacing come from the tokens at the top of `assets/css/style.css`. Body text keeps WCAG AA
  contrast (4.5:1).
- Motion is optional. Every animation has a `prefers-reduced-motion` fallback, nothing plays for more than
  5 seconds without a way to stop it, and content never needs JavaScript to become visible.
- Interactive figures work by mouse, touch and keyboard. A tap picks and keeps a value, a vertical swipe still
  scrolls the page, and screen readers get a role and a value, never a bare `role="img"` on something that takes
  input.
- Figure text stays at 10 px or more on a phone, and tables right-align numbers with units in the headers.
- External links use `target="_blank"` with `rel="noopener"`.
- Text files are LF, enforced by `.gitattributes`.

## Content

- Team projects describe the author's own part and credit the team, without naming teammates.
- Every number and claim must match the author's verified facts.
- Photos have all metadata (EXIF, GPS, XMP) stripped before they are added.
- A new project gets a page in `projects/` on the shared template, a card on the home page and an icon in
  `assets/img/projects/`.
