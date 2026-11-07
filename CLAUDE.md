# Agenda Familles Berne – mémo pour Claude Code

## Règle n°1
**En cas de doute, d'information manquante ou de décision qui revient à Maxime : toujours lui demander avant d'avancer.** Ne jamais faire d'hypothèse silencieuse.

## Le projet
Site web privé (V1, pour Maxime seul) qui affiche les activités pour enfants des 14 prochains jours à Berne.
Document de cadrage : « Agenda Familles Berne – Cadrage V1 » (6 nov. 2026). Plan détaillé : `~/.claude/plans/lexical-juggling-flute.md`.

## Façon de travailler
- Maxime débute en programmation : code simple, commenté en français.
- Une étape à la fois ; on s'arrête à la fin de chaque étape pour qu'il teste. Un commit Git par étape validée.
- Respecter strictement le périmètre V1 et le hors-périmètre du cadrage.
- Interface en français ; tous les textes dans `docs/textes_fr.json` pour pouvoir traduire en allemand plus tard. Les contenus des événements restent dans leur langue d'origine.

## Décisions prises (7 nov. 2026)
- **Architecture** : pas de serveur ni de base. `recuperer.py` lit les sources → `docs/events.json` ; page statique `docs/index.html` + `app.js`.
- **Hébergement** : dépôt GitHub **public** + GitHub Pages. Aucun secret dans le code : les clés vont dans les secrets GitHub.
- **Exécution quotidienne** : GitHub Actions.
- **Python 3.12** (Homebrew), environnement virtuel dans `.venv/`.
- **Tri enfants/adultes** : mots-clés uniquement en V1. L'API Claude viendra plus tard, dans une étape dédiée.
- **Eventfrog** : l'API exige un jeton (Bearer) demandé par Maxime à support@eventfrog.net. En attendant, on commence par les Kornhausbibliotheken (kob.ch).
- **Images** : pas d'images des sources en V1 (Eventfrog interdit le lien direct).
- **Guidle** : aucune donnée Guidle sans leur accord.

## Sources de la vague 1 (comment les lire)
| Source | Méthode |
|---|---|
| Eventfrog | API `api.eventfrog.net/public/v1/events` (jeton requis), filtres `rubId`, `lat`/`lng`/`r`, `from`/`to` |
| Kornhausbibliotheken | Pages `www.kob.ch/agenda/` + fiches `/veranstaltung/<slug>/` (WordPress) |
| Creaviva | Pages `zpk.org/de/creaviva` ; Familienmorgen = offre régulière (dimanche 10:15) |
| MuseumsQuartier | Page `mqb.ch/en/agenda`, libellé « Children & Family » ; **10 s entre requêtes** (robots.txt) |
| Menuhin Forum | REST `menuhinforum.ch/wp-json/wp/v2/ajde_events` + iCal par événement ; garder « Familienkonzert » |
| Bühnen Bern | Pages `buehnenbern.ch/spielplan/programm/` ; « Junges Publikum », Kinder/Familie ; écarter « Schulvorstellung » |

## Points ouverts
- Licence kob.ch : le cadrage dit CC BY-SA 4.0, les mentions légales du site exigent un accord écrit. OK en usage perso ; à clarifier avant toute ouverture au public.
- « Das Casino brummt » (Bühnen Bern) introuvable dans le programme actuel : ajout manuel s'il revient.

## Commandes utiles
```bash
source .venv/bin/activate      # activer l'environnement Python
python recuperer.py            # récupérer les événements
pytest                         # lancer les tests
```
