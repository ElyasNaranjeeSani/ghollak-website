# Ghollak Website — Trilingual Redesign — Design Spec

Date: 2026-10-09

## Purpose

Rebuild ghollak.app around what the app is today (personal + business finance:
accounts, people/debts, store & invoices, checks, reports & PDF/Excel export,
three languages, three calendars) and serve it in Persian (default), English
and Arabic. The page must upsell without overwhelming: short beats, real
screenshots, one clear download CTA.

## Constraints

- Contact form keeps its exact Formspree logic (`https://formspree.io/f/xnjrnzjl`,
  JSON body `{name, email, message}`, email required). Only UI and status
  strings change (localized).
- `privacy-policy.html`, `tavallod-privacy-policy.html`, `yadavar-privacy-policy.html`
  keep their URLs and content. Tavallod/Yadavar leave the nav and appear only as
  a small muted footer line. Ghollak's policy link stays `/privacy-policy.html`.
- `content/full-version-benefits.json` is in-app remote content: read it, never modify it.
- Static GitHub Pages; no runtime framework. Never `git push` without being asked.
- App Store link (single edition): `https://apps.apple.com/us/app/ghollak-persian-english/id544694377`.

## Visual direction — "warm ledger"

- Brand color: **gold everywhere** (cream paper background, deep brown-black ink,
  app gold accent), matching the FA/AR marketing and reel cover. All screenshots
  are gold-theme.
- Hero backdrop: soft gold radial glow + faint geometric line pattern (CSS/SVG).
- English type: editorial serif display + clean sans body (Google Fonts).
  FA/AR fonts chosen in phase 2.
- iPhone frames drawn in CSS (bezel, rounded screen, dynamic island) around plain
  WebP screenshots, so images stay one-per-screen-per-language and can tilt/fan.

## Page structure

1. **Nav** — icon + wordmark; Features, Pricing, Contact; language switcher;
   gold Download button.
2. **Hero** — "Simple as a piggy bank. Complete as a ledger." + one-line sub +
   App Store badge + trust row: ★4.5 · N years on the App Store (auto-computed
   from 2012) · iPhone, iPad & Mac · No sign-up, data stays on your device.
   Three fanned phones: Store, Home, Charts.
3. **Feature chapters** — five chapters: Accounts & transactions; People
   (debts/receivables); Store (inventory, barcode, invoices); Checks & reminders;
   Reports & PDF/Excel export. Each: title, 2-line copy, 3 ticks, and 1–3
   screenshots. Desktop: one sticky phone whose screen cross-fades as the
   chapters (and screens within a chapter) scroll by. Mobile: stacked, one
   phone per chapter showing its first screen. A language with fewer shots
   simply lists fewer screens per chapter.
4. **The little things** — compact tile grid: widgets, Face ID/Touch ID,
   themes + dark mode, live dollar & gold prices, folders, fast search,
   iCloud sync + manual backup, percentage/commission on transactions.
5. **Languages & calendars** — today's date rendered live via
   `Intl.DateTimeFormat` in Persian (Jalali), Gregorian and Hijri, beside the
   three language names.
6. **Plans: Free / Pro / Business** — three cards mirroring the app's own
   `PaywallFeatureCatalog` (Ghollak repo), not the older two-tier
   `full-version-benefits.json`. Free: 2 accounts & checks, 3 reminders,
   3 recurring, 2 people, 3 exports/month, store demo. Pro: unlimited
   accounts/checks/reminders/recurring/people, iCloud sync, backup & restore,
   multi-currency, tags, 10 exports/month. Business: everything in Pro + store
   management with barcode, branded PDF reports, custom totals & balance row,
   account folders, business-mode charts, chart export, list percentage,
   Ghollak Buddy, unlimited exports & history. Messaging: one-time purchase,
   no subscription; no prices shown (they vary by region). fa/ar wording
   reuses the app's own `Localizable.xcstrings` translations.
7. **Contact** — restyled form, same logic, localized labels/status messages.
8. **Footer** — Ghollak privacy policy; small muted "Other apps' policies:
   Tavallod · Yadavar"; © line.

All motion respects `prefers-reduced-motion`. Layout works at 360px wide with
no horizontal scroll.

## Languages & build

- URLs: `/` = Persian (`lang="fa" dir="rtl"`), `/en/` = English, `/ar/` = Arabic
  (`dir="rtl"`). `hreflang` alternates on every page.
- Source: `site/template.html` + `site/strings/{en,fa,ar}.json` +
  `site/screens.json` (per-language screenshot list per chapter/hero slot).
  `scripts/build-site.py` (stdlib only) renders the three pages. Generated HTML
  is committed (GitHub Pages serves it as-is).
- Language picker: first visit to `/` with no stored choice shows a light
  overlay (فارسی / English / العربية); choice saved in `localStorage`
  (try/catch, falls back to showing nothing extra) and redirects. `/en/` and
  `/ar/` never show the overlay. The nav switcher always works.

## Screenshots

Captured from the Ghollak repo (iOS simulator, 6.3" iPhone, 1206×2622, 9:41
status bar, gold theme, light mode, Business tier, consistent rich demo data).

- **English (new, ~10)**: home, account, store, invoice, people ledger, checks,
  reminders, charts, PDF export settings, rich PDF export.
- **Persian (~13)**: existing 7 (home, account, store, charts, people, checks,
  PDF) plus invoice detail, reminders, PDF export settings (logo, title, color,
  columns), rich multi-page PDF (store/invoice with logo), business-mode charts,
  savings goal / folders, export history.
- **Arabic**: existing 10; phase 2 may add PDF settings for parity.

`scripts/prepare-screenshots.py` converts sources to ~600px-wide WebP under
`assets/screens/{en,fa,ar}/`. Old `assets/screenshots/` is removed once unused.

## Phases

1. Build pipeline, assets, and `/en/` only. Root `/` stays untouched until the
   English page is approved.
2. Persian `/` and Arabic `/ar/` (RTL, fonts), language overlay goes live.

## Verification

Local `python3 -m http.server`, checked in Chrome at desktop and 375px widths:
layout, sticky chapters, reduced motion, no console errors, all policy links
resolve, contact form posts the same payload (verified via network inspection,
not by spamming the real endpoint more than once).
