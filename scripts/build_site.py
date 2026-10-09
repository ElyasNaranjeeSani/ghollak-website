#!/usr/bin/env python3
"""
Renders the three language versions of the home page from one template:

    site/template.html + site/strings/<lang>.json + site/screens.json
        -> index.html (fa), en/index.html, ar/index.html

Placeholders in the template:
    {{t:dotted.key}}   string from the language file, HTML-escaped
    {{h:dotted.key}}   string inserted as-is (for copy that carries <em> etc.)
    {{block:name}}     markup produced by a renderer in BLOCKS (repeated parts)

Any missing key fails the build with the language and key in the message, so
an untranslated string never ships as a blank. Stdlib only; run from anywhere:

    python3 scripts/build_site.py            # all languages
    python3 scripts/build_site.py en         # just /en/
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://ghollak.app"

# Order here is the order of the language switcher.
LANGS = {
    "fa": {"dir": "rtl", "path": "/"},
    "en": {"dir": "ltr", "path": "/en/"},
    "ar": {"dir": "rtl", "path": "/ar/"},
}

PLACEHOLDER = re.compile(r"\{\{(t|h|block):([A-Za-z0-9_.\-]+)\}\}")


class BuildError(Exception):
    pass


def lookup(strings, key, lang):
    node = strings
    for part in key.split("."):
        if isinstance(node, list) and part.isdigit() and int(part) < len(node):
            node = node[int(part)]
        elif isinstance(node, dict) and part in node:
            node = node[part]
        else:
            raise BuildError(f"[{lang}] missing string: {key}")
    return node


def text(strings, key, lang):
    value = lookup(strings, key, lang)
    if not isinstance(value, str):
        raise BuildError(f"[{lang}] {key} is not a string")
    return value


def esc(value):
    return html.escape(value, quote=True)


def render(template, strings, lang, blocks):
    def substitute(match):
        kind, key = match.groups()
        if kind == "block":
            if key not in blocks:
                raise BuildError(f"[{lang}] unknown block: {key}")
            return blocks[key](strings, lang)
        value = text(strings, key, lang)
        return esc(value) if kind == "t" else value

    return PLACEHOLDER.sub(substitute, template)


# ── blocks ──────────────────────────────────────────────────────────────

def block_hreflang(strings, lang):
    links = [f'<link rel="alternate" hreflang="{code}" href="{SITE_URL}{info["path"]}" />'
             for code, info in LANGS.items()]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/" />')
    return "\n  ".join(links)


BLOCKS = {
    "hreflang": block_hreflang,
}


# ── pages ───────────────────────────────────────────────────────────────

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def render_page(lang, root=ROOT):
    with open(os.path.join(root, "site", "template.html"), encoding="utf-8") as f:
        template = f.read()
    strings = load_json(os.path.join(root, "site", "strings", f"{lang}.json"))
    strings["_lang"] = lang
    strings["_dir"] = LANGS[lang]["dir"]
    strings["_path"] = LANGS[lang]["path"]
    strings["_screens"] = load_json(os.path.join(root, "site", "screens.json"))
    return render(template, strings, lang, BLOCKS)


def output_path(lang, root=ROOT):
    return os.path.join(root, LANGS[lang]["path"].strip("/"), "index.html")


def build(langs, root=ROOT):
    for lang in langs:
        page = render_page(lang, root)
        path = output_path(lang, root)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        print(f"wrote {os.path.relpath(path, root)}")


def main(argv):
    langs = argv or list(LANGS)
    unknown = [lang for lang in langs if lang not in LANGS]
    if unknown:
        sys.exit(f"unknown language(s): {', '.join(unknown)}")
    try:
        build(langs)
    except BuildError as e:
        sys.exit(f"build failed: {e}")


if __name__ == "__main__":
    main(sys.argv[1:])
