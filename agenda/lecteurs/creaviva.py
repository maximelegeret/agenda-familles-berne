"""
Lecteur du Creaviva (atelier pour enfants du Zentrum Paul Klee).

Le site zpk.org est alimenté par une API publique (Drupal JSON:API) :
- « activity » = une séance datée (début, fin) ;
- « event »    = l'offre (titre, texte, âge, ticket) à laquelle la séance appartient ;
- chaque offre appartient à un « espace » : 18 = Creaviva, 5 = Zentrum Paul Klee,
  7 = Kunstmuseum Bern (numéros relevés le 7 nov. 2026).
Le même lecteur pourra donc servir au Kunstmuseum (vague 2) en changeant l'espace dans sources.yaml.
"""

import re
from datetime import datetime, timedelta

from agenda.modele import Evenement
from agenda.web import telecharger

API = "https://kmbzpk.nodehive.app/de/jsonapi/node/activity"
SITE = "https://zpk.org/de"
NB_JOURS = 15  # un jour de marge sur la fenêtre de 14 jours

# Catégorie « Kurse für Erwachsene (ab 16 J.) » : jamais pour les enfants
CATEGORIE_ADULTES = 298

# On ne demande que les champs utiles, pour des réponses plus légères
CHAMPS = {
    "fields[node--activity]": "field_activity_date,field_activity_ref_event",
    "fields[node--event]": ("drupal_internal__nid,title,path,field_teaser_text,field_location,"
                            "field_additional_information,field_additional_information_2,"
                            "nodehive_space,field_ref_category,field_ref_product"),
    "fields[commerce_product--ticket]": "variations",
    "fields[commerce_product_variation--ticket]": "title,price",
}
INCLURE = "field_activity_ref_event,field_activity_ref_event.field_ref_product.variations"

MOTS_AGE = ("j.", "jahre", "kinder", "familie", "ans", "erwachsene")
RE_TAGLICH = re.compile(r"täglich zwischen (\d{1,2}:\d{2})\s*[–-]\s*(\d{1,2}:\d{2})", re.IGNORECASE)


def telecharger_activites(debut, fin):
    """Télécharge les séances entre deux dates. Renvoie (séances, objets liés par identifiant)."""
    params = {
        "filter[d1][condition][path]": "field_activity_date.value",
        "filter[d1][condition][operator]": ">=",
        "filter[d1][condition][value]": debut.strftime("%Y-%m-%dT00:00:00"),
        "filter[d2][condition][path]": "field_activity_date.value",
        "filter[d2][condition][operator]": "<",
        "filter[d2][condition][value]": fin.strftime("%Y-%m-%dT00:00:00"),
        "include": INCLURE,
        "sort": "field_activity_date.value",
        "page[limit]": 50,
        **CHAMPS,
    }
    seances, lies = [], {}
    url = API
    while url:
        donnees = telecharger(url, params=params).json()
        seances += donnees["data"]
        for objet in donnees.get("included", []):
            lies[objet["id"]] = objet
        # L'API découpe en pages ; le lien « next » contient déjà tous les paramètres
        url = donnees.get("links", {}).get("next", {}).get("href")
        params = None
    return seances, lies


def _relation(objet, nom):
    """Renvoie la cible d'une relation (dict ou liste), ou None."""
    return (objet.get("relationships", {}).get(nom) or {}).get("data")


def _prix(offre, lies):
    """Prix du ticket « regulär » (adulte ou enfant), sinon 'inconnu'."""
    produit = _relation(offre, "field_ref_product")
    if not produit or produit["id"] not in lies:
        return "inconnu"
    variantes = [lies[v["id"]] for v in _relation(lies[produit["id"]], "variations") or [] if v["id"] in lies]
    for v in variantes:
        if "regul" in (v["attributes"].get("title") or "").lower() and v["attributes"].get("price"):
            montant = float(v["attributes"]["price"]["number"])
            return "gratuit" if montant == 0 else f"{montant:g} CHF"
    return "inconnu"


def analyser(seances, lies, espace, nom_source):
    """Transforme les séances de l'API en Evenement, pour un espace donné."""
    evenements = []
    for seance in seances:
        cible = _relation(seance, "field_activity_ref_event")
        offre = lies.get(cible["id"]) if cible else None
        if not offre:
            continue
        espaces = [e["meta"]["drupal_internal__target_id"] for e in _relation(offre, "nodehive_space") or []]
        if espace not in espaces:
            continue
        categorie = _relation(offre, "field_ref_category")
        if categorie and categorie["meta"]["drupal_internal__target_id"] == CATEGORIE_ADULTES:
            continue
        a = offre["attributes"]
        if a["title"].upper().startswith("ABGESAGT"):  # séance annulée
            continue

        # Les champs « lieu » et « infos » contiennent tantôt l'âge, tantôt une salle ou un horaire
        extras = [t.strip() for t in (a.get("field_location"), a.get("field_additional_information_2"),
                                      a.get("field_additional_information")) if t and t.strip()]
        age_texte = next((t for t in extras if any(m in t.lower() for m in MOTS_AGE)), "")
        autres_infos = [t for t in extras if t != age_texte and not t.lower().startswith(("dauer", "treffpunkt"))]
        description = (a.get("field_teaser_text") or "").strip()
        if len(description) > 200:
            description = description[:197].rsplit(" ", 1)[0] + "…"
        if autres_infos:
            description = (description + " " + " · ".join(autres_infos)).strip()

        dates = seance["attributes"]["field_activity_date"]
        debut = datetime.fromisoformat(dates["value"])
        fin = datetime.fromisoformat(dates["end_value"]) if dates.get("end_value") else None
        chemin = (a.get("path") or {}).get("alias") or ""

        # « Täglich zwischen 10:00–17:00 » : l'horaire réel est dans le texte, pas dans la séance
        horaire = next((RE_TAGLICH.search(t) for t in extras if RE_TAGLICH.search(t)), None)
        if horaire:
            h1, h2 = horaire.groups()
            debut = debut.replace(hour=int(h1.split(":")[0]), minute=int(h1.split(":")[1]))
            fin = debut.replace(hour=int(h2.split(":")[0]), minute=int(h2.split(":")[1]))

        prix = _prix(offre, lies)
        if prix == "inconnu" and any(m in " ".join(extras).lower() for m in ("kostenlos", "gratis")):
            prix = "gratuit"

        evenements.append(Evenement(
            id=f"creaviva-{a['drupal_internal__nid']}-{debut:%Y%m%d%H%M}",
            # « Vogelperspektive: Workshop Offenes Atelier » -> on garde le titre complet, plus parlant
            titre=a["title"],
            description_courte=description,
            debut=debut.strftime("%Y-%m-%dT%H:%M"),
            fin=fin.strftime("%Y-%m-%dT%H:%M") if fin else None,
            lieu_nom="Creaviva, Zentrum Paul Klee",
            adresse="Monument im Fruchtland 3, 3006 Bern",
            age_texte=age_texte,
            prix=prix,
            categorie="atelier",
            source=nom_source,
            url_source=SITE + chemin if chemin else SITE + "/creaviva",
        ))
    return evenements


def lire(source):
    """Point d'entrée appelé par recuperer.py."""
    aujourd_hui = datetime.now()
    seances, lies = telecharger_activites(aujourd_hui, aujourd_hui + timedelta(days=NB_JOURS))
    return analyser(seances, lies, source.get("espace", 18), source["nom"])
