"""
Script principal : récupère les événements de toutes les sources actives
et les écrit dans docs/events.json, que la page web affiche.

Lancement :  python recuperer.py
"""

import importlib
import json
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from agenda.filtre_enfants import completer, trier
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


def garder_enfants(evenements, source_enfants, maintenant):
    """
    Complète âge et catégorie, puis ne garde que les événements pour enfants.
    Affiche dans le terminal ce qui est écarté (dans les 14 jours), pour pouvoir vérifier le tri.
    """
    gardes, ecartes = [], {}
    for e in evenements:
        completer(e)
        garder, raison = trier(e, source_enfants)
        if garder:
            gardes.append(e)
        elif dans_la_fenetre(e, maintenant):
            ecartes[e.titre] = raison  # une ligne par titre suffit
    for titre, raison in ecartes.items():
        print(f"    écarté : {titre[:60]}  ({raison})")
    return gardes


def main():
    maintenant = datetime.now(FUSEAU)
    sources = charger_sources()
    evenements = []
    statuts = []  # état de chaque source, affiché sur la page en cas de problème

    for source in sources:
        # Chaque source est lue à part : si l'une plante, les autres continuent
        try:
            lecteur = importlib.import_module(f"agenda.lecteurs.{source['lecteur']}")
            lus = lecteur.lire(source)
            gardes = garder_enfants(lus, source.get("pour_enfants", False), maintenant)
            evenements.extend(gardes)
            statuts.append({"nom": source["nom"], "ok": True, "nb": len(gardes)})
            print(f"- {source['nom']} : {len(lus)} lu(s), {len(gardes)} gardé(s) pour enfants")
        except Exception as erreur:
            traceback.print_exc()
            statuts.append({"nom": source["nom"], "ok": False, "erreur": str(erreur)})
            print(f"- {source['nom']} : ÉCHEC ({erreur})")

    # Les ajouts manuels sont toujours gardés : on complète seulement âge et catégorie
    ajouts = [completer(e) for e in charger_ajouts_manuels()]
    print(f"- Ajouts manuels : {len(ajouts)} lu(s)")
    evenements.extend(ajouts)

    # On ne garde que les 14 prochains jours, triés par date
    evenements = [e for e in evenements if dans_la_fenetre(e, maintenant)]
    evenements.sort(key=lambda e: e.debut)

    # On écrit le résultat, avec la date de mise à jour
    resultat = {
        "mis_a_jour": maintenant.isoformat(timespec="minutes"),
        "sources": statuts,
        "evenements": [e.en_dict() for e in evenements],
    }
    FICHIER_SORTIE.parent.mkdir(exist_ok=True)
    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        json.dump(resultat, f, ensure_ascii=False, indent=2)

    n = len(evenements)
    print(f"{n} événement{'s' if n > 1 else ''} écrit{'s' if n > 1 else ''} dans {FICHIER_SORTIE.relative_to(DOSSIER)}")


if __name__ == "__main__":
    main()
