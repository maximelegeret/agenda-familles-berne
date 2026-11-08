"""
Lecteur du MüZe Muri-Gümligen (Familien- und Weiterbildungszentrum, Thoracherhus).

La page « Veranstaltungen » liste toutes les dates, groupées par mois :
  <div class="event"><time datetime="2026-11-11T14:00:00">…</time>
     <a href="…">KREALINO – Kinderbasteln</a> <div class="date">14:00 Uhr bis 16:00 Uhr</div></div>
Le centre propose aussi des rendez-vous pour parents (consultation, allaitement)
ou pour tous (Repair-Café) : on les écarte. Pour les activités gardées des
15 prochains jours, la fiche donne le texte, le prix et l'inscription.
Le Pünktli (salle de jeux 0–5 ans) n'a pas de dates : il est dans offres_regulieres.yaml.
"""

import re
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from agenda.modele import Evenement
from agenda.textes import lire_prix, raccourcir
from agenda.web import telecharger

LISTE = "https://www.mueze-muri-guemligen.ch/angebot/veranstaltungen/"
LIEU = "MüZe Muri-Gümligen (Thoracherhus)"
ADRESSE = "Kranichweg 10, 3074 Muri bei Bern"
NB_JOURS = 15

# Rendez-vous qui ne sont pas des activités pour enfants
MOTS_EXCLUS = ("beratung", "stilltreffen", "repair", "elterncafe", "coiffeur", "ferien", "zmittag", "geschlossen")
RE_FIN = re.compile(r"bis\s*(\d{1,2}):(\d{2})")
RE_PRIX_NON_MEMBRE = re.compile(r"Nichtmitglieder:\s*(CHF\s*[\d.,]+|gratis|kostenlos)", re.I)


def lire_liste(page_html):
    """Renvoie les activités pour enfants : dicts {debut, fin, titre, url, complet}."""
    soupe = BeautifulSoup(page_html, "html.parser")
    activites = []
    for bloc in soupe.select(".event--container .event"):
        temps = bloc.find("time")
        lien = bloc.select_one(".event__details a[href]")
        if not temps or not lien or not temps.get("datetime"):
            continue
        titre = lien.get_text(" ", strip=True)
        if any(mot in titre.lower() for mot in MOTS_EXCLUS):
            continue
        debut = datetime.fromisoformat(temps["datetime"][:16])
        fin_match = RE_FIN.search(bloc.select_one(".date").get_text(" ", strip=True)) if bloc.select_one(".date") else None
        fin = debut.replace(hour=int(fin_match.group(1)), minute=int(fin_match.group(2))) if fin_match else None
        activites.append({
            "debut": debut,
            "fin": fin,
            "titre": titre,
            "url": lien["href"],
            # Pastille du calendrier marquée « booked » : complet
            "complet": "booked" in (bloc.select_one(".calendar-icon").get("class", []) if bloc.select_one(".calendar-icon") else []),
        })
    return activites


def lire_fiche(page_html):
    """Renvoie (texte, prix, inscription) depuis la fiche d'une activité."""
    soupe = BeautifulSoup(page_html, "html.parser")
    titre = soupe.find("h1")
    paragraphe = titre.find_next("p") if titre else None
    texte = paragraphe.get_text(" ", strip=True) if paragraphe else ""
    page = re.sub(r"\s+", " ", soupe.get_text(" ", strip=True))
    prix = RE_PRIX_NON_MEMBRE.search(page)
    # La fiche contient un formulaire « Anmeldung » quand il faut s'inscrire
    inscription = bool(soupe.find(string=re.compile(r"^\s*Anmeldung\s*$")))
    return raccourcir(texte), (lire_prix(prix.group(1)) if prix else "inconnu"), inscription


def lire(source):
    """Point d'entrée appelé par recuperer.py."""
    limite = datetime.now() + timedelta(days=NB_JOURS)
    activites = [a for a in lire_liste(telecharger(LISTE).text) if a["debut"] <= limite]
    fiches = {url: lire_fiche(telecharger(url).text) for url in {a["url"] for a in activites}}
    evenements = []
    for a in activites:
        texte, prix, inscription = fiches[a["url"]]
        if a["complet"]:
            texte = f"Ausgebucht. {texte}".strip()
        evenements.append(Evenement(
            id=f"mueze-{a['url'].rstrip('/').rsplit('/', 1)[-1][:50]}-{a['debut']:%H%M}",
            titre=a["titre"],
            description_courte=texte,
            debut=a["debut"].strftime("%Y-%m-%dT%H:%M"),
            fin=a["fin"].strftime("%Y-%m-%dT%H:%M") if a["fin"] else None,
            lieu_nom=LIEU,
            adresse=ADRESSE,
            prix=prix,
            inscription_requise=inscription,
            source="MüZe Muri-Gümligen",
            url_source=a["url"],
        ))
    return evenements
