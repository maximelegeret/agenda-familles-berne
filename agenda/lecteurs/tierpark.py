"""
Lecteur du Tierpark Bern (Dählhölzli et BärenPark).

1. Le calendrier (/veranstaltungskalender/) liste les activités en cartes :
   titre · « Datum: 11.11.2026 » · « Uhrzeit: 14:00 Uhr » · « Ort: Dählhölzli »
   et des pictogrammes, dont « Event für Kinder » posé par le Tierpark.
2. On garde les activités marquées pour enfants (ou dont le titre parle d'enfants).
3. Chaque fiche a des champs étiquetés (<h3> puis <p>) : Datum (avec l'heure de fin),
   Kosten, Zielgruppe (« Für Kinder von 4 bis 6 Jahren. ») et un texte de présentation.
"""

import re
from datetime import datetime

from bs4 import BeautifulSoup

from agenda.modele import Evenement
from agenda.textes import lire_inscription, lire_prix, raccourcir
from agenda.web import telecharger

CALENDRIER = "https://tierpark-bern.ch/veranstaltungskalender/"
LIEUX = {
    "Dählhölzli": ("Tierpark Dählhölzli", "Tierparkweg 1, 3005 Bern"),
    "BärenPark": ("BärenPark", "Grosser Muristalden 6, 3006 Bern"),
}
RE_DATE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{4})")
RE_HEURES = re.compile(r"(\d{1,2}):(\d{2})(?:\s*-\s*(\d{1,2}):(\d{2}))?")


def _valeur(carte, etiquette):
    """Texte après « Datum: », « Uhrzeit: », « Ort: » dans une carte du calendrier."""
    for bloc in carte.select(".calendar-item__time, .calendar-item__category"):
        texte = bloc.get_text(" ", strip=True)
        if texte.startswith(etiquette):
            return texte[len(etiquette):].strip(" :")
    return ""


def lire_calendrier(page_html):
    """Renvoie les activités pour enfants : dicts {titre, complet, debut, lieu, url}."""
    soupe = BeautifulSoup(page_html, "html.parser")
    activites = []
    for carte in soupe.select(".events-item"):
        titre = carte.select_one(".events-item__title").get_text(" ", strip=True)
        pictos = [img.get("alt", "") for img in carte.select(".calender-accessibility img")]
        if "Event für Kinder" not in pictos and not re.search(r"kinder|familie", titre, re.I):
            continue
        d = RE_DATE.search(_valeur(carte, "Datum"))
        h = RE_HEURES.search(_valeur(carte, "Uhrzeit"))
        if not d:
            continue
        complet = titre.lower().startswith("ausverkauft")
        activites.append({
            "titre": re.sub(r"^Ausverkauft:\s*", "", titre, flags=re.I),
            "complet": complet,
            "debut": datetime(int(d.group(3)), int(d.group(2)), int(d.group(1)),
                              int(h.group(1)) if h else 0, int(h.group(2)) if h else 0),
            "lieu": _valeur(carte, "Ort"),
            "url": carte.get("data-href") or carte.find("a", href=True)["href"],
        })
    return activites


def lire_fiche(page_html):
    """Champs étiquetés de la fiche : {"Datum": …, "Kosten": …, "Zielgruppe": …, "texte": …}."""
    soupe = BeautifulSoup(page_html, "html.parser")
    champs = {}
    for h3 in soupe.select("h3.event-details"):
        valeur = h3.find_next_sibling("p")
        if valeur:
            champs[h3.get_text(" ", strip=True)] = valeur.get_text(" ", strip=True)
    corps = soupe.select_one(".mt-3")
    if corps:
        sous_titre = corps.find("h2")
        premier = corps.find("p")
        morceaux = [x.get_text(" ", strip=True) for x in (sous_titre, premier) if x]
        champs["texte"] = raccourcir(" – ".join(morceaux))
    return champs


def vers_evenement(activite, champs):
    debut = activite["debut"]
    fin = None
    h = RE_HEURES.search(champs.get("Datum", ""))
    if h and h.group(3):
        debut = debut.replace(hour=int(h.group(1)), minute=int(h.group(2)))
        fin = debut.replace(hour=int(h.group(3)), minute=int(h.group(4)))
    lieu, adresse = LIEUX.get(activite["lieu"], (activite["lieu"] or "Tierpark Bern", ""))
    texte = champs.get("texte", "")
    if activite["complet"]:
        texte = f"Ausverkauft. {texte}".strip()
    return Evenement(
        id=f"tierpark-{activite['url'].rstrip('/').rsplit('/', 1)[-1]}-{debut:%Y%m%d%H%M}",
        titre=activite["titre"],
        description_courte=texte,
        debut=debut.strftime("%Y-%m-%dT%H:%M"),
        fin=fin.strftime("%Y-%m-%dT%H:%M") if fin else None,
        lieu_nom=lieu,
        adresse=adresse,
        age_texte=champs.get("Zielgruppe", ""),
        prix=lire_prix(champs.get("Kosten")),
        inscription_requise=lire_inscription(" ".join(champs.values())),
        source="Tierpark Bern",
        url_source=activite["url"],
    )


def lire(source):
    """Point d'entrée appelé par recuperer.py."""
    activites = lire_calendrier(telecharger(CALENDRIER).text)
    return [vers_evenement(a, lire_fiche(telecharger(a["url"]).text)) for a in activites]
