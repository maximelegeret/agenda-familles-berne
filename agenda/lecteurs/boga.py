"""
Lecteur du Botanischer Garten der Universität Bern (BOGA, Altenbergrain 21).

La page agenda liste toutes les dates en cartes structurées (schema.org) :
  startDate « 2026-11-25T14:00:00+01:00 », « 14:00 − 16:00 », rubrique
  (« Zaubergarten (Kinderfreizeit) », « Thementage », « Führung »…) et titre.
On garde la rubrique Kinderfreizeit (le Zaubergarten, dès 6 ans selon le site)
et les journées thématiques « für Gross und Klein ». La fiche donne le texte
et l'inscription ; le prix n'est pas chiffré (« kostenpflichtig »).
"""

import re
from datetime import datetime

from bs4 import BeautifulSoup

from agenda.modele import Evenement
from agenda.textes import raccourcir
from agenda.web import telecharger

AGENDA = "https://www.boga.unibe.ch/agenda/index_ger.html"
ADRESSE = "Altenbergrain 21, Bern"
RUBRIQUES_ENFANTS = ("kinderfreizeit", "thementag")
# La page « Kinderfreizeit » du BOGA présente le Zaubergarten « für Kinder ab 6 Jahren »
AGE_ZAUBERGARTEN = "ab 6 Jahren"
RE_HEURES = re.compile(r"(\d{1,2}):(\d{2})\s*[−–-]\s*(\d{1,2}):(\d{2})")


def lire_agenda(page_html):
    """Renvoie les dates pour enfants : dicts {debut, fin, rubrique, titre, url}."""
    soupe = BeautifulSoup(page_html, "html.parser")
    dates = []
    for carte in soupe.select("a.mdl-teaser_element__link[href]"):
        rubrique = carte.select_one(".mdl-teaser_element__topic")
        rubrique = rubrique.get_text(" ", strip=True) if rubrique else ""
        if not any(r in rubrique.lower() for r in RUBRIQUES_ENFANTS):
            continue
        debut_attr = carte.find(attrs={"itemprop": "startDate"})
        titre = carte.find(attrs={"itemprop": "name"})
        if not debut_attr or not titre:
            continue
        debut = datetime.fromisoformat(debut_attr["content"][:16])
        h = RE_HEURES.search(carte.get_text(" ", strip=True))
        fin = debut.replace(hour=int(h.group(3)), minute=int(h.group(4))) if h else None
        dates.append({
            "debut": debut,
            "fin": fin,
            "rubrique": rubrique,
            "titre": titre.get_text(" ", strip=True),
            "url": carte["href"],
        })
    return dates


def lire_fiche(page_html):
    """Renvoie (texte, inscription, gratuit) depuis la fiche d'une date."""
    soupe = BeautifulSoup(page_html, "html.parser")
    principal = soupe.find("main") or soupe
    paragraphes = [p.get_text(" ", strip=True) for p in principal.find_all("p")]
    texte = next((p for p in paragraphes if len(p) > 60 and "Uhr" not in p[:40]), "")
    page = principal.get_text(" ", strip=True).lower()
    return raccourcir(texte), "anmeld" in page, ("kostenlos" in page or "gratis" in page)


def lire(source):
    """Point d'entrée appelé par recuperer.py."""
    dates = lire_agenda(telecharger(AGENDA).text)
    fiches = {d["url"]: lire_fiche(telecharger(d["url"]).text) for d in dates}
    evenements = []
    for d in dates:
        texte, inscription, gratuit = fiches[d["url"]]
        zaubergarten = "zaubergarten" in d["rubrique"].lower()
        evenements.append(Evenement(
            id=f"boga-{d['url'].rstrip('/').split('/')[-2][:40]}-{d['debut']:%Y%m%d%H%M}",
            titre=f"Zaubergarten – {d['titre']}" if zaubergarten else d["titre"],
            description_courte=texte,
            debut=d["debut"].strftime("%Y-%m-%dT%H:%M"),
            fin=d["fin"].strftime("%Y-%m-%dT%H:%M") if d["fin"] else None,
            lieu_nom="Botanischer Garten Bern",
            adresse=ADRESSE,
            age_texte=AGE_ZAUBERGARTEN if zaubergarten else "",
            prix="gratuit" if gratuit else "inconnu",
            inscription_requise=inscription,
            categorie="nature",
            source="Botanischer Garten Bern",
            url_source=d["url"],
        ))
    return evenements
