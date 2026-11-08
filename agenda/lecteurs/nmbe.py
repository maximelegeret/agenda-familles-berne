"""
Lecteur du Naturhistorisches Museum Bern (Bernastrasse 15).

1. Le calendrier accepte le filtre de public « Familien und Kinder » dans l'adresse
   (audience[36]=36) et se lit page par page (&page=1, 2…).
   Chaque carte donne le jour (« 25.11 »), les heures (« 14:00 — 16:00 ») et le titre.
   Attention : l'attribut datetime finit par « Z » mais contient l'heure de Berne ;
   on prend la date de l'attribut et les heures du texte affiché.
2. La fiche (lue une fois par activité) a une liste « Weitere Informationen » :
   Alter, Kosten, Treffpunkt, Anmeldung, et un texte de présentation.
"""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from agenda.modele import Evenement
from agenda.textes import lire_inscription, lire_prix, raccourcir
from agenda.web import telecharger

SITE = "https://www.nmbe.ch"
CALENDRIER = SITE + "/de/kalender"
FILTRE = {"audience[36]": 36}   # « Familien und Kinder » (relevé le 8 nov. 2026)
PAGES_MAX = 5
ADRESSE = "Bernastrasse 15, 3005 Bern"
RE_HEURES = re.compile(r"(\d{1,2}):(\d{2})\s*(?:—|-|–)\s*(\d{1,2}):(\d{2})")


def lire_calendrier(page_html):
    """Renvoie la liste des séances : dicts {debut, fin, titre, url}."""
    soupe = BeautifulSoup(page_html, "html.parser")
    seances = []
    for carte in soupe.select("article.article--event"):
        lien = carte.select_one("a[href]")
        titre = carte.select_one(".article__title")
        if not lien or not titre:
            continue
        for creneau in carte.select(".event-happening-date-times__time"):
            temps = creneau.find("time")
            h = RE_HEURES.search(creneau.get_text(" ", strip=True))
            if not temps or not temps.get("datetime") or not h:
                continue
            jour = temps["datetime"][:10]  # AAAA-MM-JJ
            seances.append({
                "debut": f"{jour}T{int(h.group(1)):02d}:{h.group(2)}",
                "fin": f"{jour}T{int(h.group(3)):02d}:{h.group(4)}",
                "titre": titre.get_text(" ", strip=True),
                "url": urljoin(SITE, lien["href"]),
            })
    return seances


def lire_fiche(page_html):
    """Infos de la fiche : {"Alter": …, "Kosten": …, "Anmeldung": …, "texte": …}."""
    soupe = BeautifulSoup(page_html, "html.parser")
    infos = {}
    for terme in soupe.select("dt.definition-list__term"):
        definition = terme.find_next_sibling("dd")
        if definition:
            infos[terme.get_text(" ", strip=True)] = definition.get_text(" ", strip=True)
    principal = soupe.find("main") or soupe
    paragraphes = [p.get_text(" ", strip=True) for p in principal.find_all("p")]
    infos["texte"] = raccourcir(next((p for p in paragraphes if len(p) > 50 and "NMBE/" not in p), ""))
    return infos


def lire(source):
    """Point d'entrée appelé par recuperer.py."""
    seances, vues = [], set()
    for numero in range(PAGES_MAX):
        params = dict(FILTRE, page=numero) if numero else FILTRE
        nouvelles = [s for s in lire_calendrier(telecharger(CALENDRIER, params=params).text)
                     if (s["url"], s["debut"]) not in vues]
        if not nouvelles:
            break
        vues.update((s["url"], s["debut"]) for s in nouvelles)
        seances += nouvelles

    fiches = {url: lire_fiche(telecharger(url).text) for url in {s["url"] for s in seances}}
    evenements = []
    for s in seances:
        infos = fiches[s["url"]]
        evenements.append(Evenement(
            id=f"nmbe-{s['url'].rsplit('/', 1)[-1][:40]}-{s['debut'].replace('-', '').replace(':', '').replace('T', '')}",
            titre=s["titre"],
            description_courte=infos.get("texte", ""),
            debut=s["debut"],
            fin=s["fin"],
            lieu_nom="Naturhistorisches Museum Bern",
            adresse=ADRESSE,
            age_texte=infos.get("Alter", ""),
            prix=lire_prix(infos.get("Kosten")),
            # La valeur seule (« obligatorisch ») ne contient pas le mot « Anmeldung » : on le rajoute
            inscription_requise=lire_inscription(f"Anmeldung {infos['Anmeldung']}") if infos.get("Anmeldung") else None,
            source="Naturhistorisches Museum Bern",
            url_source=s["url"],
        ))
    return evenements
