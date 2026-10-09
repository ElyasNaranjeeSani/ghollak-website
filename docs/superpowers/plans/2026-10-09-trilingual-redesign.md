# Trilingual Website Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single English `index.html` with a gold "warm ledger" landing page served in Persian (`/`), English (`/en/`) and Arabic (`/ar/`), generated from one template.

**Architecture:** `site/template.html` holds markup + CSS + JS with `{{t:key}}` (escaped string), `{{h:key}}` (trusted HTML string) and `{{block:name}}` (Python-rendered repeated blocks) placeholders. `scripts/build-site.py` (stdlib only) loads `site/strings/<lang>.json` + `site/screens.json`, renders each page, and fails loudly on any missing key. Output HTML is committed; GitHub Pages serves it unchanged.

**Tech Stack:** Static HTML/CSS/vanilla JS, Python 3 stdlib (build + unittest), Pillow (screenshot conversion only), Google Fonts.

**Spec:** `docs/superpowers/specs/2026-10-09-trilingual-redesign-design.md`

## Global Constraints

- Formspree endpoint `https://formspree.io/f/xnjrnzjl`, JSON body `{name, email, message}`, email required — unchanged.
- `/privacy-policy.html`, `/tavallod-privacy-policy.html`, `/yadavar-privacy-policy.html` keep URLs and content.
- `content/full-version-benefits.json` is never modified.
- App Store URL: `https://apps.apple.com/us/app/ghollak-persian-english/id544694377`.
- Gold theme everywhere. Works at 360px with no horizontal scroll. Honors `prefers-reduced-motion`.
- Never `git push`.

## Review Focus

- Missing/typoed translation key → build must exit non-zero naming lang + key (never ship a blank).
- `localStorage` throwing (private mode) → overlay still dismissible, no redirect loop.
- Chapter with fewer screens in a language → no empty phone frames, sticky phone still syncs.
- Contact form: same payload; button disabled while sending; status localized.
- Untrusted characters in strings (`<`, `&`, quotes) → escaped by `{{t:}}`.

---

### Task 1: Build script + tests

**Files:** Create `scripts/build-site.py`, `scripts/test_build_site.py`.

- [ ] Tests (unittest, run `python3 -m unittest scripts/test_build_site.py`): `{{t:a.b}}` resolves nested keys and HTML-escapes; `{{h:x}}` inserts raw; `{{block:name}}` calls a registered renderer; missing key raises `BuildError` mentioning lang + key; unknown block raises; `render_page('en')` output has `lang="en" dir="ltr"` and `fa` has `dir="rtl"`; hreflang alternates for all three.
- [ ] Implement `render(template, strings, lang, blocks) -> str`, block renderers (`hero_phones`, `chapters`, `tiles`, `plans`, `lang_switch`, `hreflang`), `main()` writing `index.html` (fa), `en/index.html`, `ar/index.html`. CLI flag `--langs en` limits output.
- [ ] Tests pass; commit.

### Task 2: Screenshot pipeline

**Files:** Create `scripts/prepare-screenshots.py`; output `assets/screens/{en,fa,ar}/*.webp` (660px wide, quality 82).

- [ ] Script takes source dirs per language, converts every PNG to WebP, prints sizes. Sources: subagent output (en, fa extras, ar extras) + Desktop asset folders (existing fa/ar).
- [ ] Run, eyeball one image per language, commit.

### Task 3: Template + English strings

**Files:** Create `site/template.html`, `site/strings/en.json`, `site/screens.json`.

- [ ] Sections per spec: nav, hero (fanned phones, trust row, years counter), chapters (sticky phone desktop / inline swipe row mobile, IntersectionObserver), little-things tiles (inline SVG icons), calendars strip (Intl), plans (3 cards), contact (unchanged logic, strings via `data-*`), footer (policies; Tavallod/Yadavar muted).
- [ ] Build `--langs en`, verify in Chrome at 1440px and 375px, console clean; commit.

### Task 4: Persian + Arabic

**Files:** Create `site/strings/fa.json`, `site/strings/ar.json`; modify template for RTL fonts (Vazirmatn / Markazi Text / IBM Plex Sans Arabic), localized digits, language overlay on `/`.

- [ ] Build all, verify both RTL pages at both widths, overlay first-visit + remembered choice + switcher; commit.

### Task 5: Cleanup + final verification

- [ ] Remove unused `assets/screenshots/`, retire `scripts/prepare-assets.py` (references removed assets).
- [ ] Policy links resolve from all three pages; form payload checked via network request once; whole-branch review; commit.
