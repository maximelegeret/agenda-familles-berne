"""
Script principal : récupère les événements de toutes les sources actives
et les écrit dans docs/events.json, que la page web affiche.

Lancement :  python recuperer.py
"""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

# Dossier du projet (là où se trouve ce fichier)
DOSSIER = Path(__file__).parent
FICHIER_SOURCES = DOSSIER / "sources.yaml"
FICHIER_SORTIE = DOSSIER / "docs" / "events.json"

# Toutes les dates du projet sont à l'heure de Berne
FUSEAU = ZoneInfo("Europe/Zurich")


def charger_sources():
    """Lit sources.yaml et renvoie la liste des sources actives."""
    with open(FICHIER_SOURCES, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return [s for s in config["sources"] if s.get("actif")]


def main():
    sources = charger_sources()
    evenements = []

    # Les lecteurs seront branchés ici à partir de l'étape 2.
    for source in sources:
        print(f"- {source['nom']} : lecteur pas encore écrit")

    # On écrit le résultat, avec la date de mise à jour
    resultat = {
        "mis_a_jour": datetime.now(FUSEAU).isoformat(timespec="minutes"),
        "evenements": evenements,
    }
    FICHIER_SORTIE.parent.mkdir(exist_ok=True)
    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        json.dump(resultat, f, ensure_ascii=False, indent=2)

    n = len(evenements)
    print(f"{n} événement{'s' if n > 1 else ''} écrit{'s' if n > 1 else ''} dans {FICHIER_SORTIE.relative_to(DOSSIER)}")


if __name__ == "__main__":
    main()
