# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Maxime and their partner, parents of two children aged 2 and 5, living in Bern. They open the page on a phone **in the moment**: already out or at home with the children beside them, asking "what can we do now / this afternoon?". Attention is short and split; one hand may be busy.

Later (V2, not decided): other parents of young children (0–10) in Bern, then other Swiss cities.

## Product Purpose

One page that shows, in 30 seconds, what to do with young children in Bern over the next 14 days, filtered by when, price and type of activity. It merges several agendas (libraries, Creaviva, MuseumsQuartier, Menuhin Forum, Bühnen Bern, later Eventfrog) that are scattered and inconsistent about ages.

Success (V1): the family checks it every week and finds at least one activity they would not have found otherwise.

## Positioning

General aggregators mix adult concerts and toddler story times. This page looks at the same events with a parent's eyes: only children's and family activities, one view across sources, and the practical facts a parent needs (age, time, price, registration, "with an adult").

## Operating Context

- Data is refreshed every night by GitHub Actions and served as a static page on GitHub Pages (`docs/`).
- Content stays in its original language (mostly German, some French/English); the interface is French, prepared for German later (`docs/textes_fr.json`).
- Each event card always shows its source with a link.

## Capabilities and Constraints

- Static HTML/CSS/JavaScript, no framework, no build step; data from `docs/events.json`.
- Filters: when (today / weekend / 14 days), price (all / free / paid), type (atelier, conte, spectacle, musique, nature, sport, fête, visite).
- Weekly recurring offers are grouped in a collapsible "Chaque semaine" section.
- Ages are shown when the source states them; unknown values are labelled as unknown, never guessed silently.
- Images from sources are not used (Eventfrog forbids hotlinking; others not cleared).
- Out of scope for V1: accounts, favourites, notifications, map, native app.

## Brand Commitments

- Current name "Agenda Familles Berne" is open to change: a warmer name may be proposed, but must be approved by Maxime before it appears.
- Interface language: French, informal and friendly ("tu"), plain words.

## Evidence on Hand

Real events only, from the sources listed above. No testimonials, ratings, photos or parent reviews exist yet; none may be invented.

## Product Principles

1. Answer "what can we do now?" before anything else: the next relevant activities come first.
2. Parent facts over decoration: age, time, place, price and registration must be readable at a glance.
3. Honest data: show the source, say "unknown" when unknown.
4. One-handed phone use first; desktop is secondary.
5. Calm, not noisy: a busy parent with children around needs clarity, not stimulation.

## Accessibility & Inclusion

Readable outdoors on a phone (contrast, text size), large touch targets, works in light and dark mode. No specific standard required beyond good practice (WCAG AA as a target).
