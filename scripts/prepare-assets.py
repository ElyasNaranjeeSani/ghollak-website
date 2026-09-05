#!/usr/bin/env python3
"""
One-off utility: crops/resizes/compresses the Ghollak app screenshots and
icons (from the user's Desktop) into the web-ready assets committed under
assets/. Not part of any build or deploy process — run manually if the
source screenshots ever change.

WARNING: the files under assets/screenshots/cropped/ have since been
manually touched up (cleaner edges) directly in that folder. Re-running
this script overwrites those files with fresh machine-crops, discarding
that manual cleanup. Only re-run the parts you actually need regenerated.

Requires: Pillow (`pip install pillow`)
"""
from PIL import Image
import os

SRC_DIR = "/Users/elyas/Desktop/Ghollak new screenshots/iPhone final"
ICON_PRO = "/Users/elyas/Desktop/icon-white.jpg"

OUT_GALLERY = "assets/screenshots/gallery"
OUT_CROPPED = "assets/screenshots/cropped"
OUT_ICONS = "assets/icons"

# Bounding box of the phone mockup within the 1320x2868 source canvas,
# measured by scanning for the device bezel's dark pixels. Identical
# across all 9 source images since they share one export template.
CROP_BOX = (79, 431, 1240, 2848)

GALLERY_SIZE = (640, 1391)
CROPPED_SIZE = (680, 1416)
ICON_SIZE = (256, 256)

# (source filename, output basename, needs cropped/phone-only version)
SCREENSHOTS = [
    ("ghollak-screenshot (1) copy 6.png", "all-accounts-en", True),
    ("ghollak-screenshot (1).png", "manage-transactions-en", True),
    ("ghollak-screenshot (1) copy.png", "manage-transactions-fa", True),
    ("ghollak-screenshot (1) copy 9.png", "reminders-en", True),
    ("ghollak-screenshot (1) copy 5.png", "reminders-fa", True),
    ("ghollak-screenshot (1) copy 8.png", "charts-en", True),
    ("ghollak-screenshot (1) copy 3.png", "charts-fa", True),
    ("ghollak-screenshot (1) copy 4.png", "reports-builder-fa", False),
    ("ghollak-screenshot (1) copy 2.png", "export-pdf-excel-fa", True),
]

# Added later, for the hero's Persian/English duo image and the gallery's
# Persian counterpart to all-accounts-en. Lives in a different source
# folder than the rest, so it's handled separately below rather than
# folded into SCREENSHOTS. Used for both the gallery card and the cropped
# phone-only version (unlike reports-builder-fa above, which is gallery-only).
ACCOUNTS_FA_SRC = "/Users/elyas/Desktop/0x0ss (17).png"
ACCOUNTS_FA_BASENAME = "all-accounts-fa"


def save_quantized(im, path):
    im.convert("P", palette=Image.ADAPTIVE, colors=256).save(path, optimize=True)


def main():
    os.makedirs(OUT_GALLERY, exist_ok=True)
    os.makedirs(OUT_CROPPED, exist_ok=True)
    os.makedirs(OUT_ICONS, exist_ok=True)

    for filename, basename, needs_crop in SCREENSHOTS:
        src_path = os.path.join(SRC_DIR, filename)
        im = Image.open(src_path).convert("RGB")

        gallery_im = im.resize(GALLERY_SIZE, Image.LANCZOS)
        save_quantized(gallery_im, os.path.join(OUT_GALLERY, f"{basename}.png"))

        if needs_crop:
            cropped_im = im.crop(CROP_BOX).resize(CROPPED_SIZE, Image.LANCZOS)
            save_quantized(cropped_im, os.path.join(OUT_CROPPED, f"{basename}.png"))

        print(f"done: {basename}")

    accounts_fa = Image.open(ACCOUNTS_FA_SRC).convert("RGB")
    accounts_fa_cropped = accounts_fa.crop(CROP_BOX).resize(CROPPED_SIZE, Image.LANCZOS)
    save_quantized(accounts_fa_cropped, os.path.join(OUT_CROPPED, f"{ACCOUNTS_FA_BASENAME}.png"))
    accounts_fa_gallery_im = accounts_fa.resize(GALLERY_SIZE, Image.LANCZOS)
    save_quantized(accounts_fa_gallery_im, os.path.join(OUT_GALLERY, f"{ACCOUNTS_FA_BASENAME}.png"))
    print(f"done: {ACCOUNTS_FA_BASENAME}")

    pro = Image.open(ICON_PRO).convert("RGB").resize(ICON_SIZE, Image.LANCZOS)
    pro.save(os.path.join(OUT_ICONS, "ghollak-icon.png"), optimize=True)

    print("done: icons")


if __name__ == "__main__":
    main()
