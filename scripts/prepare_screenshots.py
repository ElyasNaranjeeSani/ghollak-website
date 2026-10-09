#!/usr/bin/env python3
"""
Converts raw app screenshots (1206x2622 PNG from the iOS simulator) into the
web-sized WebP files the site uses, keeping each file's base name:

    python3 scripts/prepare_screenshots.py <lang> <source_dir> [<source_dir> ...]
        -> assets/screens/<lang>/<name>.webp

The phone frame is drawn in CSS, so these are plain screen captures. Run it
by hand whenever screenshots change; it is not part of the page build.

Requires: Pillow (`pip install pillow`)
"""
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Phones render at most ~330 CSS px wide, so this covers 2x displays.
WIDTH = 660
QUALITY = 82


def convert_dir(src_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for name in sorted(os.listdir(src_dir)):
        if not name.lower().endswith(".png"):
            continue
        im = Image.open(os.path.join(src_dir, name)).convert("RGB")
        height = round(im.height * WIDTH / im.width)
        im = im.resize((WIDTH, height), Image.LANCZOS)
        path = os.path.join(out_dir, os.path.splitext(name)[0] + ".webp")
        im.save(path, "WEBP", quality=QUALITY, method=6)
        written.append(path)
    return written


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    lang, sources = argv[0], argv[1:]
    out_dir = os.path.join(ROOT, "assets", "screens", lang)
    for src in sources:
        for path in convert_dir(src, out_dir):
            print(f"{os.path.relpath(path, ROOT)}  {os.path.getsize(path) // 1024} KB")


if __name__ == "__main__":
    main(sys.argv[1:])
