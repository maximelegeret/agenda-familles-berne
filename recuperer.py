"""
Script principal : récupère les événements de toutes les sources actives
et les écrit dans docs/events.json, que la page web affiche.

Lancement :  python recuperer.py
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from agenda.modele import Evenement

# Dossier du projet (là où se trouve ce fichier)
DOSSIER = Path(__file__).parent
FICHIER_SOURCES = DOSSIER / "sources.yaml"
FICHIER_AJOUTS = DOSSIER / "ajouts_manuels.yaml"
FICHIER_SORTIE = DOSSIER / "docs" / "events.json"

# Toutes les dates du projet sont à l'heure de Berne
FUSEAU = ZoneInfo("Europe/Zurich")
# On garde les événements des 14 prochains jours
NB_JOURS = 14


def charger_sources():
    """Lit sources.yaml et renvoie la liste des sources actives."""
    with open(FICHIER_SOURCES, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return [s for s in config["sources"] if s.get("actif")]


def charger_ajouts_manuels():
    """Lit ajouts_manuels.yaml et renvoie une liste d'Evenement."""
    with open(FICHIER_AJOUTS, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    return [Evenement(**donnees) for donnees in (config.get("evenements") or [])]


def dans_la_fenetre(evenement, maintenant):
    """Vrai si l'événement n'est pas terminé et commence dans les 14 prochains jours."""
    debut = evenement.date_debut().replace(tzinfo=FUSEAU)
    fin = datetime.fromisoformat(evenement.fin).replace(tzinfo=FUSEAU) if evenement.fin else debut
    limite = maintenant.replace(hour=0, minute=0) + timedelta(days=NB_JOURS + 1)
    # Sans heure de fin, on garde l'événement toute la journée de son début
    if not evenement.fin:
        fin = fin.replace(hour=23, minute=59)
    return fin >= maintenant and debut < limite


def main():
    maintenant = datetime.now(FUSEAU)
    sources = charger_sources()
    evenements = []

    # Les lecteurs seront branchés ici à partir de l'étape 2.
    for source in sources:
        print(f"- {source['nom']} : lecteur pas encore écrit")

    ajouts = charger_ajouts_manuels()
    print(f"- Ajouts manuels : {len(ajouts)} lu(s)")
    evenements.extend(ajouts)

    # On ne garde que les 14 prochains jours, triés par date
    evenements = [e for e in evenements if dans_la_fenetre(e, maintenant)]
    evenements.sort(key=lambda e: e.debut)

    # On écrit le résultat, avec la date de mise à jour
    resultat = {
        "mis_a_jour": maintenant.isoformat(timespec="minutes"),
        "evenements": [e.en_dict() for e in evenements],
    }
    FICHIER_SORTIE.parent.mkdir(exist_ok=True)
    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        json.dump(resultat, f, ensure_ascii=False, indent=2)

    n = len(evenements)
    print(f"{n} événement{'s' if n > 1 else ''} écrit{'s' if n > 1 else ''} dans {FICHIER_SORTIE.relative_to(DOSSIER)}")


if __name__ == "__main__":
    main()
