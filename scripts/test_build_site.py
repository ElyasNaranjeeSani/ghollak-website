import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import build_site as bs  # noqa: E402


class RenderTests(unittest.TestCase):
    def test_t_resolves_nested_key_and_escapes(self):
        out = bs.render("<p>{{t:a.b}}</p>", {"a": {"b": "Tom & <Jerry> \"x\""}}, "en", {})
        self.assertEqual(out, "<p>Tom &amp; &lt;Jerry&gt; &quot;x&quot;</p>")

    def test_t_resolves_list_index(self):
        out = bs.render("{{t:items.1}}", {"items": ["a", "b"]}, "en", {})
        self.assertEqual(out, "b")

    def test_h_inserts_raw_html(self):
        out = bs.render("{{h:x}}", {"x": "Simple <em>as</em>"}, "en", {})
        self.assertEqual(out, "Simple <em>as</em>")

    def test_block_calls_renderer_with_strings_and_lang(self):
        blocks = {"greet": lambda s, lang: f"{s['hi']}-{lang}"}
        out = bs.render("[{{block:greet}}]", {"hi": "yo"}, "fa", blocks)
        self.assertEqual(out, "[yo-fa]")

    def test_missing_key_raises_naming_lang_and_key(self):
        with self.assertRaises(bs.BuildError) as cm:
            bs.render("{{t:nav.nope}}", {"nav": {}}, "ar", {})
        self.assertIn("ar", str(cm.exception))
        self.assertIn("nav.nope", str(cm.exception))

    def test_unknown_block_raises(self):
        with self.assertRaises(bs.BuildError):
            bs.render("{{block:ghost}}", {}, "en", {})

    def test_non_string_value_for_t_raises(self):
        with self.assertRaises(bs.BuildError):
            bs.render("{{t:a}}", {"a": {"b": 1}}, "en", {})


class PageTests(unittest.TestCase):
    def make_root(self, langs=("en", "fa", "ar")):
        root = tempfile.mkdtemp()
        os.makedirs(os.path.join(root, "site", "strings"))
        with open(os.path.join(root, "site", "template.html"), "w") as f:
            f.write('<html lang="{{t:_lang}}" dir="{{t:_dir}}"><head>{{block:hreflang}}</head>'
                    "<body>{{t:hello}}</body></html>")
        for lang in langs:
            with open(os.path.join(root, "site", "strings", f"{lang}.json"), "w") as f:
                json.dump({"hello": f"hi-{lang}"}, f)
        with open(os.path.join(root, "site", "screens.json"), "w") as f:
            json.dump({}, f)
        return root

    def test_lang_and_dir_attributes(self):
        root = self.make_root()
        self.assertIn('lang="en" dir="ltr"', bs.render_page("en", root))
        self.assertIn('lang="fa" dir="rtl"', bs.render_page("fa", root))
        self.assertIn('lang="ar" dir="rtl"', bs.render_page("ar", root))

    def test_hreflang_alternates_for_all_languages(self):
        html = bs.render_page("en", self.make_root())
        self.assertIn('hreflang="fa" href="https://ghollak.app/"', html)
        self.assertIn('hreflang="en" href="https://ghollak.app/en/"', html)
        self.assertIn('hreflang="ar" href="https://ghollak.app/ar/"', html)
        self.assertIn('hreflang="x-default" href="https://ghollak.app/"', html)

    def test_build_writes_output_paths(self):
        root = self.make_root()
        bs.build(["fa", "en", "ar"], root)
        self.assertIn("hi-fa", open(os.path.join(root, "index.html")).read())
        self.assertIn("hi-en", open(os.path.join(root, "en", "index.html")).read())
        self.assertIn("hi-ar", open(os.path.join(root, "ar", "index.html")).read())

    def test_build_subset_leaves_other_pages_alone(self):
        root = self.make_root()
        bs.build(["en"], root)
        self.assertFalse(os.path.exists(os.path.join(root, "index.html")))


class BlockTests(unittest.TestCase):
    def strings(self, root, lang="en", chapters=None):
        os.makedirs(os.path.join(root, "assets", "screens", lang), exist_ok=True)
        for name in ("a", "b", "c"):
            open(os.path.join(root, "assets", "screens", lang, name + ".webp"), "w").close()
        return {
            "_lang": lang, "_root": root,
            "_screens": {"hero": {lang: ["a", "b", "c"]},
                         "chapters": {"one": {lang: chapters or ["a", "b"]}, "two": {lang: ["c"]}}},
            "screens": {"a": "Alt A", "b": "Alt B", "c": "Alt C"},
            "chapters": {"items": [
                {"id": "one", "kicker": "K1", "title": "T1", "body": "B1", "ticks": ["x"]},
                {"id": "two", "kicker": "K2", "title": "T2", "body": "B2", "ticks": ["y"]},
            ]},
        }

    def test_chapters_render_one_mark_and_one_phone_per_listed_screen(self):
        html = bs.block_chapters(self.strings(tempfile.mkdtemp()), "en")
        self.assertEqual(html.count('class="mark"'), 3)
        self.assertEqual(html.count('class="phone"'), 3)
        self.assertNotIn('src=""', html)

    def test_stage_lists_each_screen_once(self):
        html = bs.block_stage(self.strings(tempfile.mkdtemp(), chapters=["a", "c"]), "en")
        self.assertEqual(html.count("<img"), 2)

    def test_missing_screen_file_raises(self):
        s = self.strings(tempfile.mkdtemp(), chapters=["a", "zz"])
        s["screens"]["zz"] = "Alt"
        with self.assertRaises(bs.BuildError) as cm:
            bs.block_chapters(s, "en")
        self.assertIn("zz", str(cm.exception))

    def test_missing_alt_text_raises(self):
        s = self.strings(tempfile.mkdtemp())
        del s["screens"]["b"]
        with self.assertRaises(bs.BuildError):
            bs.block_chapters(s, "en")

    def test_chapter_without_screens_for_language_raises(self):
        s = self.strings(tempfile.mkdtemp())
        s["_screens"]["chapters"]["two"] = {}
        with self.assertRaises(bs.BuildError):
            bs.block_chapters(s, "en")

    def test_chapter_numbers_use_persian_digits_in_fa(self):
        html = bs.block_chapters(self.strings(tempfile.mkdtemp(), lang="fa"), "fa")
        self.assertIn("۰۱", html)

    def test_localize_digits(self):
        self.assertEqual(bs.localize_digits("14+", "fa"), "۱۴+")
        self.assertEqual(bs.localize_digits("14+", "ar"), "١٤+")
        self.assertEqual(bs.localize_digits("14+", "en"), "14+")

    def test_lang_switch_marks_current_and_links_all(self):
        html = bs.block_lang_switch({}, "ar")
        self.assertIn('href="/en/"', html)
        self.assertIn('href="/"', html)
        self.assertIn('aria-current="true" data-lang="ar"', html)

    def test_store_badge_links_to_app_store_with_localized_text(self):
        s = {"store_badge": {"kicker": "دانلود از", "store": "اپ‌استور"}}
        html = bs.block_store_badge(s, "fa")
        self.assertIn('href="https://apps.apple.com/us/app/ghollak-persian-english/id544694377"', html)
        self.assertIn("اپ‌استور", html)

    def test_overlay_only_on_persian_root(self):
        s = {"picker": {"title": "t", "note": "n"}}
        self.assertIn("lang-picker", bs.block_lang_overlay(s, "fa"))
        self.assertEqual(bs.block_lang_overlay(s, "en"), "")


if __name__ == "__main__":
    unittest.main()
