"""
Lecteur du MuseumsQuartier Bern (mqb.ch) : agenda commun du Musée d'histoire,
du Musée d'histoire naturelle, du Musée alpin, de la Kunsthalle, du Musée de la communication…

Comment ça marche :
1. La page agenda accepte les filtres dans l'adresse : public « Children & Family »
   (Audiences[1]) et types Event / Guided tour / Workshop (Activities[2], [3], [4]).
   Les expositions (Activities[1]) sont exclues : ce ne sont pas des activités datées.
   Avec ces filtres, la page liste toutes les prochaines dates d'un coup.
2. Pour chaque événement, la fiche détaillée donne toutes les séances (« Next dates »),
   le prix, le lieu et le texte de présentation.

Le site demande 10 secondes entre deux pages (robots.txt) : on respecte ce délai.
"""

import re
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from agenda.modele import Evenement
from agenda.textes import lire_inscription, lire_prix, raccourcir
from agenda.web import telecharger

SITE = "https://www.mqb.ch"
AGENDA = SITE + "/en/agenda"
FILTRES = {"Audiences[1]": 1, "Activities[2]": 2, "Activities[3]": 3, "Activities[4]": 4}
PAUSE = 10  # secondes entre deux pages, demandé par le site

MOIS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}
# « Sunday, 29. November 2026 » puis « 11:00 - 11:40 »
RE_JOUR = re.compile(r"(\d{1,2})\.\s*([A-Za-z]+)\s+(\d{4})")
RE_LANGUE = re.compile(r"^(only in german|nur auf deutsch|only in french|nur auf französisch)\s*!?", re.IGNORECASE)
RE_HEURES = re.compile(r"(\d{1,2}):(\d{2})(?:\s*-\s*(\d{1,2}):(\d{2}))?")


def liens_evenements(page_html):
    """Renvoie les adresses (sans doublon) des fiches listées dans la page agenda."""
    soupe = BeautifulSoup(page_html, "html.parser")
    liens = []
    for article in soupe.find_all("article"):
        lien = article.select_one("h3 a[href]")
        if lien:
            url = urljoin(SITE, lien["href"])
            if url not in liens:
                liens.append(url)
    return liens


def _bloc(soupe, titre):
    """Le bloc qui suit un intertitre h2 (« Next dates », « Admission prices »…)."""
    h2 = soupe.find("h2", string=re.compile(rf"^\s*{titre}\s*$"))
    return h2.parent if h2 else None


def analyser_fiche(page_html, url):
    """Lit une fiche mqb.ch et renvoie un Evenement par séance."""
    soupe = BeautifulSoup(page_html, "html.parser")
    titre = soupe.find("h1").get_text(" ", strip=True)

    # Lieu (nom de l'institution)
    bloc_lieu = _bloc(soupe, "Location")
    lieu = bloc_lieu.find("li").get_text(" ", strip=True) if bloc_lieu and bloc_lieu.find("li") else "MuseumsQuartier Bern"

    # Prix
    bloc_prix = _bloc(soupe, "Admission prices")
    texte_prix = bloc_prix.get_text(" ", strip=True).replace("Admission prices", "") if bloc_prix else ""

    # Texte de présentation : le chapeau (paragraphe en gros caractères), puis le contenu, hors prix
    paragraphes = []
    for p in soupe.select("main p[class*='text,2xl'], .typography p"):
        if bloc_prix and p in bloc_prix.find_all("p"):
            continue
        # On retire la mention « Only in German! » placée en tête de certains textes
        texte = RE_LANGUE.sub("", p.get_text(" ", strip=True)).strip()
        if texte:
            paragraphes.append(texte)
    texte_complet = " ".join(paragraphes) + " " + soupe.get_text(" ", strip=True)

    evenements = []
    bloc_dates = _bloc(soupe, "Next dates")
    for ligne in bloc_dates.find_all("li") if bloc_dates else []:
        jour = RE_JOUR.search(ligne.get_text(" ", strip=True))
        heures = RE_HEURES.search(ligne.get_text(" ", strip=True))
        if not jour or not heures:
            continue
        j, mois, annee = jour.groups()
        date = datetime(int(annee), MOIS[mois.lower()], int(j))
        h1, m1, h2, m2 = heures.groups()
        debut = date.replace(hour=int(h1), minute=int(m1))
        fin = date.replace(hour=int(h2), minute=int(m2)) if h2 else None
        evenements.append(Evenement(
            id=f"mqb-{url.rstrip('/').rsplit('/', 1)[-1]}-{debut:%Y%m%d%H%M}",
            titre=titre,
            description_courte=raccourcir(paragraphes[0]) if paragraphes else "",
            debut=debut.strftime("%Y-%m-%dT%H:%M"),
            fin=fin.strftime("%Y-%m-%dT%H:%M") if fin else None,
            lieu_nom=lieu,
            prix=lire_prix(texte_prix),
            inscription_requise=lire_inscription(texte_complet),
            source="MuseumsQuartier Bern",
            url_source=url,
        ))
    return evenements


def lire(source):
    """Point d'entrée appelé par recuperer.py."""
    agenda = telecharger(AGENDA, params=FILTRES, pause=PAUSE).text
    evenements = []
    for url in liens_evenements(agenda):
        evenements += analyser_fiche(telecharger(url, pause=PAUSE).text, url)
    return evenements
