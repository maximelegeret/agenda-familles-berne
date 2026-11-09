"""
Script principal : récupère les événements de toutes les sources actives
et les écrit dans docs/events.json, que la page web affiche.

Lancement :  python recuperer.py
"""

import importlib
import json
import os
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from agenda import ajouts, lieux
from agenda.calendrier import ecrire_ics
from agenda.doublons import fusionner_doublons
from agenda.filtre_enfants import completer, trier
from agenda.regulier import separer

# Dossier du projet (là où se trouve ce fichier)
DOSSIER = Path(__file__).parent
FICHIER_SOURCES = DOSSIER / "sources.yaml"
FICHIER_AJOUTS = DOSSIER / "ajouts_manuels.yaml"
FICHIER_OFFRES = DOSSIER / "offres_regulieres.yaml"
FICHIER_SORTIE = DOSSIER / "docs" / "events.json"
FICHIER_AGENDA = DOSSIER / "docs" / "agenda.ics"
FICHIER_LIEUX = DOSSIER / "lieux.yaml"
FICHIER_LIEUX_SORTIE = DOSSIER / "docs" / "lieux.json"

# Toutes les dates du projet sont à l'heure de Berne
FUSEAU = ZoneInfo("Europe/Zurich")
# On garde les événements des 14 prochains jours
NB_JOURS = 14


def charger_env():
    """
    Lit le fichier local .env (s'il existe) et met ses lignes NOM=valeur dans l'environnement.
    Sert aux essais sur l'ordinateur : .env contient les jetons (ex. EVENTFROG_TOKEN) et n'est
    jamais envoyé sur GitHub (.gitignore). Sur GitHub, les jetons viennent des secrets du dépôt.
    """
    fichier = DOSSIER / ".env"
    if not fichier.exists():
        return
    for ligne in fichier.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if ligne and not ligne.startswith("#") and "=" in ligne:
            nom, valeur = ligne.split("=", 1)
            # Une valeur déjà présente dans l'environnement reste prioritaire
            os.environ.setdefault(nom.strip(), valeur.strip().strip('"').strip("'"))


def charger_sources():
    """Lit sources.yaml et renvoie la liste des sources actives."""
    with open(FICHIER_SOURCES, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return [s for s in config["sources"] if s.get("actif")]


def charger_ajouts_manuels():
    """Lit ajouts_manuels.yaml et renvoie la liste des Evenement valides (les erreurs sont ignorées)."""
    evenements, _ = ajouts.charger(FICHIER_AJOUTS)
    return evenements


def dans_la_fenetre(evenement, maintenant):
    """Vrai si l'événement n'est pas terminé et commence dans les 14 prochains jours."""
    debut = evenement.date_debut().replace(tzinfo=FUSEAU)
    fin = datetime.fromisoformat(evenement.fin).replace(tzinfo=FUSEAU) if evenement.fin else debut
    limite = maintenant.replace(hour=0, minute=0) + timedelta(days=NB_JOURS + 1)
    # Sans heure de fin, on considère qu'il dure 2 heures (une visite de 11:00 disparaît à 13:00)
    if not evenement.fin:
        fin = debut + timedelta(hours=2)
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


def ecrire_lieux(maintenant):
    """Lit lieux.yaml, calcule les horaires des 14 prochains jours et écrit docs/lieux.json."""
    liste, erreurs = lieux.charger(FICHIER_LIEUX, aujourd_hui=maintenant.date(), nb_jours=NB_JOURS)
    for erreur in erreurs:
        print(f"    ⚠️  lieu écarté : {erreur}")
    with open(FICHIER_LIEUX_SORTIE, "w", encoding="utf-8") as f:
        json.dump({"mis_a_jour": maintenant.isoformat(timespec="minutes"), "lieux": liste},
                  f, ensure_ascii=False, indent=2)
    print(f"{len(liste)} lieux écrits dans {FICHIER_LIEUX_SORTIE.relative_to(DOSSIER)}")


def main():
    charger_env()
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
    manuels, erreurs = ajouts.charger(FICHIER_AJOUTS)
    manuels = [completer(e) for e in manuels]
    print(f"- Ajouts manuels : {len(manuels)} lu(s)")
    for erreur in erreurs:
        print(f"    ⚠️  {erreur}")
    if erreurs:
        # Visible aussi sur la page, pour ne pas croire qu'un ajout a été pris en compte
        statuts.append({"nom": "Ajouts manuels", "ok": False, "erreur": " ; ".join(erreurs)})
    evenements.extend(manuels)

    # On ne garde que les 14 prochains jours, triés par date
    evenements = [e for e in evenements if dans_la_fenetre(e, maintenant)]

    # Un même événement vu dans plusieurs sources n'apparaît qu'une fois
    evenements, nb_fusions = fusionner_doublons(evenements)
    print(f"- Doublons fusionnés : {nb_fusions}")
    evenements.sort(key=lambda e: e.debut)

    # Les activités qui reviennent chaque semaine vont dans la section « Chaque semaine »
    evenements, offres = separer(evenements)

    # … plus les offres fixes écrites à la main (ex. le Pünktli du MüZe)
    fixes, erreurs_offres = ajouts.charger_offres(FICHIER_OFFRES)
    for erreur in erreurs_offres:
        print(f"    ⚠️  {erreur}")
    offres += [completer(o) for o in fixes]
    print(f"- Offres régulières : {len(offres)} ({', '.join(o.titre[:30] for o in offres)})")

    # On écrit le résultat, avec la date de mise à jour
    resultat = {
        "mis_a_jour": maintenant.isoformat(timespec="minutes"),
        "sources": statuts,
        "offres_regulieres": [o.en_dict() for o in offres],
        "evenements": [e.en_dict() for e in evenements],
    }
    FICHIER_SORTIE.parent.mkdir(exist_ok=True)
    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        json.dump(resultat, f, ensure_ascii=False, indent=2)

    n = len(evenements)
    print(f"{n} événement{'s' if n > 1 else ''} et {len(offres)} offre(s) régulière(s) "
          f"écrits dans {FICHIER_SORTIE.relative_to(DOSSIER)}")

    # Flux d'agenda auquel on peut s'abonner depuis le téléphone
    ecrire_ics(evenements, FICHIER_AGENDA, maintenant)
    print(f"Flux d'agenda écrit dans {FICHIER_AGENDA.relative_to(DOSSIER)}")

    # Lieux permanents de l'onglet « Sortir », avec leurs horaires des prochains jours
    ecrire_lieux(maintenant)


if __name__ == "__main__":
    main()
