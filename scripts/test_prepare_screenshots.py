import os
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import prepare_screenshots as ps  # noqa: E402


class ConvertTests(unittest.TestCase):
    def test_converts_png_to_webp_at_target_width_keeping_name_and_aspect(self):
        src = tempfile.mkdtemp()
        out = tempfile.mkdtemp()
        Image.new("RGB", (1206, 2622), "white").save(os.path.join(src, "03-store.png"))
        written = ps.convert_dir(src, out)
        path = os.path.join(out, "03-store.webp")
        self.assertEqual(written, [path])
        im = Image.open(path)
        self.assertEqual(im.format, "WEBP")
        self.assertEqual(im.size, (ps.WIDTH, round(2622 * ps.WIDTH / 1206)))

    def test_ignores_non_png_files(self):
        src = tempfile.mkdtemp()
        open(os.path.join(src, "notes.txt"), "w").close()
        self.assertEqual(ps.convert_dir(src, tempfile.mkdtemp()), [])


if __name__ == "__main__":
    unittest.main()
