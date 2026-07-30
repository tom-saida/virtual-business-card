#!/usr/bin/env python3
"""Turn the white-background JPEG logo into a trimmed, transparent PNG.

    ./.venv/bin/python prep_logo.py [source-image]

Naive "make white transparent" leaves a pale halo around the letters, because the
anti-aliased edge pixels are gold blended into white. So we treat white as a matte:
derive alpha from how far each pixel is from white, then un-premultiply the colour
to recover the original gold. Result composites cleanly on black or cream.
"""
import pathlib
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).parent
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "assets/logo-source.png"
dst = ROOT / "logo.png"

im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.float32)

# Distance from white, via the darkest channel (gold's blue channel drops furthest
# from white, so this tracks ink coverage well).
dist = 255.0 - a.min(axis=2)

# The artwork is OPAQUE gold on white, not translucent — and the wordmark carries a
# gradient, so scaling alpha by ink darkness leaves the lighter gold see-through and
# muddy on black. Treat it as a threshold instead: anything clearly not-white becomes
# fully opaque, and only the narrow anti-aliased fringe gets partial alpha.
LO, HI = 6.0, 30.0
alpha = np.clip((dist - LO) / (HI - LO), 0.0, 1.0) * 255.0

# Un-premultiply against the white matte to recover the true ink colour at the
# anti-aliased edges. Solid pixels (alpha 255) come back unchanged.
safe = np.maximum(alpha, 1.0)[..., None]
rgb = (a - (255.0 - alpha)[..., None]) * 255.0 / safe
rgb = np.clip(rgb, 0, 255)

out = np.dstack([rgb, alpha]).astype(np.uint8)
img = Image.fromarray(out)

# Trim the transparent padding, then re-add a small even margin.
bbox = img.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
if bbox:
    img = img.crop(bbox)
pad = max(2, round(img.width * 0.015))
canvas = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
canvas.paste(img, (pad, pad))

canvas.save(dst)
print(f"{src.name} {im.size} -> logo.png {canvas.size} (ratio {canvas.width/canvas.height:.2f})")
