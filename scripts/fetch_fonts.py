#!/usr/bin/env python3
"""Download the website fonts so they are served from GitHub Pages.

Runs in the deploy job, right before publishing docs/. It asks Google Fonts
for the stylesheet once, downloads the woff2 files (latin and latin-ext
only) into docs/fonts/ and writes docs/fonts/fonts.css pointing at them.
Visitors then load the fonts from this site and never contact Google.

Standard library only.
"""
from __future__ import annotations

import hashlib
import re
import sys
import urllib.request
from pathlib import Path

CSS_URL = ("https://fonts.googleapis.com/css2?"
           "family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400"
           "&family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,400..800"
           "&display=swap")
# A modern browser user agent makes Google answer with woff2 files
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
KEEP = {"latin", "latin-ext"}
OUT = Path(__file__).resolve().parent.parent / "docs" / "fonts"


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def main() -> int:
    try:
        css = get(CSS_URL).decode("utf-8")
    except OSError as err:   # never block a deploy over fonts
        print(f"Could not fetch fonts ({err}); the site falls back to system fonts")
        return 0
    # Google prefixes each @font-face with a comment naming its subset
    blocks = re.findall(r"/\* ([\w-]+) \*/\s*(@font-face \{.*?\})", css, re.S)
    if not blocks:
        print("No @font-face blocks found; keeping system fonts")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    out = []
    for subset, block in blocks:
        if subset not in KEEP:
            continue
        url = re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
        name = hashlib.sha1(url.encode()).hexdigest()[:12] + ".woff2"
        if not (OUT / name).exists():
            (OUT / name).write_bytes(get(url))
        out.append(block.replace(url, name))
    (OUT / "fonts.css").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{len(out)} font files ready in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
