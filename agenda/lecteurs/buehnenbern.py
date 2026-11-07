"""
Lecteur de Bühnen Bern (Stadttheater, Vidmar, Berner Symphonieorchester…).

Comment ça marche :
1. Le programme (buehnenbern.ch/spielplan/programm/) liste 20 représentations par page,
   par ordre de date. On lit deux listes jusqu'à dépasser 15 jours :
   - avec le filtre « Junges Publikum » (paramètre filter3 dans l'adresse) ;
   - sans filtre, pour attraper les visites et ateliers « Vermittlung » pour enfants.
2. On écarte les « Schulvorstellung » (réservées aux classes).
3. Pour chaque spectacle retenu, la fiche détaillée donne l'âge (ex. « 4+ », « 14+ »)
   et un texte de présentation. Le tri général écarte ensuite ce qui vise plus de 10 ans.
"""

import re
from datetime import datetime, timedelta
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from agenda.modele import Evenement
from agenda.textes import lire_prix, raccourcir
from agenda.web import telecharger

SITE = "https://buehnenbern.ch"
PROGRAMME = SITE + "/spielplan/programm/"
FILTRE_JEUNE_PUBLIC = {"filter3": "7370|7074|7352"}  # « Junges Publikum » (relevé le 7 nov. 2026)
NB_JOURS = 15
PAGES_MAX = 6  # garde-fou

# Indices qu'une représentation de la liste générale vise les enfants
RE_ENFANTS = re.compile(r"kinder|familie|ab \d+ jahren", re.IGNORECASE)

# Rubrique du site -> catégorie de l'agenda (les autres sont devinées par mots-clés)
CATEGORIES = {
    "Schauspiel": "spectacle", "Tanz": "spectacle", "Oper": "spectacle",
    "Berner Symphonieorchester": "musique", "Kammermusik": "musique",
}


def _texte(element, selecteur):
    trouve = element.select_one(selecteur)
    return trouve.get_text(" ", strip=True) if trouve else ""


def lire_cartes(page_html):
    """Lit une page du programme : liste de dicts (date, heure, rubrique, titre, infos, prix, lieu, lien)."""
    soupe = BeautifulSoup(page_html, "html.parser")
    cartes = []
    for item in soupe.select(".cp-calendar-item"):
        lien = item.select_one("a.link-box[href]")
        date = _texte(item, ".date")
        if not lien or not re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", date):
            continue
        cartes.append({
            "date": datetime.strptime(date, "%d.%m.%Y"),
            "heure": _texte(item, ".time"),
            "rubrique": _texte(item, ".division"),
            "titre": _texte(item, ".play-name"),
            "infos": _texte(item, ".info-text"),
            "prix": _texte(item, ".prize"),
            "lieu": _texte(item, ".location"),
            "url": urljoin(SITE, lien["href"]),
        })
    return cartes


def lire_fiche(page_html):
    """Fiche d'un spectacle : renvoie (âge tel qu'écrit, ex. « 4+ », texte de présentation)."""
    soupe = BeautifulSoup(page_html, "html.parser")
    barre = _texte(soupe, ".icon-bar")
    age = re.search(r"\b(\d{1,2})\s*\+", barre)
    # Dans .intro : titre, sous-titre, puis le texte ; on prend le premier paragraphe assez long
    paragraphes = [p.get_text(" ", strip=True) for p in soupe.select(".intro p")]
    description = next((p for p in paragraphes if len(p) > 60), "")
    return (f"{age.group(1)}+" if age else ""), raccourcir(description)


def _cartes_dans_la_fenetre(params, limite):
    """Lit les pages du programme (avec ou sans filtre) jusqu'à dépasser la date limite."""
    cartes = []
    for numero in range(1, PAGES_MAX + 1):
        url = PROGRAMME if numero == 1 else f"{PROGRAMME}page{numero}"
        page = lire_cartes(telecharger(url, params=params).text)
        cartes += [c for c in page if c["date"] <= limite]
        if not page or page[-1]["date"] > limite:
            break
    return cartes


def lire(source):
    """Point d'entrée appelé par recuperer.py."""
    limite = datetime.now() + timedelta(days=NB_JOURS)
    jeune_public = _cartes_dans_la_fenetre(FILTRE_JEUNE_PUBLIC, limite)
    generales = [c for c in _cartes_dans_la_fenetre(None, limite)
                 if RE_ENFANTS.search(f"{c['titre']} {c['infos']}")]

    # Fusion des deux listes, sans doublon ni représentation scolaire
    cartes, vues = [], set()
    for c in jeune_public + generales:
        cle = (c["url"], c["date"], c["heure"])
        if cle in vues or "schulvorstellung" in c["infos"].lower():
            continue
        vues.add(cle)
        cartes.append(c)

    # Une seule lecture de fiche par spectacle
    fiches = {url: lire_fiche(telecharger(url).text) for url in {c["url"] for c in cartes}}
    return [carte_en_evenement(c, *fiches[c["url"]]) for c in cartes]


def carte_en_evenement(carte, age_fiche, description):
    """Transforme une carte du programme (et les infos de sa fiche) en Evenement."""
    heure = carte["heure"] if re.fullmatch(r"\d{1,2}:\d{2}", carte["heure"]) else "00:00"
    h, m = heure.split(":")
    debut = carte["date"].replace(hour=int(h), minute=int(m))
    # L'âge de la carte (« Ab 5 Jahren ») est plus précis que celui de la fiche (« 5+ »)
    age_texte = carte["infos"] if re.search(r"jahr", carte["infos"], re.IGNORECASE) else age_fiche
    return Evenement(
        id=f"buehnenbern-{carte['url'].rstrip('/').rsplit('/', 1)[-1]}-{debut:%Y%m%d%H%M}",
        titre=carte["titre"],
        description_courte=description,
        debut=debut.strftime("%Y-%m-%dT%H:%M"),
        lieu_nom=carte["lieu"] or "Bühnen Bern",
        age_texte=age_texte,
        prix=lire_prix(carte["prix"]),
        categorie=CATEGORIES.get(carte["rubrique"]),
        source="Bühnen Bern",
        url_source=carte["url"],
    )
