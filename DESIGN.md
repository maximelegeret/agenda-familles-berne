---
name: Agenda Familles Berne
description: Agenda des activités pour enfants (0–10 ans) à Berne, pensé pour le téléphone et le moment présent.
colors:
  apricot-ground: "#fcebdc"
  card: "#ffffff"
  ink: "#2b2320"
  ink-soft: "#75655b"
  hairline: "#f1e2d5"
  neutral-fill: "#f7ede4"
  tomato-action: "#cf3a1b"
  tomato-soft: "#fde1d8"
  amber-accent: "#f6a33a"
  free-fill: "#dff0dc"
  free-ink: "#2c6630"
  stamp-fill: "#fff0d1"
  stamp-ink: "#855400"
  night-ground: "#1d1714"
  night-card: "#2a221d"
  night-ink: "#f6ece4"
  night-tomato: "#ff6b47"
typography:
  display:
    fontFamily: "Figtree, ui-rounded, system-ui, sans-serif"
    fontSize: "clamp(28px, 7.4vw, 40px)"
    fontWeight: 800
    lineHeight: 1.08
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Figtree, ui-rounded, system-ui, sans-serif"
    fontSize: "23px"
    fontWeight: 750
    lineHeight: 1.18
    letterSpacing: "-0.015em"
  section:
    fontFamily: "Figtree, ui-rounded, system-ui, sans-serif"
    fontSize: "20px"
    fontWeight: 750
    lineHeight: 1.2
  item:
    fontFamily: "Figtree, ui-rounded, system-ui, sans-serif"
    fontSize: "16.5px"
    fontWeight: 700
    lineHeight: 1.3
  body:
    fontFamily: "Figtree, ui-rounded, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.45
  sheet-title:
    fontFamily: "Figtree, ui-rounded, system-ui, sans-serif"
    fontSize: "21px"
    fontWeight: 750
    lineHeight: 1.2
  day:
    fontFamily: "Figtree, ui-rounded, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 750
    lineHeight: 1.2
  secondary:
    fontFamily: "Figtree, ui-rounded, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.4
  meta:
    fontFamily: "Figtree, ui-rounded, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.4
  label:
    fontFamily: "Figtree, ui-rounded, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 650
    lineHeight: 1.3
  badge:
    fontFamily: "Figtree, ui-rounded, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 800
    lineHeight: 1
rounded:
  chip: "999px"
  tile: "16px"
  thumb: "18px"
  card: "22px"
  card-large: "28px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "16px"
  lg: "22px"
  xl: "28px"
components:
  button-primary:
    backgroundColor: "{colors.tomato-action}"
    textColor: "{colors.card}"
    rounded: "{rounded.chip}"
    padding: "0 24px"
    height: "50px"
  segment-active:
    backgroundColor: "{colors.tomato-action}"
    textColor: "{colors.card}"
    rounded: "{rounded.chip}"
    height: "46px"
  segment-idle:
    textColor: "{colors.ink-soft}"
    rounded: "{rounded.chip}"
    height: "46px"
  chip:
    backgroundColor: "{colors.neutral-fill}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.chip}"
    padding: "4px 10px"
  chip-free:
    backgroundColor: "{colors.free-fill}"
    textColor: "{colors.free-ink}"
    rounded: "{rounded.chip}"
    padding: "4px 10px"
  card:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.card}"
  card-featured:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.card-large}"
---

# Design System: Agenda Familles Berne

## Overview

**Creative North Star: "La poche du parent"**

A warm consumer app a parent opens with one hand, children beside them. It answers "what can we do now?" before anything else: the next activity is a big illustrated card with how soon it starts; the rest is a calm list grouped by day; period and filters live in a bar at the bottom, under the thumb.

Warmth comes from the apricot ground, rounded type and authored illustrations, never from childish devices. Calm comes from restraint: white cards, one bright colour, and that colour only where something can be pressed.

**Key Characteristics:**
- Apricot ground, white cards with soft large radii and soft offset shadows.
- One saturated action colour (tomato), reserved for things you can press.
- Each activity type owns a tint and a two-tone illustration; colour codes the type, not decoration.
- Rounded humanist sans (Figtree, self-hosted), tabular figures for every time.
- Light by day, warm dark at night (follows the phone's setting).

## Colors

### Primary
- **Tomato action** `#cf3a1b` (night `#ff6b47`): active segment, primary buttons, source links, filter count badge. Nothing else.

### Neutral
- **Apricot ground** `#fcebdc` (night `#1d1714`): the page field.
- **Card** `#ffffff` (night `#2a221d`): every surface that holds content; also the "highlight" fill inside illustrations.
- **Ink** `#2b2320`, **soft ink** `#75655b`: text; soft ink for places, dates, secondary lines.
- **Neutral fill** `#f7ede4`, **hairline** `#f1e2d5`: chips, idle buttons, dividers.

### Activity type tints
Each type sets `--cat-fond` (tile background), `--i-ink` (illustration ink and type label) and `--i-soft` (illustration mid-tone), light and dark: conte lilac, atelier apricot, spectacle rose, musique sky, visite sage, nature leaf, sport sun, fête coral, autre sand. Values live in `docs/style.css` under `[data-cat]`.

### Named Rules
**The Pressable Colour Rule.** Tomato appears only on elements that respond to a tap. Information ("Dans 40 min") uses ink, never tomato.

**The Type Owns Its Colour Rule.** Type tints appear only on the illustration tile, the illustration and the type label; they never become page sections or borders.

## Typography

Figtree (SIL OFL), self-hosted variable 400–800 in `docs/fonts/`.

### Hierarchy
- **Display** 28–40px / 800 / -0.025em: the page question only.
- **Title** 23px / 750: the featured activity.
- **Section** 20px / 750 and **day** 18px / 750 (sticky).
- **Item** 16.5px / 700: activity names in lists.
- **Body** 16px / 400; **secondary** 15px for descriptions and buttons; **meta** 14px for places, times, links and actions; **label** 13px / 650 for chips and type labels; **badge** 12px / 800 for the filter count.
- **Sheet title** 21px / 750.

### Named Rules
**The Tabular Time Rule.** Every time and duration uses tabular figures so columns of hours align.

## Layout

Single column, max 680px, 16px side gutters. Mobile-first; from 720px the header scene becomes a centred card and the featured card splits into illustration | text. The bottom bar is fixed, floating 12px above the safe area; the page reserves 104px of bottom padding for it. Upcoming activities scroll horizontally in a snap row inside the column; the page itself never scrolls sideways.

## Elevation & Depth

Two soft offset shadows, warm-tinted: `--ombre` for cards and chips, `--ombre-forte` for the featured card, bottom bar and sheet. No hard offset shadows, no glow.

## Shapes

Pills (999px) for chips, segments and buttons; 16–18px for illustration tiles; 22px for cards and list groups; 28px for the featured card, the header scene card and the filter sheet's top corners.

## Components

### Buttons
Primary: tomato pill, 50px tall, 750 weight, soft tomato shadow; press scales to 0.96. Text button: soft ink, underlined.

### Chips
Neutral fill by default; free = green fill; registration = amber "stamp" fill; unknown values in soft ink ("Âge ?", "Prix ?").

### Cards / Containers
List items are rows inside one white group card per day, separated by hairlines; never a card per row. A row is a button: illustration tile, time + type, name, place, chips; tapping unfolds description and source link.

### Navigation
Bottom bar: three-way period segment (Aujourd'hui / Week-end / 14 jours) + round filter button with a count badge. Filters open as a bottom sheet (`<dialog>`) with price segments, type choices as illustrated tiles, and a "Voir N activités" primary button.

### Featured card ("Bientôt")
The signature component: tinted illustration panel with the relative-time badge ("En cours", "Dans 40 min", "Demain 16:00"), then time, type, name, short text, place, chips and source link. Badges refresh every minute.

### Actions (favori, agenda, partage)
A row of neutral-fill pills (40px tall, meta size, line icon + word) at the end of the featured card and of every unfolded row: « Favori », « Agenda » (downloads an .ics), a tomato text link « Google Agenda », « Partager » (native share, else copy + toast). An active favourite turns stamp-amber with a filled amber star; the same star then marks the row title. Regular offers get favourite and share only.

### Filter sheet controls
« Seulement mes favoris (N) » is a full-width switch (tomato track when on). Children's ages are 44px rounded tiles 0–10 (« < 1 » for babies), tomato when selected; they are a durable setting that « Effacer » and « Tout afficher » keep. Time of day reuses the price segments (Matin / Après-midi / Soir, multi-select).

### Toast
Ink pill above the bottom bar, white text, 2.6 s, for confirmations (« Ajouté à tes favoris », « Lien copié »).

### Illustrations
Authored inline SVG (`docs/illustrations.js`), 64×64, two-tone per type plus the amber accent and card white; the Bern header scene (Münster, Zytglogge, arcades, Aare) follows the theme through `--s-*` variables.

## Do's and Don'ts

### Do:
- Do keep tomato for pressable elements only.
- Do give every new activity type a tint pair and an illustration in the same 64×64 two-tone style.
- Do write labels in plain, friendly French ("Qu'est-ce qu'on fait avec les enfants ?").
- Do show "?" for unknown age or price rather than hiding the chip.

### Don't:
- Don't add source photos (rights) or emoji/glyph icons; draw icons as SVG.
- Don't add a kicker or eyebrow label above headings.
- Don't use bounce or elastic easing, pulsing dots, gradient text or glass effects.
- Don't make it childish: no cartoon fonts, mascots or saturated rainbow fills.
