# Agenda Familles Berne – mémo pour Claude Code

## Règle n°1
**En cas de doute, d'information manquante ou de décision qui revient à Maxime : toujours lui demander avant d'avancer.** Ne jamais faire d'hypothèse silencieuse.

## Le projet
Site web privé (V1, pour Maxime seul) qui affiche les activités pour enfants des 14 prochains jours à Berne.
Document de cadrage : « Agenda Familles Berne – Cadrage V1 » (6 nov. 2026). Plan détaillé : `~/.claude/plans/lexical-juggling-flute.md`.

## Façon de travailler
- Maxime débute en programmation : code simple, commenté en français.
- Une étape à la fois ; on s'arrête à la fin de chaque étape pour qu'il teste.
- **Commits automatiques** (accord de Maxime, 7 nov. 2026) : à la fin de chaque étape terminée, quand les tests passent
  et que le résultat est vérifié, faire le commit sans demander. Si Maxime demande ensuite un changement, le faire
  dans un nouveau commit. **Toujours demander avant tout `git push`, toute publication en ligne ou toute action
  visible par d'autres.**
- Respecter strictement le périmètre V1 et le hors-périmètre du cadrage.
- Interface en français ; tous les textes dans `docs/textes_fr.json` pour pouvoir traduire en allemand plus tard. Les contenus des événements restent dans leur langue d'origine.

## Décisions prises (7 nov. 2026)
- **Architecture** : pas de serveur ni de base. `recuperer.py` lit les sources → `docs/events.json` ; page statique `docs/index.html` + `app.js`.
- **Hébergement** : dépôt GitHub **public** + GitHub Pages. Aucun secret dans le code : les clés vont dans les secrets GitHub.
- **Exécution quotidienne** : GitHub Actions (`.github/workflows/quotidien.yml`, 4:00 UTC + bouton manuel).
- **En ligne** : dépôt https://github.com/maximelegeret/agenda-familles-berne. Deux hébergements identiques, mis à jour par le même commit nocturne :
  - GitHub Pages : https://maximelegeret.github.io/agenda-familles-berne/ (Pages depuis `main` /docs) ;
  - Vercel : https://agenda-familles-berne.vercel.app/ (configuré par `vercel.json` : pas de framework, pas de build, sortie `docs/`). Les adresses de branche `…-git-main-maxime-c428.vercel.app` sont protégées par la connexion Vercel.
  - Décision du 8 nov. 2026 : garder les deux. Ne pas supprimer `vercel.json` ni désactiver Pages sans l'accord de Maxime.
- **Commits du robot** : chaque nuit, « github-actions[bot] » commite `docs/events.json`. Toujours faire `git pull` avant de travailler et avant tout push.
- **Outil gh** : installé dans `/opt/homebrew/bin/gh` (pas dans le PATH du terminal de Maxime).
- **Python 3.12** (Homebrew), environnement virtuel dans `.venv/`.
- **Tri enfants/adultes** : mots-clés uniquement en V1. L'API Claude viendra plus tard, dans une étape dédiée.
- **Eventfrog** (actif depuis le 9 nov. 2026) : jeton « Public API-Key » créé par Maxime dans son compte Eventfrog, rangé dans `.env` (local, ignoré par git) et dans le secret GitHub `EVENTFROG_TOKEN`. `recuperer.py` lit `.env` au démarrage. Ne jamais afficher ni écrire le jeton ailleurs.
  - Réponse d'Eventfrog (9 nov. 2026) : usage validé. CGU § 17 : contenus repris tels quels, lien vers la page Eventfrog de chaque activité, mise à jour quotidienne, pas de transmission à des tiers, crédits `emblemCredits` si images (on n'en affiche pas). Limites : 30 requêtes/min, 2000/jour.
  - Leur demande : si un organisateur veut ajouter un événement, le renvoyer vers Eventfrog (saisie gratuite) ; **ne pas créer de formulaire de saisie**.
  - Choix de Maxime : rubrique 906 « Kinderveranstaltungen » entière, rayon 15 km ; organisateur CityQuest écarté (jeux de piste payants répétés chaque jour).
  - Les tests se lancent avec `python -m pytest` (un simple `pytest` ne trouve pas le module `agenda`).
- **Offres régulières** : déduites des séances hebdomadaires (`agenda/regulier.py`), sauf les spectacles (séries limitées, restent jour par jour) ; les offres sans dates sont écrites à la main dans `offres_regulieres.yaml` (ex. Pünktli du MüZe).
- **Images** : pas d'images des sources (Eventfrog interdit le lien direct, site public). À la place : illustrations dessinées en SVG (`docs/illustrations.js`), une par type d'activité + une scène bernoise.
- **Design** (7 nov. 2026) : univers « appli chaleureuse » choisi par Maxime avec le skill Impeccable (`.claude/skills/impeccable`, copie manuelle, télémétrie coupée). Produit décrit dans `PRODUCT.md`, système visuel dans `DESIGN.md` : **les lire avant toute modification de la page**. Police Figtree auto-hébergée (`docs/fonts/`, licence OFL).
- **Nom** : « Agenda Familles Berne » reste en attendant ; Maxime est ouvert à un nom plus chaleureux, à valider avant affichage.
- **Guidle** : aucune donnée Guidle sans leur accord.
- **Catégories** : liste fermée du cadrage + « visite » (visites guidées pour enfants), ajoutée avec l'accord de Maxime.
- **Champ `age_texte`** : l'âge tel qu'écrit par la source (ex. « in Begleitung »), en plus de age_min/age_max.
- **Tranche d'âge visée** : 0–10 ans ; un événement « dès 11 ans » ou plus est écarté.

## Sources de la vague 1 (comment les lire)
| Source | Méthode |
|---|---|
| Eventfrog | API `api.eventfrog.net/public/v1/events` (jeton requis), `rubId=906`, `lat`/`lng`/`r`, `from`/`to`, `page` ; lieux via `/public/v1/locations?id=…` (adresse + coordonnées) |
| Kornhausbibliotheken | Pages `www.kob.ch/agenda/` + fiches `/veranstaltung/<slug>/` (WordPress) |
| Creaviva | Pages `zpk.org/de/creaviva` ; Familienmorgen = offre régulière (dimanche 10:15) |
| MuseumsQuartier | Page `mqb.ch/en/agenda`, libellé « Children & Family » ; **10 s entre requêtes** (robots.txt) |
| Menuhin Forum | REST `menuhinforum.ch/wp-json/wp/v2/ajde_events` + iCal par événement ; garder « Familienkonzert » |
| Bühnen Bern | Pages `buehnenbern.ch/spielplan/programm/` ; « Junges Publikum », Kinder/Familie ; écarter « Schulvorstellung » |

## Sources ajoutées le 8 nov. 2026
| Source | Méthode |
|---|---|
| Berner Puppen Theater | `berner-puppentheater.ch/spielplan` ; seulement les liens `/kinderprogramm/` ; prix enfant–adulte sur la page |
| Schlachthaus Theater | `schlachthaus.ch/de/programm/shows/` ; âge ≤ 10 ans, écarter « Schulvorstellung » ; dates sans année (déduite) |
| Tierpark Bern | `tierpark-bern.ch/veranstaltungskalender/` ; pictogramme « Event für Kinder » ; fiche : Datum, Kosten, Zielgruppe |
| Naturhistorisches Museum | `nmbe.ch/de/kalender?audience[36]=36` (Familien und Kinder), pages `&page=N` ; datetime « Z » = heure locale |
| MüZe Muri-Gümligen | `mueze-muri-guemligen.ch/angebot/veranstaltungen/` ; écarter Beratung/Stilltreffen/Repair/Coiffeur ; Pünktli dans `offres_regulieres.yaml` |
| Dampfzentrale | page d'accueil (filtre en JavaScript) + fiche : `span.tag` = « Junges Publikum » |
| Botanischer Garten (BOGA) | `boga.unibe.ch/agenda/index_ger.html` (schema.org startDate) ; rubriques Kinderfreizeit et Thementage |

Pistes non faites (agenda en JavaScript ou absent) : Spielen in Bern / DOK, centres de quartier VBG (vbgbern.ch), Theater Matte, ALPS (alps.museum, en partie via MQB).

## Feuille de route V2 (validée le 8 nov. 2026) : mieux servir la famille, pas d'ouverture au public
Plan détaillé : `~/.claude/plans/lexical-juggling-flute.md`. Réglages personnels (favoris, âges, domicile) **sur le téléphone uniquement**, jamais dans le dépôt public.
- Lot 1 : Kunstmuseum (lecteur Creaviva, espace 7), favoris, ajout à l'agenda (.ics + flux `docs/agenda.ics`), partage, filtres âge des enfants et moment de la journée.
- Lot 2 : `lieux.yaml` (coordonnées, dedans/dehors), carte Leaflet/OSM, distance depuis le domicile.
- Lot 3 : résumé du week-end par mail le jeudi (GitHub Actions + mot de passe d'application Gmail en secret).
- Lot 4 : Eventfrog (fait le 9 nov. 2026), idées « jour de pluie », places de jeux (open data), IA Claude (cas flous + sites sans agenda lisible).

## V3 (validée le 9 nov. 2026) : au-delà de la liste, « dimanche 9 h, il pleut, on fait quoi ? »
Plan détaillé : `~/.claude/plans/lexical-juggling-flute.md`. Lot A (onglets + « Sortir »), Lot B (places de jeux, cafés, carte), Lot C (« Pratique » : échéances, infos utiles, anniversaires, saisons).
- **Lieux** : `lieux.yaml`, choisis par Maxime et vérifiés sur les sites officiels (champ `verifie_le`, à revérifier une fois par an). `agenda/lieux.py` calcule chaque nuit les plages d'ouverture des 14 prochains jours (saisons, jours fériés bernois, Zibelemärit) dans `docs/lieux.json` ; la page compare juste l'heure.
- **Page** : onglets en bas (Agenda / Sortir ; Pratique viendra au Lot C, pas d'onglet vide). Période et filtres dans un bandeau collant en haut. Code de l'onglet dans `docs/sortir.js`.
- **Météo** : Open-Meteo lu par la page (gratuit, sans clé, seulement les coordonnées du centre de Berne), crédit affiché (CC BY 4.0). S'il pleut, les lieux couverts passent en premier.
- **Pour vérifier** : `…/?maintenant=2026-11-15T09:00&meteo=pluie#sortir` simule une heure et une météo.
- Manques signalés à Maxime : aucun café avec coin jeux ni ferme fiable trouvés ; Bernisches Historisches Museum illisible ; horaires d'été des piscines non relevés (hors saison = fermé).

## Points ouverts
- Licence kob.ch : le cadrage dit CC BY-SA 4.0, les mentions légales du site exigent un accord écrit. OK en usage perso ; à clarifier avant toute ouverture au public.
- « Das Casino brummt » (Bühnen Bern) introuvable dans le programme actuel : ajout manuel s'il revient.

## Commandes utiles
```bash
source .venv/bin/activate      # activer l'environnement Python
python recuperer.py            # récupérer les événements
python -m pytest               # lancer les tests
```
