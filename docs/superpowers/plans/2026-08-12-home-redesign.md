# Ghollak Home Page Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `index.html`'s home view with real app screenshots, App Store download links for both editions, and copy that reflects the app's actual features, replacing the current content-free green/serif template.

**Architecture:** Single static HTML file (`index.html`) with inline `<style>`/`<script>`, following the existing site's pattern (no build step, no framework). New content is added as additional CSS rules and HTML sections within the same file; nothing is extracted into separate CSS/JS files. Images are pre-processed once (crop/resize/compress) by a one-off Python script and committed as static binary assets under `assets/`.

**Tech Stack:** Plain HTML/CSS/JS. Python 3 + Pillow (already installed) for one-time image asset preparation — not part of any build/deploy pipeline, just used once to produce the committed asset files.

## Global Constraints

- Site stays English-only (no Persian UI strings on the site itself; Persian text inside screenshot images is fine and expected).
- `privacy-policy.html` and `tavallod-privacy-policy.html` must not be modified.
- `content/full-version-benefits.json` must not be modified (in-app remote content, unrelated to the website).
- The contact form's field IDs (`name`, `email`, `message`), field `name` attributes, the `#form-status` element, and the `handleSubmit()` function (including the `fetch('https://formspree.io/f/xnjrnzjl', ...)` call, its JSON payload shape `{ name, email, message }`, and its headers) must remain byte-identical — only their CSS may change.
- App Store links, used exactly as given:
  - Ghollak Mini (free): `https://apps.apple.com/us/app/ghollak-mini-english-%D9%81%D8%A7%D8%B1%D8%B3%DB%8C/id611339401`
  - Ghollak (paid): `https://apps.apple.com/us/app/ghollak-persian-english/id544694377`
- Commit freely at each task boundary; **never run `git push`** — the repo deploys live via GitHub Pages the moment a push happens, and pushing is the user's call only.
- No automated test suite exists for this static site. "Testing" in this plan means: the page must load without console errors, referenced assets must resolve (no 404s), and visual/responsive behavior must be manually confirmed in a browser at the stated breakpoints.

---

## File Structure

- `scripts/prepare-assets.py` — **create**. One-off utility that crops/resizes/compresses the 9 source screenshots and 2 source icons (read from the user's Desktop, outside the repo) into the committed asset files below. Not part of any build process; documents how the assets were derived.
- `assets/screenshots/gallery/*.png` — **create**. 9 files, full marketing-card screenshots (background + baked-in title + phone), resized for the horizontal gallery.
- `assets/screenshots/cropped/*.png` — **create**. 8 files, phone-only crops (background/title removed) of a subset of the same screenshots, used in the hero and spotlight rows.
- `assets/icons/ghollak-mini-icon.png`, `assets/icons/ghollak-icon.png` — **create**. Resized app icons used in the hero download badges.
- `index.html` — **modify**. Rewritten `:root` palette/fonts, nav, hero, new gallery/spotlight/facts sections, restyled (not restructured) contact section, updated footer.

---

### Task 1: Prepare image assets

**Files:**
- Create: `scripts/prepare-assets.py`
- Create (via running the script): `assets/screenshots/gallery/*.png` (9 files), `assets/screenshots/cropped/*.png` (8 files), `assets/icons/ghollak-mini-icon.png`, `assets/icons/ghollak-icon.png`

**Interfaces:**
- Produces: the exact file paths under `assets/` listed above, which every later task references by these exact paths (relative to `index.html`, i.e. `assets/screenshots/gallery/all-accounts-en.png` etc.).

- [ ] **Step 1: Create the asset prep script**

Create `scripts/prepare-assets.py`:

```python
#!/usr/bin/env python3
"""
One-off utility: crops/resizes/compresses the Ghollak app screenshots and
icons (from the user's Desktop) into the web-ready assets committed under
assets/. Not part of any build or deploy process — run manually if the
source screenshots ever change.

Requires: Pillow (`pip install pillow`)
"""
from PIL import Image
import os

SRC_DIR = "/Users/elyas/Desktop/Ghollak new screenshots/iPhone final"
ICON_MINI = "/Users/elyas/Desktop/GhollakMini.png"
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

    mini = Image.open(ICON_MINI).convert("RGB").resize(ICON_SIZE, Image.LANCZOS)
    mini.save(os.path.join(OUT_ICONS, "ghollak-mini-icon.png"), optimize=True)

    pro = Image.open(ICON_PRO).convert("RGB").resize(ICON_SIZE, Image.LANCZOS)
    pro.save(os.path.join(OUT_ICONS, "ghollak-icon.png"), optimize=True)

    print("done: icons")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script from the repo root**

Run: `python3 scripts/prepare-assets.py`
Expected: prints `done: <name>` nine times followed by `done: icons`, with no tracebacks.

- [ ] **Step 3: Verify output counts, sizes, and dimensions**

Run:
```bash
ls assets/screenshots/gallery | wc -l   # expect 9
ls assets/screenshots/cropped | wc -l   # expect 8
ls assets/icons                          # expect ghollak-mini-icon.png, ghollak-icon.png
du -sh assets/                           # expect roughly 3-5M total
python3 -c "from PIL import Image; im = Image.open('assets/screenshots/gallery/all-accounts-en.png'); print(im.size)"
```
Expected: 9 gallery files, 8 cropped files, 2 icon files, total size in the 3-5MB range, and the sampled image reports `(640, 1391)`.

- [ ] **Step 4: Visually spot-check one cropped image**

Open `assets/screenshots/cropped/all-accounts-en.png` and confirm it shows only the phone mockup with no leftover headline text or background gradient band above/below it (a thin sliver of background at the rounded corners is expected and fine).

- [ ] **Step 5: Commit**

```bash
git add scripts/prepare-assets.py assets/
git commit -m "Add web-optimized screenshot and icon assets"
```

---

### Task 2: Foundation — palette, fonts, nav

**Files:**
- Modify: `index.html` (the `<link>` font import, the `:root` CSS block, and the `.nav-links` markup + its mobile media query)

**Interfaces:**
- Produces: CSS custom properties `--accent` (`#2f6fbd`), `--accent-rgb` (`47, 111, 189`), `--accent-dark` (`#24568f`), `--accent-light` (`#e8f1fb`), `--serif` (`'Fraunces', Georgia, serif`), `--sans` (`'Inter', system-ui, sans-serif`) — every later task's CSS relies on these exact variable names.

- [ ] **Step 1: Swap the Google Fonts import**

In `index.html`, replace:
```html
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet" />
```
with:
```html
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
```

- [ ] **Step 2: Replace the `:root` color/font variables**

Replace:
```css
    :root {
      --bg: #faf8f5;
      --surface: #ffffff;
      --ink: #1a1a1a;
      --muted: #7a7570;
      --accent: #2d6a4f;
      --accent-light: #e8f4ee;
      --border: #e8e4df;
      --serif: 'DM Serif Display', Georgia, serif;
      --sans: 'DM Sans', system-ui, sans-serif;
    }
```
with:
```css
    :root {
      --bg: #faf8f5;
      --surface: #ffffff;
      --ink: #1a1a1a;
      --muted: #7a7570;
      --accent: #2f6fbd;
      --accent-rgb: 47, 111, 189;
      --accent-dark: #24568f;
      --accent-light: #e8f1fb;
      --border: #e8e4df;
      --serif: 'Fraunces', Georgia, serif;
      --sans: 'Inter', system-ui, sans-serif;
    }
```

- [ ] **Step 3: Add the Features nav link and allow nav-links to wrap on narrow screens**

Replace:
```html
    <ul class="nav-links">
      <li><a href="/">Home</a></li>
      <li><a href="/privacy-policy.html">Privacy Policy</a></li>
      <li><a href="/tavallod-privacy-policy.html">Tavallod Privacy Policy</a></li>
    </ul>
```
with:
```html
    <ul class="nav-links">
      <li><a href="/">Home</a></li>
      <li><a href="#features">Features</a></li>
      <li><a href="/privacy-policy.html">Privacy Policy</a></li>
      <li><a href="/tavallod-privacy-policy.html">Tavallod Privacy Policy</a></li>
    </ul>
```

Then in the `@media (max-width: 640px)` block, replace:
```css
      .nav-links { gap: 1.25rem; }
```
with:
```css
      .nav-links { gap: 1.25rem; flex-wrap: wrap; }
```

- [ ] **Step 4: Verify the page still loads with the old hero/features markup intact (they'll be replaced in later tasks) and the new palette/fonts are visibly applied**

Run: `python3 -m http.server 8080` from the repo root, then open `http://localhost:8080/` in a browser.
Expected: page renders with no console errors; nav text and any accent-colored elements now show the new blue instead of green; headline font looks different from before (Fraunces instead of DM Serif Display). Stop the server with Ctrl+C when done.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "Switch site palette and fonts to the app's blue identity"
```

---

### Task 3: Rebuild the hero section

**Files:**
- Modify: `index.html` (the `.hero` CSS block and everything through `.hero-pill`, plus the `<section class="hero">` markup)

**Interfaces:**
- Consumes: `--accent`, `--accent-dark`, `--serif`, `--sans` from Task 2; `assets/icons/ghollak-mini-icon.png`, `assets/icons/ghollak-icon.png`, `assets/screenshots/cropped/all-accounts-en.png` from Task 1.
- Produces: `.hero-inner`, `.hero-copy`, `.hero-downloads`, `.store-badge`, `.hero-visual`, `.hero-phone` CSS classes — not reused by later tasks, but keep the names in mind since Task 8's responsive pass touches this block again.

- [ ] **Step 1: Replace the hero CSS block**

Replace this entire block (from `.hero {` through `.hero-pill { ... }`):
```css
    /* ── HERO ── */
    .hero {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 8rem 2rem 4rem;
      position: relative;
      overflow: hidden;
    }

    /* subtle geometric background */
    .hero::before {
      content: '';
      position: absolute;
      inset: 0;
      background:
        radial-gradient(ellipse 60% 50% at 70% 30%, rgba(45,106,79,0.07) 0%, transparent 70%),
        radial-gradient(ellipse 50% 60% at 20% 80%, rgba(45,106,79,0.05) 0%, transparent 60%);
      pointer-events: none;
    }

    .hero-eyebrow {
      font-family: var(--sans);
      font-size: 0.75rem;
      font-weight: 500;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 1.5rem;
      opacity: 0;
      animation: fadeUp 0.6s ease 0.1s forwards;
    }

    .hero h1 {
      font-family: var(--serif);
      font-size: clamp(2.8rem, 7vw, 5.5rem);
      line-height: 1.1;
      letter-spacing: -0.03em;
      color: var(--ink);
      max-width: 700px;
      margin-bottom: 1.5rem;
      opacity: 0;
      animation: fadeUp 0.7s ease 0.2s forwards;
    }

    .hero h1 em {
      font-style: italic;
      color: var(--accent);
    }

    .hero-sub {
      font-size: 1.1rem;
      font-weight: 300;
      color: var(--muted);
      max-width: 420px;
      line-height: 1.7;
      margin-bottom: 3rem;
      opacity: 0;
      animation: fadeUp 0.7s ease 0.35s forwards;
    }

    .hero-cta {
      display: inline-block;
      background: var(--accent);
      color: #fff;
      padding: 0.9rem 2.2rem;
      border-radius: 2rem;
      font-size: 0.9rem;
      font-weight: 500;
      text-decoration: none;
      letter-spacing: 0.02em;
      transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
      opacity: 0;
      animation: fadeUp 0.7s ease 0.5s forwards;
    }
    .hero-cta:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(45,106,79,0.25);
      background: #245c43;
    }

    /* decorative pill */
    .hero-pill {
      position: absolute;
      bottom: 3rem;
      left: 50%;
      transform: translateX(-50%);
      width: 1px;
      height: 60px;
      background: linear-gradient(to bottom, transparent, var(--accent));
      opacity: 0.4;
    }
```
with:
```css
    /* ── HERO ── */
    .hero {
      min-height: 100vh;
      display: flex;
      align-items: center;
      padding: 9rem 2.5rem 4rem;
      position: relative;
      overflow: hidden;
    }

    .hero-inner {
      max-width: 1160px;
      margin: 0 auto;
      width: 100%;
      display: grid;
      grid-template-columns: 1.05fr 0.95fr;
      gap: 3.5rem;
      align-items: center;
    }

    .hero-eyebrow {
      font-family: var(--sans);
      font-size: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 1.5rem;
      opacity: 0;
      animation: fadeUp 0.6s ease 0.1s forwards;
    }

    .hero h1 {
      font-family: var(--serif);
      font-size: clamp(2.6rem, 5vw, 4.2rem);
      line-height: 1.1;
      letter-spacing: -0.02em;
      color: var(--ink);
      margin-bottom: 1.5rem;
      opacity: 0;
      animation: fadeUp 0.7s ease 0.2s forwards;
    }

    .hero h1 em {
      font-style: italic;
      color: var(--accent);
    }

    .hero-sub {
      font-size: 1.1rem;
      font-weight: 400;
      color: var(--muted);
      max-width: 460px;
      line-height: 1.7;
      margin-bottom: 2.5rem;
      opacity: 0;
      animation: fadeUp 0.7s ease 0.35s forwards;
    }

    .hero-downloads {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      opacity: 0;
      animation: fadeUp 0.7s ease 0.5s forwards;
    }

    .store-badge {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      background: #000;
      color: #fff;
      border-radius: 0.85rem;
      padding: 0.6rem 1.2rem 0.6rem 0.6rem;
      text-decoration: none;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .store-badge:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }

    .store-badge-icon {
      width: 2.6rem;
      height: 2.6rem;
      border-radius: 0.6rem;
      display: block;
    }

    .store-badge-text {
      display: flex;
      flex-direction: column;
      line-height: 1.25;
    }

    .store-badge-edition {
      font-family: var(--sans);
      font-size: 0.65rem;
      font-weight: 600;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      opacity: 0.75;
    }

    .store-badge-store {
      font-family: var(--sans);
      font-size: 0.95rem;
      font-weight: 600;
    }

    .hero-visual {
      display: flex;
      justify-content: center;
      opacity: 0;
      animation: fadeUp 0.8s ease 0.3s forwards;
    }

    .hero-phone {
      width: min(320px, 100%);
      height: auto;
      filter: drop-shadow(0 30px 50px rgba(26,26,26,0.18));
    }

    @media (max-width: 900px) {
      .hero-inner { grid-template-columns: 1fr; text-align: center; }
      .hero-sub { margin-left: auto; margin-right: auto; }
      .hero-downloads { justify-content: center; }
      .hero-visual { margin-top: 2.5rem; }
    }
```

- [ ] **Step 2: Replace the hero HTML markup**

Replace:
```html
  <!-- HERO -->
  <section class="hero">
    <p class="hero-eyebrow">Your money, finally clear</p>
    <h1>Personal finance,<br /><em>without the panic.</em></h1>
    <p class="hero-sub">Simple, calm tools to help you understand where your money goes — and feel good about it.</p>
    <a href="#contact" class="hero-cta">Get in touch ↓</a>
    <div class="hero-pill"></div>
  </section>
```
with:
```html
  <!-- HERO -->
  <section class="hero">
    <div class="hero-inner">
      <div class="hero-copy">
        <p class="hero-eyebrow">14 years on the App Store</p>
        <h1>Personal finance,<br /><em>without the panic.</em></h1>
        <p class="hero-sub">Ghollak has been the Persian-speaking world's personal finance app since 2012 — fully bilingual in Persian and English, with support for both the Shamsi and Gregorian calendars.</p>
        <div class="hero-downloads">
          <a class="store-badge" href="https://apps.apple.com/us/app/ghollak-mini-english-%D9%81%D8%A7%D8%B1%D8%B3%DB%8C/id611339401" target="_blank" rel="noopener">
            <img src="assets/icons/ghollak-mini-icon.png" alt="" class="store-badge-icon" />
            <span class="store-badge-text">
              <span class="store-badge-edition">Free — Ghollak Mini</span>
              <span class="store-badge-store">Download on the App Store</span>
            </span>
          </a>
          <a class="store-badge" href="https://apps.apple.com/us/app/ghollak-persian-english/id544694377" target="_blank" rel="noopener">
            <img src="assets/icons/ghollak-icon.png" alt="" class="store-badge-icon" />
            <span class="store-badge-text">
              <span class="store-badge-edition">Pro — Ghollak</span>
              <span class="store-badge-store">Download on the App Store</span>
            </span>
          </a>
        </div>
      </div>
      <div class="hero-visual">
        <img src="assets/screenshots/cropped/all-accounts-en.png" alt="Ghollak showing a list of accounts and their balances in one place" class="hero-phone" />
      </div>
    </div>
  </section>
```

- [ ] **Step 3: Verify in browser at desktop and mobile widths**

Run: `python3 -m http.server 8080` from the repo root, open `http://localhost:8080/`.
Expected: at desktop width, hero shows copy on the left and the phone screenshot on the right, both App Store badges visible with icons and correct labels ("Free — Ghollak Mini" / "Pro — Ghollak"). Resize the browser to ~375px width (or use dev tools device mode): the layout stacks to a single centered column. Click each badge and confirm it opens the correct App Store URL in a new tab. Stop the server with Ctrl+C when done.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "Rebuild hero with App Store download badges and flagship screenshot"
```

---

### Task 4: Screenshot gallery section

**Files:**
- Modify: `index.html` (add new `.gallery-section` CSS block after the hero CSS, and new `<section class="gallery-section">` markup after `</section>` closing the hero)

**Interfaces:**
- Consumes: `--serif`, `--sans`, `--muted`, `--surface`, `--border` from Task 2; all 9 files in `assets/screenshots/gallery/` from Task 1.
- Produces: `id="features"` anchor target, which Task 2's nav link (`href="#features"`) points at — this task is what makes that link actually scroll somewhere.

- [ ] **Step 1: Add the gallery CSS**

Insert this new block immediately after the `@media (max-width: 900px) { ... }` block added in Task 3 (i.e., right before the `/* ── FEATURES STRIP ── */` comment, which the next task will remove):

```css
    /* ── SCREENSHOT GALLERY ── */
    .gallery-section {
      padding: 5rem 0;
      background: var(--surface);
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
    }

    .gallery-heading {
      max-width: 1160px;
      margin: 0 auto 2.5rem;
      padding: 0 2.5rem;
    }

    .gallery-heading h2 {
      font-family: var(--serif);
      font-size: 2rem;
      letter-spacing: -0.02em;
      margin-bottom: 0.5rem;
    }

    .gallery-heading p {
      color: var(--muted);
      font-size: 0.95rem;
    }

    .gallery-track {
      display: flex;
      gap: 1.5rem;
      overflow-x: auto;
      scroll-snap-type: x mandatory;
      padding: 0 2.5rem 1rem;
      -webkit-overflow-scrolling: touch;
    }

    .gallery-track::-webkit-scrollbar { height: 8px; }
    .gallery-track::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

    .gallery-item {
      flex: 0 0 auto;
      width: clamp(170px, 22vw, 220px);
      scroll-snap-align: start;
    }

    .gallery-item img {
      width: 100%;
      height: auto;
      border-radius: 1.5rem;
      box-shadow: 0 16px 32px rgba(26,26,26,0.12);
      display: block;
    }
```

- [ ] **Step 2: Add the gallery markup**

Insert this new section immediately after the hero's closing `</section>` tag (before the `<!-- FEATURES -->` comment/`<div class="features">`, which the next task will remove):

```html
  <!-- GALLERY -->
  <section class="gallery-section" id="features">
    <div class="gallery-heading">
      <h2>Ghollak, in action</h2>
      <p>A closer look at what's inside — in both Persian and English.</p>
    </div>
    <div class="gallery-track">
      <div class="gallery-item"><img src="assets/screenshots/gallery/all-accounts-en.png" alt="All accounts and balances in one place" loading="lazy" /></div>
      <div class="gallery-item"><img src="assets/screenshots/gallery/manage-transactions-en.png" alt="Browsing transactions in a checking account" loading="lazy" /></div>
      <div class="gallery-item"><img src="assets/screenshots/gallery/manage-transactions-fa.png" alt="Managing transactions in Persian" loading="lazy" /></div>
      <div class="gallery-item"><img src="assets/screenshots/gallery/reminders-en.png" alt="Upcoming reminders for bills and checks" loading="lazy" /></div>
      <div class="gallery-item"><img src="assets/screenshots/gallery/reminders-fa.png" alt="Reminders list in Persian" loading="lazy" /></div>
      <div class="gallery-item"><img src="assets/screenshots/gallery/charts-en.png" alt="Income and expense charts" loading="lazy" /></div>
      <div class="gallery-item"><img src="assets/screenshots/gallery/charts-fa.png" alt="Charts and visual reports in Persian" loading="lazy" /></div>
      <div class="gallery-item"><img src="assets/screenshots/gallery/reports-builder-fa.png" alt="Building a custom report by date range" loading="lazy" /></div>
      <div class="gallery-item"><img src="assets/screenshots/gallery/export-pdf-excel-fa.png" alt="Exporting a report to PDF" loading="lazy" /></div>
    </div>
  </section>
```

- [ ] **Step 3: Verify in browser**

Run: `python3 -m http.server 8080`, open `http://localhost:8080/`.
Expected: below the hero, a "Ghollak, in action" heading appears followed by a horizontally scrollable row of all 9 screenshots (drag or trackpad-scroll to confirm all 9 are reachable and snap into place). Click the nav's "Features" link and confirm the page scrolls to this section. Stop the server when done.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "Add horizontal screenshot gallery"
```

---

### Task 5: Spotlight rows and removal of the old features strip

**Files:**
- Modify: `index.html` (replace the `.features`/`.feature*` CSS block with a new `.spotlight` block, replace the `<div class="features">...</div>` markup with four `<section class="spotlight">` blocks, and update the `.features`/`.feature` rules inside the mobile media query)

**Interfaces:**
- Consumes: `--serif`, `--sans`, `--muted`, `--surface`, `--border` from Task 2; 8 files in `assets/screenshots/cropped/` from Task 1.

- [ ] **Step 1: Replace the old features-strip CSS with the spotlight CSS**

Replace:
```css
    /* ── FEATURES STRIP ── */
    .features {
      display: flex;
      justify-content: center;
      gap: 0;
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
      background: var(--surface);
    }

    .feature {
      flex: 1;
      max-width: 300px;
      padding: 2.5rem 2rem;
      text-align: center;
      border-right: 1px solid var(--border);
    }
    .feature:last-child { border-right: none; }

    .feature-icon {
      font-size: 1.5rem;
      margin-bottom: 0.75rem;
    }

    .feature h3 {
      font-family: var(--serif);
      font-size: 1.1rem;
      margin-bottom: 0.5rem;
      letter-spacing: -0.01em;
    }

    .feature p {
      font-size: 0.875rem;
      color: var(--muted);
      line-height: 1.6;
    }
```
with:
```css
    /* ── SPOTLIGHTS ── */
    .spotlight {
      padding: 5rem 2.5rem;
    }
    .spotlight:nth-of-type(even) {
      background: var(--surface);
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
    }

    .spotlight-inner {
      max-width: 1120px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 3.5rem;
      align-items: center;
    }

    .spotlight h3 {
      font-family: var(--serif);
      font-size: 1.9rem;
      letter-spacing: -0.02em;
      margin-bottom: 1rem;
    }

    .spotlight p {
      color: var(--muted);
      font-size: 1rem;
      line-height: 1.7;
      max-width: 440px;
    }

    .spotlight-duo {
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .spotlight-duo img {
      width: 45%;
      max-width: 230px;
      border-radius: 1.5rem;
      box-shadow: 0 20px 40px rgba(26,26,26,0.15);
      position: relative;
    }

    .spotlight-duo img:first-child {
      transform: rotate(-4deg) translateX(14%);
      z-index: 1;
    }

    .spotlight-duo img:last-child {
      transform: rotate(4deg) translateX(-14%);
      margin-left: -6%;
      z-index: 2;
    }

    @media (max-width: 900px) {
      .spotlight-inner { grid-template-columns: 1fr; text-align: center; }
      .spotlight p { margin-left: auto; margin-right: auto; }
      .spotlight-duo { margin-top: 1rem; }
    }
```

- [ ] **Step 2: Replace the features markup with four spotlight sections**

Replace:
```html
  <!-- FEATURES -->
  <div class="features">
    <div class="feature">
      <div class="feature-icon">📊</div>
      <h3>Clear overview</h3>
      <p>See exactly where your money goes, without the overwhelm.</p>
    </div>
    <div class="feature">
      <div class="feature-icon">🧘</div>
      <h3>Calm by design</h3>
      <p>No scary charts, no judgment. Just simple, honest numbers.</p>
    </div>
    <div class="feature">
      <div class="feature-icon">🔒</div>
      <h3>Your data, yours</h3>
      <p>Privacy-first. We never sell or share your financial information.</p>
    </div>
  </div>
```
with:
```html
  <!-- SPOTLIGHTS -->
  <section class="spotlight">
    <div class="spotlight-inner">
      <div class="spotlight-duo">
        <img src="assets/screenshots/cropped/manage-transactions-en.png" alt="Transaction list for a checking account" loading="lazy" />
        <img src="assets/screenshots/cropped/manage-transactions-fa.png" alt="Transaction list shown in Persian" loading="lazy" />
      </div>
      <div>
        <h3>Manage every transaction, effortlessly</h3>
        <p>Add, search, and review transactions in seconds. Transfer between accounts, filter by income or expense, and keep every balance up to date — in Persian or English, whichever you prefer.</p>
      </div>
    </div>
  </section>

  <section class="spotlight">
    <div class="spotlight-inner">
      <div>
        <h3>Never miss a check, bill, or reminder</h3>
        <p>Ghollak tracks your checks, recurring transactions, and one-off reminders, then notifies you before they're due. Set up a bill once and let it repeat automatically — reliably, every time.</p>
      </div>
      <div class="spotlight-duo">
        <img src="assets/screenshots/cropped/reminders-en.png" alt="Reminders for upcoming bills and checks" loading="lazy" />
        <img src="assets/screenshots/cropped/reminders-fa.png" alt="Reminders shown in Persian" loading="lazy" />
      </div>
    </div>
  </section>

  <section class="spotlight">
    <div class="spotlight-inner">
      <div class="spotlight-duo">
        <img src="assets/screenshots/cropped/charts-en.png" alt="Income and expense charts" loading="lazy" />
        <img src="assets/screenshots/cropped/charts-fa.png" alt="Charts shown in Persian" loading="lazy" />
      </div>
      <div>
        <h3>See the full picture, in any calendar</h3>
        <p>Visual charts break down income and expenses at a glance, and Pro reports let you build custom breakdowns over any date range — in either the Shamsi or Gregorian calendar.</p>
      </div>
    </div>
  </section>

  <section class="spotlight">
    <div class="spotlight-inner">
      <div>
        <h3>Take your data with you</h3>
        <p>Track unlimited accounts, sync automatically across your devices with iCloud, and back up or restore your data manually whenever you want. Export any report to PDF or Excel, and personalize the app with different themes.</p>
      </div>
      <div class="spotlight-duo">
        <img src="assets/screenshots/cropped/all-accounts-en.png" alt="All accounts and balances in one place" loading="lazy" />
        <img src="assets/screenshots/cropped/export-pdf-excel-fa.png" alt="Exporting a report to PDF in Persian" loading="lazy" />
      </div>
    </div>
  </section>
```

- [ ] **Step 3: Update the mobile media query**

Replace:
```css
      .features { flex-direction: column; align-items: center; }
      .feature { border-right: none; border-bottom: 1px solid var(--border); max-width: 100%; }
      .feature:last-child { border-bottom: none; }
```
with:
```css
      .spotlight { padding: 3.5rem 1.5rem; }
```

- [ ] **Step 4: Verify in browser at desktop and mobile widths**

Run: `python3 -m http.server 8080`, open `http://localhost:8080/`.
Expected: four alternating rows below the gallery, each showing two overlapping/tilted phone screenshots (no visible headline text baked into them) beside a heading and paragraph. Confirm the image side alternates left/right/left/right down the page at desktop width, and confirm all four stack cleanly (image above or below text, no overlap/clipping) at ~375px width. Stop the server when done.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "Replace feature strip with four screenshot spotlight rows"
```

---

### Task 6: Facts strip

**Files:**
- Modify: `index.html` (add a new `.facts`/`.fact*` CSS block after the spotlight CSS, add the `<div class="facts">` markup after the last spotlight section, add a mobile rule)

**Interfaces:**
- Consumes: `--serif`, `--muted`, `--accent-dark`, `--accent-light`, `--border` from Task 2.

- [ ] **Step 1: Add the facts strip CSS**

Insert immediately after the spotlight `@media (max-width: 900px) { ... }` block from Task 5:

```css
    /* ── FACTS STRIP ── */
    .facts {
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
      background: var(--accent-light);
    }

    .fact {
      flex: 1;
      min-width: 200px;
      max-width: 280px;
      padding: 2.5rem 1.5rem;
      text-align: center;
      border-right: 1px solid var(--border);
    }
    .fact:last-child { border-right: none; }

    .fact-headline {
      font-family: var(--serif);
      font-size: 1.3rem;
      color: var(--accent-dark);
      margin-bottom: 0.4rem;
    }

    .fact-caption {
      font-size: 0.85rem;
      color: var(--muted);
      line-height: 1.5;
    }
```

- [ ] **Step 2: Add the facts markup after the last spotlight section**

Insert immediately after the fourth `</section>` from Task 5 (the "Take your data with you" spotlight), before the `<!-- CONTACT -->` comment:

```html
  <!-- FACTS -->
  <div class="facts">
    <div class="fact">
      <p class="fact-headline">14+ Years</p>
      <p class="fact-caption">On the App Store, since 2012</p>
    </div>
    <div class="fact">
      <p class="fact-headline">Shamsi &amp; Gregorian</p>
      <p class="fact-caption">Pick the calendar you use</p>
    </div>
    <div class="fact">
      <p class="fact-headline">Persian &amp; English</p>
      <p class="fact-caption">Use the app in either language</p>
    </div>
    <div class="fact">
      <p class="fact-headline">Free &amp; Pro</p>
      <p class="fact-caption">Ghollak Mini or the full app</p>
    </div>
  </div>
```

- [ ] **Step 3: Add the mobile stacking rule**

In the `@media (max-width: 640px)` block, add (near the other section-specific mobile rules):
```css
      .facts { flex-direction: column; align-items: center; }
      .fact { border-right: none; border-bottom: 1px solid var(--border); max-width: 100%; }
      .fact:last-child { border-bottom: none; }
```

- [ ] **Step 4: Verify in browser**

Run: `python3 -m http.server 8080`, open `http://localhost:8080/`.
Expected: a four-column light-blue strip with "14+ Years", "Shamsi & Gregorian", "Persian & English", "Free & Pro" appears between the last spotlight and the contact section; at ~375px width it stacks into a single column with dividing lines between items. Stop the server when done.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "Add facts strip highlighting App Store tenure and platform support"
```

---

### Task 7: Restyle contact section and update footer

**Files:**
- Modify: `index.html` (two hardcoded green `rgba(45,106,79,...)` values inside `.form-field input:focus, .form-field textarea:focus` and `.submit-btn:hover`; the footer's copyright year)

**Interfaces:**
- Consumes: `--accent-rgb`, `--accent-dark` from Task 2.
- **Hard constraint:** this task must not touch the `id`/`name` attributes of `name`, `email`, `message`, the `#form-status` element, or anything inside the `<script>` block. Only the two CSS rules below and the footer's visible year text change.

- [ ] **Step 1: Update the focus-ring color**

Replace:
```css
    .form-field input:focus,
    .form-field textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(45,106,79,0.1);
    }
```
with:
```css
    .form-field input:focus,
    .form-field textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.1);
    }
```

- [ ] **Step 2: Update the submit button's hover color**

Replace:
```css
    .submit-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(45,106,79,0.25);
      background: #245c43;
    }
```
with:
```css
    .submit-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(var(--accent-rgb), 0.25);
      background: var(--accent-dark);
    }
```

- [ ] **Step 3: Update the footer copyright year**

Replace:
```html
    <p>© 2025 Ghollak – All Rights Reserved.</p>
```
with:
```html
    <p>© 2026 Ghollak – All Rights Reserved.</p>
```

- [ ] **Step 4: Verify the contact form still behaves identically**

Run: `python3 -m http.server 8080`, open `http://localhost:8080/`.
Confirm via `grep` that nothing else in the file changed:
```bash
grep -n 'id="name"\|id="email"\|id="message"\|id="form-status"\|formspree.io/f/xnjrnzjl\|function handleSubmit' index.html
```
Expected: all five matches still present, unchanged from before this task. In the browser, focus the email field and confirm the focus ring is now blue-tinted; hover the "Send message" button and confirm its shadow/hover background are blue-tinted. (Do not need to actually submit the form here — Task 8 covers that.) Stop the server when done.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "Restyle contact section to new palette and bump footer year"
```

---

### Task 8: Full-page integration QA

**Files:**
- Modify: `index.html` only if the verification steps below surface a concrete issue (e.g., a broken image path or a responsive overlap) — otherwise this task makes no further edits.

**Interfaces:**
- Consumes: the complete page produced by Tasks 1–7.

- [ ] **Step 1: Confirm every referenced asset resolves (no 404s)**

Run: `python3 -m http.server 8080` from the repo root, open `http://localhost:8080/` with the browser's dev tools Network tab open (or Console).
Expected: zero 404s for anything under `assets/`. If any image fails to load, cross-check its `src` in `index.html` against the actual filename under `assets/` (created in Task 1) and fix the typo.

- [ ] **Step 2: Responsive pass at three widths**

Using browser dev tools device mode, check the full page top to bottom at:
- ~1440px (desktop): hero two-column, gallery scrolls horizontally, spotlights alternate left/right, facts strip is four columns.
- ~768px (tablet): hero and spotlights should have collapsed to single-column per the `900px` media queries from Tasks 3 and 5.
- ~375px (mobile): nav links wrap without overlapping the logo, facts strip is a single column, gallery is still horizontally scrollable, contact form fields stack (pre-existing `640px` rule).

Expected: no horizontal page-level scrollbar at any width (only the intentional inner scroll on `.gallery-track`), no visibly overlapping or clipped text/images.

- [ ] **Step 3: Confirm the contact form still submits correctly**

With the local server running, open the page, fill in the Name/Email/Message fields, and click "Send message". Open the Network tab beforehand.
Expected: a `POST` request fires to `https://formspree.io/f/xnjrnzjl` with a JSON body `{"name": "...", "email": "...", "message": "..."}`; the on-page status message updates to the "✓ Thanks! We'll be in touch." text (or the network is genuinely offline/blocked in the sandbox, in which case confirm the request was attempted with the correct URL and payload shape via the Network tab rather than requiring a live 200 response).

- [ ] **Step 4: Confirm untouched files are actually untouched**

Run:
```bash
git status
git diff --stat -- privacy-policy.html tavallod-privacy-policy.html content/full-version-benefits.json
```
Expected: the diff-stat command produces no output (zero changes) for all three paths.

- [ ] **Step 5: Stop the local server and do a final full commit if Step 1 or 2 required fixes**

```bash
git add index.html
git commit -m "Fix responsive/asset issues found in final QA pass"
```
(Skip this step entirely if no fixes were needed — do not create an empty commit.)
