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
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://ghollak.app"
# Ghollak has been on the App Store since 2012; the page JS keeps this current too.
LAUNCH_YEAR = 2012

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

NATIVE_NAMES = {"fa": "فارسی", "en": "English", "ar": "العربية"}
DIGITS = {"fa": "۰۱۲۳۴۵۶۷۸۹", "ar": "٠١٢٣٤٥٦٧٨٩"}
# Rendered size of every screenshot WebP (see scripts/prepare_screenshots.py).
SHOT_W, SHOT_H = 660, 1435

# 24px stroke icons for the "little things" tiles, keyed by the tile's "icon".
ICONS = {
    "widgets": '<rect x="3" y="3" width="8" height="8" rx="2"/><rect x="13" y="3" width="8" height="8" rx="2"/><rect x="3" y="13" width="18" height="8" rx="2"/>',
    "lock": '<rect x="4" y="10" width="16" height="11" rx="2.5"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/><circle cx="12" cy="15.5" r="1.2"/>',
    "palette": '<path d="M12 3a9 9 0 1 0 0 18c1.1 0 1.6-.8 1.6-1.6 0-.9-.7-1.3-.7-2.2 0-.9.7-1.6 1.6-1.6H17a4 4 0 0 0 4-4C21 6.8 17 3 12 3Z"/><circle cx="7.5" cy="11" r="1"/><circle cx="10" cy="7" r="1"/><circle cx="15" cy="7.5" r="1"/>',
    "cloud": '<path d="M7 18a4.5 4.5 0 0 1-.6-9A6 6 0 0 1 18 8.5 4.75 4.75 0 0 1 17.5 18Z"/><path d="M12 15v-4m-2 2 2-2 2 2"/>',
    "currency": '<circle cx="9" cy="9" r="6"/><path d="M15.2 9.3A6 6 0 1 1 9.3 15.2"/><path d="M9 6.5v5M7.5 8h2.25a1 1 0 0 1 0 2H8"/>',
    "tag": '<path d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9Z"/><circle cx="8" cy="8" r="1.5"/>',
    "folder": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/>',
    "calculator": '<rect x="5" y="2.5" width="14" height="19" rx="2.5"/><rect x="8" y="5.5" width="8" height="3.5" rx="1"/><path d="M8.5 13h.01M12 13h.01M15.5 13h.01M8.5 17h.01M12 17h.01M15.5 17h.01"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "price": '<path d="M3 17l5-5 4 4 8-8"/><path d="M14 8h6v6"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "percent": '<path d="M19 5 5 19"/><circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="17" r="2.5"/>',
}


def localize_digits(value, lang):
    digits = DIGITS.get(lang)
    if not digits:
        return value
    return "".join(digits[int(c)] if c.isdigit() else c for c in value)


def screen_list(strings, lang, section, key=None):
    table = lookup(strings, f"_screens.{section}", lang)
    if key is not None:
        table = table.get(key, {})
    names = table.get(lang)
    if not names:
        where = f"{section}.{key}" if key else section
        raise BuildError(f"[{lang}] no screenshots listed for {where} in site/screens.json")
    return names


def shot_img(strings, lang, name, eager=False):
    path = os.path.join(strings.get("_root", ROOT), "assets", "screens", lang, name + ".webp")
    if not os.path.exists(path):
        raise BuildError(f"[{lang}] screenshot file missing: assets/screens/{lang}/{name}.webp")
    alt = text(strings, f"screens.{name}", lang)
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="/assets/screens/{lang}/{name}.webp" alt="{esc(alt)}" '
            f'width="{SHOT_W}" height="{SHOT_H}" {loading} decoding="async" data-shot="{name}" />')


def phone(inner, extra_class=""):
    cls = f"phone {extra_class}".strip()
    return f'<div class="{cls}"><div class="phone-screen">{inner}</div></div>'


def block_hreflang(strings, lang):
    links = [f'<link rel="alternate" hreflang="{code}" href="{SITE_URL}{info["path"]}" />'
             for code, info in LANGS.items()]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/" />')
    return "\n  ".join(links)


def block_lang_switch(strings, lang):
    links = []
    for code, info in LANGS.items():
        current = ' aria-current="true"' if code == lang else ""
        links.append(f'<a href="{info["path"]}" lang="{code}" hreflang="{code}"{current} '
                     f'data-lang="{code}">{NATIVE_NAMES[code]}</a>')
    return "".join(links)


def block_lang_overlay(strings, lang):
    # Only the Persian root greets first-time visitors with a choice; /en/
    # and /ar/ were already chosen by whoever followed that link.
    if lang != "fa":
        return ""
    buttons = "".join(
        f'<a class="lang-choice" href="{info["path"]}" lang="{code}" data-lang="{code}">'
        f'{NATIVE_NAMES[code]}</a>' for code, info in LANGS.items())
    return (f'<div class="lang-picker" role="dialog" aria-modal="true" aria-labelledby="lang-picker-title" hidden>'
            f'<div class="lang-picker-card">'
            f'<img src="/assets/icons/ghollak-icon.png" alt="" width="64" height="64" />'
            f'<p id="lang-picker-title" class="lang-picker-title">{esc(text(strings, "picker.title", lang))}'
            f'<span lang="en">Choose your language</span><span lang="ar">اختر لغتك</span></p>'
            f'<div class="lang-choices">{buttons}</div>'
            f'<p class="lang-picker-note">{esc(text(strings, "picker.note", lang))}</p>'
            f'</div></div>')


APP_STORE_URL = "https://apps.apple.com/us/app/ghollak-persian-english/id544694377"
APPLE_LOGO = ('<path d="M16.37 1.43c0 1.14-.49 2.27-1.18 3.08-.74.9-1.99 1.57-2.99 1.57-.12 0-.23-.02-.3-.03-.01-.06'
              '-.04-.22-.04-.39 0-1.15.57-2.27 1.21-2.98.8-.94 2.14-1.64 3.25-1.68.03.13.05.28.05.43zm4.56 15.71c-.03.07'
              '-.46 1.58-1.52 3.12-.94 1.34-1.94 2.71-3.43 2.71-1.52 0-1.9-.88-3.63-.88-1.7 0-2.3.91-3.67.91-1.38 0-2.33'
              '-1.26-3.43-2.8-1.29-1.82-2.32-4.63-2.32-7.28 0-4.28 2.8-6.55 5.55-6.55 1.45 0 2.68.95 3.6.95.87 0 2.22'
              '-1.01 3.9-1.01.61 0 2.89.06 4.37 2.19-.13.09-2.38 1.37-2.38 4.19 0 3.26 2.85 4.42 2.96 4.45z"/>')


def block_store_badge(strings, lang):
    return (f'<a class="store-badge" href="{APP_STORE_URL}" target="_blank" rel="noopener">'
            f'<svg viewBox="0 0 24 24" aria-hidden="true">{APPLE_LOGO}</svg>'
            f'<span><small>{esc(text(strings, "store_badge.kicker", lang))}</small>'
            f'<strong>{esc(text(strings, "store_badge.store", lang))}</strong></span></a>')


def block_hero_phones(strings, lang):
    names = screen_list(strings, lang, "hero")
    if len(names) != 3:
        raise BuildError(f"[{lang}] hero needs exactly 3 screenshots, got {len(names)}")
    left, center, right = names
    return (phone(shot_img(strings, lang, left), "phone-side phone-left")
            + phone(shot_img(strings, lang, center, eager=True), "phone-center")
            + phone(shot_img(strings, lang, right), "phone-side phone-right"))


def block_stage(strings, lang):
    """The sticky phone beside the chapters: every chapter screen, stacked."""
    seen = []
    for item in lookup(strings, "chapters.items", lang):
        for name in screen_list(strings, lang, "chapters", item["id"]):
            if name not in seen:
                seen.append(name)
    imgs = "".join(shot_img(strings, lang, name) for name in seen)
    return phone(imgs, "stage-phone")


def block_chapters(strings, lang):
    out = []
    for i, item in enumerate(lookup(strings, "chapters.items", lang)):
        cid = item["id"]
        names = screen_list(strings, lang, "chapters", cid)
        number = localize_digits(f"{i + 1:02d}", lang)
        ticks = "".join(f"<li>{esc(t)}</li>" for t in item["ticks"])
        marks = "".join(f'<i class="mark" data-shot="{n}"></i>' for n in names)
        phones = "".join(phone(shot_img(strings, lang, n)) for n in names)
        out.append(
            f'<article class="chapter" id="{cid}" style="--shots:{len(names)}">'
            f'<div class="marks" aria-hidden="true">{marks}</div>'
            f'<div class="chapter-copy">'
            f'<p class="chapter-kicker"><span class="chapter-num">{number}</span>{esc(item["kicker"])}</p>'
            f'<h3>{esc(item["title"])}</h3>'
            f'<p class="chapter-body">{esc(item["body"])}</p>'
            f'<ul class="ticks">{ticks}</ul>'
            f'</div>'
            f'<div class="chapter-shots">{phones}</div>'
            f'</article>')
    return "\n".join(out)


def block_tiles(strings, lang):
    out = []
    for tile in lookup(strings, "little.tiles", lang):
        if tile["icon"] not in ICONS:
            raise BuildError(f"[{lang}] unknown tile icon: {tile['icon']}")
        out.append(
            f'<div class="tile reveal"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[tile["icon"]]}</svg>'
            f'<h3>{esc(tile["title"])}</h3><p>{esc(tile["body"])}</p></div>')
    return "\n".join(out)


def block_plans(strings, lang):
    out = []
    for i, card in enumerate(lookup(strings, "plans.cards", lang)):
        featured = "badge" in card
        badge = f'<span class="plan-badge">{esc(card["badge"])}</span>' if featured else ""
        items = "".join(f"<li>{esc(t)}</li>" for t in card["items"])
        out.append(
            f'<div class="plan reveal{" plan-featured" if featured else ""}" style="--i:{i}">{badge}'
            f'<h3>{esc(card["name"])}</h3><p class="plan-tag">{esc(card["tag"])}</p>'
            f'<p class="plan-lead">{esc(card["lead"])}</p><ul class="ticks">{items}</ul></div>')
    return "\n".join(out)


BLOCKS = {
    "hreflang": block_hreflang,
    "lang_switch": block_lang_switch,
    "lang_overlay": block_lang_overlay,
    "hero_phones": block_hero_phones,
    "store_badge": block_store_badge,
    "stage": block_stage,
    "chapters": block_chapters,
    "tiles": block_tiles,
    "plans": block_plans,
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
    strings["_root"] = root
    strings["_native"] = NATIVE_NAMES[lang]
    strings["_years"] = localize_digits(str(date.today().year - LAUNCH_YEAR), lang)
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
