# Agenda Familles Berne

Une page qui montre, en 30 secondes, les activités pour enfants (0–10 ans) des 14 prochains jours à Berne.
Version 1, à usage personnel.

## Comment ça marche

1. `recuperer.py` lit chaque source (sites des bibliothèques, du Creaviva, du MuseumsQuartier,
   du Menuhin Forum, de Bühnen Bern), ne garde que les activités pour enfants, fusionne les doublons
   et écrit le résultat dans `docs/events.json`.
2. La page `docs/index.html` affiche ce fichier, avec des filtres (quand, prix, type).

Il n'y a ni serveur ni base de données : seulement des fichiers.

## Les commandes utiles

À lancer dans le dossier du projet :

```bash
# Récupérer les événements (environ 2 à 3 minutes)
.venv/bin/python recuperer.py

# Voir la page sur l'ordinateur : ouvrir ensuite http://localhost:8000
.venv/bin/python -m http.server 8000 --directory docs

# Lancer les tests automatiques
.venv/bin/python -m pytest
```

Le terminal affiche, pour chaque source, le nombre d'événements lus et gardés,
ainsi que la liste de ce qui a été écarté et pourquoi (ex. « dès 12 ans »).

## Ajouter un événement à la main

Pour un événement trouvé ailleurs (Fäger, affiche, message d'école…) :

1. Ouvrir `ajouts_manuels.yaml`.
2. Copier le modèle (exemple minimal : titre, date, lieu) sous `evenements:`.
3. Lancer `.venv/bin/python recuperer.py` : si une fiche a un problème (champ manquant,
   faute de frappe, date mal écrite), le terminal le dit et la page affiche un avertissement.

## Ajouter une source

Donner l'adresse de l'agenda à Claude Code : il écrit le lecteur dans `agenda/lecteurs/`
et ajoute une ligne dans `sources.yaml`. Une source peut être mise en pause avec `actif: false`.

## Organisation des fichiers

| Fichier | Rôle |
|---|---|
| `sources.yaml` | Liste des sources (active ou en pause, réservée aux enfants ou non) |
| `ajouts_manuels.yaml` | Événements ajoutés à la main |
| `recuperer.py` | Script principal |
| `agenda/modele.py` | Format commun d'un événement |
| `agenda/lecteurs/` | Un lecteur par source |
| `agenda/filtre_enfants.py` | Tri enfants / adultes, âge, catégorie |
| `agenda/doublons.py` | Fusion des doublons |
| `agenda/regulier.py` | Offres qui reviennent chaque semaine |
| `docs/` | La page web (HTML, JavaScript, CSS, textes en français) |
| `tests/` | Tests automatiques, avec des pages enregistrées des sources |
| `CLAUDE.md` | Décisions du projet, pour Claude Code |

## Droits

Usage personnel uniquement. Chaque fiche affiche sa source avec un lien.
Avant toute ouverture au public, il faut vérifier les conditions de chaque source
(voir `CLAUDE.md`, en particulier les Kornhausbibliotheken).
