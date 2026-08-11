# Ghollak Home Page Redesign — Design Spec

Date: 2026-08-12

## Purpose

The current `index.html` home page is a generic, content-free marketing template — it never mentions the app is called Ghollak's actual features, has no App Store links, no screenshots, and uses a color identity unrelated to the app itself. This redesign rebuilds the home view to actually represent the app: real screenshots, real feature descriptions, App Store download links for both editions, and copy that uses the app's genuine differentiators (14 years on the App Store, dual calendar support, bilingual UI, checks/reminders/recurring transactions, etc).

Scope is the home view (`index.html`) only. The two privacy policy pages (`privacy-policy.html`, `tavallod-privacy-policy.html`) and `content/full-version-benefits.json` (in-app remote content, unrelated to the website) are explicitly out of scope and must not be modified.

## Content facts to draw on

- First Persian personal finance app on the App Store, ~14 years (since ~2012).
- Supports both Shamsi (Jalali) and Gregorian calendars.
- Fully bilingual: Persian and English.
- Easy to use.
- Features: managing checks, iCloud sync, reminders, recurring transactions, manual backup & restore, reliability, charts, pro reports, PDF/Excel export, themes/customization.
- Two editions: **Ghollak Mini** (free) and **Ghollak** (paid/full).
- App Store links:
  - Mini (free): `https://apps.apple.com/us/app/ghollak-mini-english-%D9%81%D8%A7%D8%B1%D8%B3%DB%8C/id611339401`
  - Ghollak (paid): `https://apps.apple.com/us/app/ghollak-persian-english/id544694377`

## Visual direction

- **Color:** Replace the current sage-green accent (`--accent: #2d6a4f`) with a blue accent derived from the Ghollak app icon (a deep, slightly muted blue, not a raw system blue). Keep the existing warm off-white background (`--bg`) and dark ink text (`--ink`) — only the accent (buttons, links, hover states, focus rings, facts strip) changes.
- **Typography:** Move away from the current DM Serif Display / DM Sans pairing to a different editorial display font (headlines) + clean sans (body/UI), chosen for personality on a marketing/landing page. Not Vazirmatn — the app's font choice doesn't need to carry over to the site. Final font pairing selected during implementation (Google Fonts, loaded the same way the current fonts are).
- **Nav bar:** structurally unchanged (wordmark left, links right) so it still visually matches the untouched privacy-policy pages' nav. Wordmark stays text-only (no icon swap). Only the accent color and font update. Add one new anchor link: "Features".
- **Hero becomes two-column** on desktop (copy + CTAs left, one flagship phone screenshot right), stacking to a single centered column on mobile — replacing the current single-column centered hero.

## Assets

Source files (already on disk, not yet in repo) get copied into `assets/` and optimized for web (resized + compressed; sources currently run 600KB–2MB each):

- `assets/screenshots/` — the 9 app screenshots (mixed English/Persian, used as-is including Persian-language ones)
- `assets/icons/ghollak-mini.png` — Ghollak Mini app icon
- `assets/icons/ghollak.png` — full Ghollak app icon (from `icon-white.jpg`)

## Page structure

### 1. Nav
Unchanged structure/links (`Home`, `Privacy Policy`, `Tavallod Privacy Policy`) plus a new `Features` anchor pointing at the gallery/spotlight section. Colors/fonts updated to match new palette.

### 2. Hero
- Eyebrow: "14 years on the App Store"
- Headline: keeps the "Personal finance, without the panic." spirit (exact copy finalized in implementation)
- Subhead: works in the origin story + calendar/language facts (first Persian finance app on the App Store, Shamsi & Gregorian, Persian & English)
- Two download buttons, styled as App Store badges:
  - Left: Ghollak Mini icon + "Free" label + badge linking to the Mini App Store URL
  - Right: Ghollak icon + "Pro" label + badge linking to the full Ghollak App Store URL
- Flagship phone screenshot (the "All Your Money, One Place" accounts-overview screenshot) shown beside the copy on desktop, below it on mobile.

### 3. Screenshot gallery
Horizontal scroll-snap strip containing all 9 screenshots, each in a rounded phone-corner frame with a short caption underneath. Scrolls natively (touch/trackpad); no dependency on external carousel libraries.

### 4. Spotlight rows
Four alternating full-width rows (image-left/text-right, then text-left/image-right, repeating). Each row pairs the English and Persian screenshot of the *same screen*, shown overlapped/tilted as a duo, so the bilingual + dual-calendar support is demonstrated visually rather than just claimed:

1. **Manage every transaction** — `Manage Transactions` (EN) + `مدیریت تراکنش‌های مالی` (FA). Copy covers: accounts, transfers, search, ease of use.
2. **Never miss a check or bill** — `Never Miss A Payment` (EN) + `همه مدل یادآوری` (FA). Copy covers: checks, reminders, recurring transactions, reliability.
3. **See the full picture** — `Visualized Charts` (EN) + `گزارش‌های نموداری` (FA). Copy covers: charts, pro reports, custom date ranges.
4. **Take your data with you** — `All Your Money, One Place` (EN) + `خروجی پی‌دی‌اف و اکسل` (FA). Copy covers: unlimited accounts, iCloud sync, manual backup/restore, PDF/Excel export, themes/customization.

### 5. Facts strip
Four short stat chips, styled consistently with each other:
- "14+ years on the App Store"
- "Shamsi & Gregorian"
- "Persian & English"
- "Free & Pro editions"

### 6. Contact
Visually restyled to the new palette/fonts only. The following must remain byte-identical in behavior:
- Field element IDs: `name`, `email`, `message`
- Field `name` attributes: `name`, `email`, `message`
- The `handleSubmit()` function and its `fetch('https://formspree.io/f/xnjrnzjl', ...)` call, including the JSON payload shape (`{ name, email, message }`) and header set
- The `#form-status` success/error message element and IDs it references

No structural or behavioral changes to the form — only CSS.

### 7. Footer
Same structure (wordmark, copyright line, privacy links). Copyright year corrected from 2025 to 2026. Colors/fonts updated.

## Explicitly out of scope

- `privacy-policy.html` and `tavallod-privacy-policy.html` — not modified.
- `content/full-version-benefits.json` — not modified (in-app remote content, not website content).
- Persian-language site support — site stays English-only; Persian text appears only inside the screenshot images themselves.
- A dedicated "Free vs Pro" comparison section — declined; only the two hero download buttons distinguish editions.

## Testing / verification

Static site, no build step or test suite. Verification is manual:
- Open the page in a browser at desktop and mobile widths; confirm hero, gallery, spotlights, facts strip, contact, and footer all render correctly and responsively.
- Confirm both App Store badge links point to the correct URLs.
- Submit the contact form (or inspect the network request) to confirm the Formspree POST still fires with the same payload shape as before the redesign.
- Confirm privacy-policy pages are byte-identical to their pre-redesign state (`git diff` shows no changes to those files).
