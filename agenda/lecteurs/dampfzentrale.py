"""
Lecteur de la Dampfzentrale Bern (Marzilistrasse 47, au bord de l'Aar).

1. La page d'accueil contient tout le programme : un lien par date, avec titre,
   sous-titre et « SO 8.11.26 11:00 ». Le filtre « Junges Publikum » du site est
   chargé en JavaScript, donc inutilisable ici.
2. On lit la fiche de chaque événement des 15 prochains jours : sa rubrique est
   écrite dans <span class="tag"> ; on garde « Junges Publikum ».
   La fiche donne aussi « Preis: … », « Alter: … » et le texte de présentation.
"""

import re
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from agenda.modele import Evenement
from agenda.textes import lire_prix, raccourcir
from agenda.web import telecharger

ACCUEIL = "https://www.dampfzentrale.ch/"
ADRESSE = "Marzilistrasse 47, 3005 Bern"
NB_JOURS = 15
RUBRIQUE_ENFANTS = "junges publikum"
RE_DATE = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{2})(?:\s+(\d{1,2}):(\d{2}))?")
# « Preis: CHF 10.– » ou « Kosten: 10.- pro Person »
RE_PRIX = re.compile(r"(?:Preis|Kosten):\s*((?:CHF\s*)?\d+(?:[.,]\d+)?|gratis|kostenlos|Eintritt frei)", re.I)
# « Alter: zwischen 5 und 10 Jahren », sinon « Für alle von 13 bis 16 Jahren » ou « ab 5 Jahren »
RE_AGE_ALTER = re.compile(r"Alter:\s*(.{0,40}?Jahren)")
RE_AGE = re.compile(r"((?:von |zwischen |ab )\d+(?:\s*(?:bis|und|-)\s*\d+)?\s*Jahren)", re.I)
RE_PRATIQUE = re.compile(r"Ticket|@|anmelden|Anmeldung|Kosten:|Preis:", re.I)


def lire_programme(page_html):
    """Renvoie toutes les dates du programme : dicts {debut, titre, sous_titre, url} (sans doublon)."""
    soupe = BeautifulSoup(page_html, "html.parser")
    dates, vues = [], set()
    for lien in soupe.select('a.overlay-link[href*="/event/"]'):
        titre = lien.find("h2")
        sous_titre = lien.find("h3")
        m = RE_DATE.search(lien.get_text(" ", strip=True))
        if not titre or not m:
            continue
        j, mo, a, h, mi = m.groups()
        debut = datetime(2000 + int(a), int(mo), int(j), int(h or 0), int(mi or 0))
        nom = titre.get_text(" ", strip=True)
        if (nom, debut) in vues:
            continue  # même événement listé deux fois (ex. « Wild Card »)
        vues.add((nom, debut))
        dates.append({
            "debut": debut,
            "titre": nom,
            "sous_titre": sous_titre.get_text(" ", strip=True) if sous_titre else "",
            "url": lien["href"],
        })
    return dates


def lire_fiche(page_html):
    """Renvoie {"rubrique", "prix", "age", "texte"} depuis la fiche d'un événement."""
    soupe = BeautifulSoup(page_html, "html.parser")
    rubrique = soupe.select_one("span.tag")
    texte_page = re.sub(r"\s+", " ", soupe.get_text(" ", strip=True))
    prix = RE_PRIX.search(texte_page)
    age = RE_AGE_ALTER.search(texte_page) or RE_AGE.search(texte_page)
    # Présentation : premier long paragraphe qui n'est pas une info pratique (tickets, contact…)
    paragraphes = [p.get_text(" ", strip=True) for p in soupe.find_all("p")]
    texte = next((p for p in paragraphes if len(p) > 80 and not RE_PRATIQUE.search(p)), "")
    return {
        "rubrique": rubrique.get_text(" ", strip=True) if rubrique else "",
        "prix": lire_prix(prix.group(1)) if prix else "inconnu",
        "age": age.group(1) if age else "",
        "texte": raccourcir(texte),
    }


def lire(source):
    """Point d'entrée appelé par recuperer.py."""
    limite = datetime.now() + timedelta(days=NB_JOURS)
    dates = [d for d in lire_programme(telecharger(ACCUEIL).text) if d["debut"] <= limite]
    fiches = {url: lire_fiche(telecharger(url).text) for url in {d["url"] for d in dates}}
    evenements = []
    for d in dates:
        fiche = fiches[d["url"]]
        if RUBRIQUE_ENFANTS not in fiche["rubrique"].lower():
            continue
        texte = fiche["texte"] or d["sous_titre"]
        evenements.append(Evenement(
            id=f"dampfzentrale-{d['url'].rstrip('/').rsplit('/', 1)[-1][:40]}-{d['debut']:%Y%m%d%H%M}",
            titre=d["titre"],
            description_courte=texte,
            debut=d["debut"].strftime("%Y-%m-%dT%H:%M"),
            lieu_nom="Dampfzentrale Bern",
            adresse=ADRESSE,
            age_texte=fiche["age"],
            prix=fiche["prix"],
            source="Dampfzentrale Bern",
            url_source=d["url"],
        ))
    return evenements
