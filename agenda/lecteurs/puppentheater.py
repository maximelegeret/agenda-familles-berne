"""
Lecteur du Berner Puppen Theater (Gerechtigkeitsgasse 31, vieille ville).

La page « Spielplan » liste toutes les séances, groupées par mois :
  <h2>November 2026</h2>
  <div class="appearance"> jour · « 8. » · « 11:00 Uhr » · titre + « Ab 5 Jahren » · lien </div>
Les spectacles pour enfants pointent vers /kinderprogramm/?act=… ; ceux du soir
(/abendprogramm/) sont pour adultes et sont ignorés.
Chaque spectacle a une fiche (lue une fois) dont on tire un court texte.
Les prix enfants/adultes sont écrits sur la page du programme.
"""

import re
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from agenda.modele import Evenement
from agenda.textes import raccourcir
from agenda.web import telecharger

SITE = "https://www.berner-puppentheater.ch"
SPIELPLAN = SITE + "/spielplan"
ADRESSE = "Gerechtigkeitsgasse 31, 3011 Bern"

MOIS = {
    "januar": 1, "februar": 2, "märz": 3, "april": 4, "mai": 5, "juni": 6,
    "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "dezember": 12,
}
# « Vorstellungen für Kinder: Kinder Fr. 18.– / Erwachsene Fr. 25.– »
RE_PRIX = re.compile(r"Kinder:\s*Kinder\s*Fr\.\s*(\d+).{0,30}?Erwachsene\s*Fr\.\s*(\d+)", re.S)


def lire_prix_enfants(texte):
    """Renvoie '18–25 CHF' (enfant–adulte) ou 'inconnu'."""
    m = RE_PRIX.search(texte)
    return f"{m.group(1)}–{m.group(2)} CHF" if m else "inconnu"


def lire_spielplan(page_html):
    """
    Lit la page du programme. Renvoie (séances, prix) où chaque séance est
    un dict {debut, titre, age, url} pour les spectacles enfants seulement.
    """
    soupe = BeautifulSoup(page_html, "html.parser")
    texte = re.sub(r"\s+", " ", soupe.get_text(" ", strip=True))
    seances = []
    for titre_mois in soupe.find_all("h2"):
        m = re.fullmatch(r"\s*([A-Za-zäÄ]+)\s+(\d{4})\s*", titre_mois.get_text())
        if not m or m.group(1).lower() not in MOIS:
            continue
        mois, annee = MOIS[m.group(1).lower()], int(m.group(2))
        bloc = titre_mois.find_next_sibling("div", class_="events")
        if not bloc:
            continue
        for seance in bloc.select(".appearance"):
            lien = seance.select_one(".title a[href]")
            if not lien or "/kinderprogramm" not in lien["href"]:
                continue  # programme du soir : pour adultes
            jour = re.search(r"\d+", seance.select_one(".dateDay").get_text())
            heure = re.search(r"(\d{1,2}):(\d{2})", seance.select_one(".time").get_text())
            if not jour or not heure:
                continue
            nom = lien.find("strong").get_text(" ", strip=True)
            # Ce qui suit le titre en gras : « Ab 5 Jahren »
            age = " ".join(t.strip() for t in lien.find_all(string=True, recursive=False) if t.strip())
            seances.append({
                "debut": datetime(annee, mois, int(jour.group()), int(heure.group(1)), int(heure.group(2))),
                "titre": nom,
                "age": age,
                "url": urljoin(SITE, lien["href"]),
            })
    return seances, lire_prix_enfants(texte)


def lire_fiche(page_html):
    """Texte de présentation d'un spectacle : premier paragraphe assez long."""
    soupe = BeautifulSoup(page_html, "html.parser")
    zone = soupe.select_one(".block.columnLeft") or soupe
    for p in zone.find_all("p"):
        texte = p.get_text(" ", strip=True)
        if len(texte) > 80 and not texte.startswith("Spieldaten"):
            return raccourcir(texte)
    return ""


def lire(source):
    """Point d'entrée appelé par recuperer.py."""
    seances, prix = lire_spielplan(telecharger(SPIELPLAN).text)
    textes = {url: lire_fiche(telecharger(url).text) for url in {s["url"] for s in seances}}
    return [
        Evenement(
            # ex. « puppentheater-act12-202611081100 »
            id=f"puppentheater-act{s['url'].rsplit('=', 1)[-1]}-{s['debut']:%Y%m%d%H%M}",
            titre=s["titre"],
            description_courte=textes.get(s["url"], ""),
            debut=s["debut"].strftime("%Y-%m-%dT%H:%M"),
            lieu_nom="Berner Puppen Theater",
            adresse=ADRESSE,
            age_texte=s["age"],
            prix=prix,
            categorie="spectacle",
            source="Berner Puppen Theater",
            url_source=s["url"],
        )
        for s in seances
    ]
