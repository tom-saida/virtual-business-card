#!/usr/bin/env python3
"""Download the TTFs the PRINT build needs into fonts/.

    ./.venv/bin/python fetch_fonts.py

The web card loads fonts from Google Fonts at runtime, so it needs nothing here.
The print renderer embeds fonts into the PDF and needs real font files.

Gotcha: Google Fonts serves woff2 to modern browsers, and WeasyPrint is happier
with TTF — so this asks with an ancient User-Agent, which makes the API hand back
truetype URLs instead.
"""
import pathlib
import re
import urllib.request

FONTS = pathlib.Path(__file__).parent / "fonts"
API = ("https://fonts.googleapis.com/css2"
       "?family=Inter:wght@400;700;900&family=JetBrains+Mono:wght@400;500;700")

FONTS.mkdir(exist_ok=True)
req = urllib.request.Request(API, headers={"User-Agent": "Mozilla/4.0"})
css = urllib.request.urlopen(req).read().decode()

got = 0
for block in css.split("@font-face")[1:]:
    fam = re.search(r"font-family: '([^']+)'", block)
    weight = re.search(r"font-weight: (\d+)", block)
    url = re.search(r"url\((https://[^)]+\.ttf)\)", block)
    if not (fam and weight and url):
        continue
    dest = FONTS / f"{fam.group(1).replace(' ', '')}-{weight.group(1)}.ttf"
    if not dest.exists():
        urllib.request.urlretrieve(url.group(1), dest)
    got += 1
    print(f"  {dest.name}")

print(f"{got} font files in {FONTS}")
if not got:
    raise SystemExit("No TTF URLs found — Google Fonts may have changed its response.")
