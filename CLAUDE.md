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
- **Eventfrog** : l'API exige un jeton (Bearer) demandé par Maxime à support@eventfrog.net. En attendant, on commence par les Kornhausbibliotheken (kob.ch).
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
