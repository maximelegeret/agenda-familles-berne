"""
Fusion des doublons : un même événement présent dans plusieurs sources
(ex. un concert du Menuhin Forum aussi listé par le MuseumsQuartier ou Eventfrog).

Deux événements de sources différentes sont considérés comme le même si :
- ils commencent le même jour, à 30 minutes près ;
- leurs titres se ressemblent (l'un contient l'autre, ou ressemblance ≥ 80 %) ;
- leurs lieux ne sont pas clairement différents (un mot important en commun suffit,
  car les sources nomment les lieux différemment : « Menuhin Forum » / « Yehudi Menuhin Forum Bern »).

On garde la fiche la plus complète, on la complète avec les infos des autres
(âge, prix, adresse…) et on ajoute leurs liens dans `autres_sources`.
"""

import re
import unicodedata
from difflib import SequenceMatcher

ECART_MAX_MINUTES = 30
RESSEMBLANCE_MIN = 0.8
# Mots trop courants pour dire que deux lieux sont le même
MOTS_VIDES = {"bern", "berne", "der", "die", "das", "und", "the", "von", "saal", "haus"}
# Champs recopiés depuis un doublon quand la fiche gardée ne les a pas
CHAMPS_A_COMPLETER = ["description_courte", "fin", "adresse", "latitude", "longitude", "age_min", "age_max",
                      "age_source", "age_texte", "inscription_requise", "categorie", "licence"]


def normaliser(texte):
    """« Peter und der Wolf – Familienkonzert! » -> « peter und der wolf familienkonzert »."""
    texte = unicodedata.normalize("NFKD", texte.lower())
    texte = "".join(c for c in texte if not unicodedata.combining(c))  # ä -> a
    return " ".join(re.sub(r"[^a-z0-9]+", " ", texte).split())


def titres_proches(a, b):
    a, b = normaliser(a), normaliser(b)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    return SequenceMatcher(None, a, b).ratio() >= RESSEMBLANCE_MIN


def lieux_compatibles(a, b):
    mots_a = {m for m in normaliser(a).split() if len(m) >= 4 and m not in MOTS_VIDES}
    mots_b = {m for m in normaliser(b).split() if len(m) >= 4 and m not in MOTS_VIDES}
    if not mots_a or not mots_b:
        return True  # lieu trop vague pour trancher
    return bool(mots_a & mots_b)


def sont_le_meme(e1, e2):
    if e1.source == e2.source:
        return False  # une source ne se répète pas elle-même (ex. même conte dans deux bibliothèques)
    ecart = abs((e1.date_debut() - e2.date_debut()).total_seconds()) / 60
    if e1.debut[:10] != e2.debut[:10] or ecart > ECART_MAX_MINUTES:
        return False
    return titres_proches(e1.titre, e2.titre) and lieux_compatibles(e1.lieu_nom, e2.lieu_nom)


def _richesse(e):
    """Nombre de champs utiles remplis : sert à choisir la fiche à garder."""
    remplis = [e.description_courte, e.fin, e.adresse, e.age_min, e.age_max, e.age_texte,
               e.inscription_requise, e.categorie]
    return sum(v not in (None, "") for v in remplis) + (e.prix != "inconnu")


def _fusionner(groupe):
    """Fusionne un groupe de doublons en une seule fiche."""
    groupe = sorted(groupe, key=_richesse, reverse=True)
    principal = groupe[0]
    for autre in groupe[1:]:
        for champ in CHAMPS_A_COMPLETER:
            if getattr(principal, champ) in (None, "") and getattr(autre, champ) not in (None, ""):
                setattr(principal, champ, getattr(autre, champ))
        if principal.prix == "inconnu" and autre.prix != "inconnu":
            principal.prix = autre.prix
        principal.autres_sources.append({"source": autre.source, "url_source": autre.url_source})
    return principal


def fusionner_doublons(evenements):
    """Renvoie (liste sans doublons, nombre de fusions faites)."""
    groupes = []
    for e in sorted(evenements, key=lambda x: x.debut):
        groupe = next((g for g in groupes if any(sont_le_meme(e, membre) for membre in g)), None)
        if groupe:
            groupe.append(e)
        else:
            groupes.append([e])
    resultat = [_fusionner(g) if len(g) > 1 else g[0] for g in groupes]
    return resultat, len(evenements) - len(resultat)
