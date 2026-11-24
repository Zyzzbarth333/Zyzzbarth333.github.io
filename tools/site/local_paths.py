"""Machine-specific paths for the build tools, read from a file outside the repo
(~/.config/portfolio-build/paths.json, or $PORTFOLIO_PRIVATE/paths.json). Keys: drive (the headless driver script),
impeccable (the design checker), fonts (the downloaded Chivo Mono files), facts (the facts file the facts gate reads)."""
import json
import os
from pathlib import Path

PRIVATE = Path(os.environ.get('PORTFOLIO_PRIVATE', Path.home() / '.config/portfolio-build'))
_f = PRIVATE / 'paths.json'
_paths = json.loads(_f.read_text()) if _f.exists() else {}


def path(key, default=None):
    v = os.environ.get(f'PORTFOLIO_{key.upper()}') or _paths.get(key) or default
    return Path(v).expanduser() if v else None
