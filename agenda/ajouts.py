"""
Lecture des événements ajoutés à la main (fichier ajouts_manuels.yaml).

Pour que l'ajout soit simple, seuls trois champs sont obligatoires : titre, debut, lieu_nom.
Le reste est complété automatiquement (identifiant, source « Ajout manuel »…).
Une fiche mal écrite est ignorée avec un message clair : elle ne bloque pas les autres.
"""

import re
import unicodedata
from datetime import date, datetime
from pathlib import Path

import yaml

from agenda.modele import Evenement

OBLIGATOIRES = ["titre", "debut", "lieu_nom"]
SOURCE_PAR_DEFAUT = "Ajout manuel"


def _texte_date(valeur):
    """
    Accepte « 2026-11-08T16:00 », « 2026-11-08 16:00 » ou « 2026-11-08 » (journée entière à 00:00).
    YAML transforme parfois une date en objet : on la remet en texte.
    """
    if isinstance(valeur, datetime):
        return valeur.strftime("%Y-%m-%dT%H:%M")
    if isinstance(valeur, date):
        return valeur.strftime("%Y-%m-%dT00:00")
    texte = str(valeur).strip().replace(" ", "T")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", texte):
        texte += "T00:00"
    datetime.fromisoformat(texte)  # erreur claire si la date est mal écrite
    return texte


def _identifiant(titre, debut):
    """« Fäger: Zirkus » + « 2026-11-20T14:00 » -> « manuel-fager-zirkus-202611201400 »."""
    sans_accents = unicodedata.normalize("NFKD", titre.lower()).encode("ascii", "ignore").decode()
    mots = re.sub(r"[^a-z0-9]+", "-", sans_accents).strip("-")[:40]
    return f"manuel-{mots}-{debut.replace('-', '').replace(':', '').replace('T', '')}"


def lire_fiche(donnees):
    """Transforme une fiche du fichier YAML en Evenement (lève ValueError si elle est invalide)."""
    if not isinstance(donnees, dict):
        raise ValueError("ce n'est pas une fiche (chaque fiche commence par « - titre: … »)")
    manquants = [c for c in OBLIGATOIRES if not donnees.get(c)]
    if manquants:
        raise ValueError(f"champ(s) obligatoire(s) manquant(s) : {', '.join(manquants)}")
    connus = set(Evenement.__dataclass_fields__)
    inconnus = [c for c in donnees if c not in connus]
    if inconnus:
        raise ValueError(f"champ(s) inconnu(s) : {', '.join(inconnus)} (faute de frappe ?)")

    fiche = dict(donnees)
    fiche["titre"] = str(fiche["titre"])
    fiche["debut"] = _texte_date(fiche["debut"])
    if fiche.get("fin"):
        fiche["fin"] = _texte_date(fiche["fin"])
    if fiche.get("prix") is not None:
        fiche["prix"] = str(fiche["prix"])
    fiche.setdefault("source", SOURCE_PAR_DEFAUT)
    fiche.setdefault("url_source", "")
    fiche.setdefault("id", _identifiant(fiche["titre"], fiche["debut"]))
    return Evenement(**fiche)


def charger(chemin):
    """Lit le fichier. Renvoie (événements valides, liste des erreurs lisibles)."""
    chemin = Path(chemin)
    if not chemin.exists():
        return [], []
    try:
        contenu = yaml.safe_load(chemin.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as erreur:
        return [], [f"le fichier n'est pas lisible (vérifie les espaces et les « : ») : {erreur}"]

    evenements, erreurs = [], []
    for numero, donnees in enumerate(contenu.get("evenements") or [], start=1):
        try:
            evenements.append(lire_fiche(donnees))
        except (ValueError, TypeError) as erreur:
            titre = donnees.get("titre", "sans titre") if isinstance(donnees, dict) else "?"
            erreurs.append(f"fiche n°{numero} (« {titre} ») ignorée : {erreur}")
    return evenements, erreurs
