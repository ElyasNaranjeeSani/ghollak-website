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


if __name__ == "__main__":
    unittest.main()
