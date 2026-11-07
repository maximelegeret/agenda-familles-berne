"""
Lecteur des Kornhausbibliotheken (kob.ch, ~20 bibliothèques de Berne et environs).

Comment ça marche :
1. L'API WordPress du site donne la liste des événements avec leurs catégories et âges,
   mais PAS les dates. On s'en sert pour repérer les événements pour enfants.
2. Pour chacun, on lit la fiche HTML : le tableau « Auf einen Blick » contient
   Zeit (une ou plusieurs dates), Ort, Kosten, Alter.
3. Une fiche avec plusieurs dates donne un événement par date.
"""

import html
import re
from datetime import datetime

from bs4 import BeautifulSoup

from agenda.modele import Evenement
from agenda.textes import lire_inscription, lire_prix, raccourcir  # noqa: F401 (utilisés aussi par les tests)
from agenda.web import telecharger

NOM_SOURCE = "Kornhausbibliotheken"
API = "https://www.kob.ch/wp-json/wp/v2/veranstaltung"

# Catégories kob.ch qui sont toujours pour les enfants
# (numéros relevés le 7 nov. 2026 via /wp-json/wp/v2/categories)
CATEGORIES_ENFANTS = {
    55: "Kinderanlass",
    227: "Buchstart",
    218: "Schenk mir eine Geschichte",
}

MOIS = {
    "januar": 1, "februar": 2, "märz": 3, "april": 4, "mai": 5, "juni": 6,
    "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "dezember": 12,
}

# Une date, ex. « Samstag, 07. November 2026 »
_DATE = r"(\d{1,2})\.\s*([A-Za-zäÄ]+)\s+(\d{4})"
# Date simple : « Samstag, 07. November 2026, 16:00-17:00 Uhr »
RE_DATE_SIMPLE = re.compile(_DATE + r",\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})")
# Période : « Freitag, 13. November 2026 bis Samstag, 14. November 2026, 18:00-08:30 Uhr »
RE_PERIODE = re.compile(_DATE + r"\s+bis\s+\w+,\s*" + _DATE + r",\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})")

def _date_iso(jour, mois, annee, heure):
    """('07', 'November', '2026', '16:00') -> '2026-11-07T16:00'"""
    h, m = heure.split(":")
    d = datetime(int(annee), MOIS[mois.lower()], int(jour), int(h), int(m))
    return d.isoformat(timespec="minutes")


def lire_dates(texte):
    """
    Transforme le texte « Zeit » en liste de (début, fin) au format ISO.
    Gère les dates multiples et les périodes sur deux jours.
    """
    resultats = []
    # D'abord les périodes « … bis … », qu'on retire ensuite du texte
    for m in RE_PERIODE.finditer(texte):
        j1, mo1, a1, j2, mo2, a2, h1, h2 = m.groups()
        resultats.append((_date_iso(j1, mo1, a1, h1), _date_iso(j2, mo2, a2, h2)))
    texte = RE_PERIODE.sub("", texte)
    for m in RE_DATE_SIMPLE.finditer(texte):
        j, mo, a, h1, h2 = m.groups()
        resultats.append((_date_iso(j, mo, a, h1), _date_iso(j, mo, a, h2)))
    return sorted(resultats)


def analyser_fiche(page_html, url, id_wordpress, titre):
    """Lit une fiche HTML kob.ch et renvoie un Evenement par date."""
    soupe = BeautifulSoup(page_html, "html.parser")

    # Tableau « Auf einen Blick » : {"Zeit": "...", "Ort": "...", ...}
    infos = {}
    for ligne in soupe.select(".entry-content table tr"):
        cases = ligne.find_all("td")
        if len(cases) >= 2:
            infos[cases[0].get_text(strip=True)] = cases[1].get_text(" ", strip=True)

    # Texte de présentation, à côté de l'image
    bloc = soupe.select_one(".um-next-to-thumb")
    paragraphes = [p.get_text(" ", strip=True) for p in bloc.find_all("p")] if bloc else []
    paragraphes = [p for p in paragraphes if p]
    texte_complet = " ".join(paragraphes)
    description = raccourcir(paragraphes[0]) if paragraphes else ""

    evenements = []
    for debut, fin in lire_dates(infos.get("Zeit", "")):
        evenements.append(Evenement(
            id=f"kob-{id_wordpress}-{debut[:16].replace('-', '').replace(':', '').replace('T', '')}",
            titre=titre,
            description_courte=description,
            debut=debut,
            fin=fin,
            lieu_nom=infos.get("Ort", "Kornhausbibliotheken"),
            age_texte=infos.get("Alter", ""),
            prix=lire_prix(infos.get("Kosten")),
            inscription_requise=lire_inscription(texte_complet),
            source=NOM_SOURCE,
            url_source=url,
        ))
    return evenements


def est_pour_enfants(fiche_api):
    """Vrai si l'événement est dans une catégorie enfants ou a une tranche d'âge."""
    return bool(set(fiche_api["categories"]) & CATEGORIES_ENFANTS.keys()) or bool(fiche_api["alter"])


def lire(source):
    """Point d'entrée appelé par recuperer.py : renvoie la liste des événements."""
    # 1. Liste de tous les événements publiés (100 par page)
    fiches = []
    page = 1
    while True:
        reponse = telecharger(API, params={
            "per_page": 100, "page": page, "_fields": "id,link,title,categories,alter",
        })
        fiches += reponse.json()
        if page >= int(reponse.headers.get("X-WP-TotalPages", 1)):
            break
        page += 1

    # 2. Lecture de la fiche de chaque événement pour enfants
    evenements = []
    for fiche in filter(est_pour_enfants, fiches):
        titre = html.unescape(fiche["title"]["rendered"])
        page_html = telecharger(fiche["link"]).text
        evenements += analyser_fiche(page_html, fiche["link"], fiche["id"], titre)
    return evenements
