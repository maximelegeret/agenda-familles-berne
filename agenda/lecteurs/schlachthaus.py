"""
Lecteur du Schlachthaus Theater Bern (Rathausgasse 20/22).

La liste du programme (/de/programm/shows/) contient une carte par représentation :
  date « So 08.11. » · titre · détails « Saal / 15:00 / Ab 6 Jahren / … » · étiquettes
  (« Schulvorstellung », « mit Munterbunt », « Ausverkauft »…).
On garde les représentations qui indiquent un âge de 10 ans au plus (ou qui parlent
d'enfants), sauf les séances scolaires. La fiche de chaque spectacle (lue une fois)
donne le prix (« 5-33 CHF ») et le texte de présentation.
"""

import re
from datetime import date, datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from agenda.filtre_enfants import AGE_MAX_VISE, extraire_age
from agenda.modele import Evenement
from agenda.textes import lire_prix, raccourcir
from agenda.web import telecharger

SITE = "https://www.schlachthaus.ch"
PROGRAMME = SITE + "/de/programm/shows/"
ADRESSE = "Rathausgasse 20/22, 3011 Bern"
RE_DATE = re.compile(r"(\d{1,2})\.(\d{1,2})\.")
RE_HEURE = re.compile(r"^(\d{1,2}):(\d{2})$")
RE_PRIX = re.compile(r"(\d+\s*-\s*\d+|\d+)\s*CHF")


def annee_probable(jour, mois, aujourd_hui):
    """Les dates n'ont pas d'année : un mois déjà passé de plus de 2 mois = l'an prochain."""
    annee = aujourd_hui.year
    if (aujourd_hui.month - mois) > 2:
        annee += 1
    return annee


def lire_programme(page_html, aujourd_hui=None):
    """Renvoie la liste des représentations pour enfants : dicts {debut, titre, salle, age, url, fiche}."""
    aujourd_hui = aujourd_hui or date.today()
    soupe = BeautifulSoup(page_html, "html.parser")
    resultats = []
    for carte in soupe.select("article.show"):
        lien = carte.find("a", href=True)
        d = RE_DATE.search(carte.select_one(".date").get_text(" ", strip=True)) if carte.select_one(".date") else None
        if not lien or not d:
            continue
        etiquettes = [li.get_text(" ", strip=True) for li in carte.select(".pills li")]
        if any("schulvorstellung" in e.lower() for e in etiquettes):
            continue  # réservé aux classes
        # Détails séparés par des <br> : salle, heure, âge, accessibilité…
        details = carte.select_one(".details")
        lignes = [t.strip() for t in details.find_all(string=True, recursive=False) if t.strip()] if details else []
        heure = next((RE_HEURE.match(l) for l in lignes if RE_HEURE.match(l)), None)
        age = next((l for l in lignes if "jahr" in l.lower()), "")
        titre_bloc = carte.select_one(".title h4")
        surtitre = titre_bloc.select_one(".supertitle") if titre_bloc else None
        nom_compagnie = surtitre.get_text(" ", strip=True) if surtitre else ""
        if surtitre:
            surtitre.extract()
        titre = titre_bloc.get_text(" ", strip=True) if titre_bloc else ""

        age_min, _ = extraire_age(age)
        pour_enfants = (age_min is not None and age_min <= AGE_MAX_VISE) or re.search(r"kinder|familie", titre, re.I)
        if not pour_enfants or not heure:
            continue
        jour, mois = int(d.group(1)), int(d.group(2))
        resultats.append({
            "debut": datetime(annee_probable(jour, mois, aujourd_hui), mois, jour, int(heure.group(1)), int(heure.group(2))),
            "titre": f"{titre} ({nom_compagnie})" if nom_compagnie else titre,
            "salle": lignes[0] if lignes and not RE_HEURE.match(lignes[0]) and "schlachthaus" not in lignes[0].lower() else "",
            "age": age,
            "url": urljoin(SITE, lien["href"]),
            "fiche": urljoin(SITE, lien["href"].split("?")[0]),  # une fiche par spectacle
        })
    return resultats


def lire_fiche(page_html):
    """Renvoie (prix, texte de présentation) depuis la fiche d'un spectacle."""
    soupe = BeautifulSoup(page_html, "html.parser")
    for t in soupe(["script", "style", "nav", "header", "footer"]):
        t.decompose()
    texte = re.sub(r"\s+", " ", soupe.get_text(" ", strip=True))
    prix = RE_PRIX.search(texte)
    paragraphes = [p.get_text(" ", strip=True) for p in soupe.find_all("p")]
    # Le premier paragraphe est parfois le bloc d'infos (« Saal Ab 6 Jahren Objekttheater… ») : on le saute
    description = next((p for p in paragraphes if len(p) > 80 and not re.search(r"Ab \d+ Jahren", p[:60])), "")
    return (lire_prix(prix.group(0)) if prix else "inconnu"), raccourcir(description)


def lire(source):
    """Point d'entrée appelé par recuperer.py."""
    seances = lire_programme(telecharger(PROGRAMME).text)
    fiches = {url: lire_fiche(telecharger(url).text) for url in {s["fiche"] for s in seances}}
    evenements = []
    for s in seances:
        prix, texte = fiches[s["fiche"]]
        evenements.append(Evenement(
            id=f"schlachthaus-{s['url'].rsplit('=', 1)[-1]}-{s['debut']:%Y%m%d%H%M}",
            titre=s["titre"],
            description_courte=texte,
            debut=s["debut"].strftime("%Y-%m-%dT%H:%M"),
            lieu_nom=f"Schlachthaus Theater – {s['salle']}" if s["salle"] else "Schlachthaus Theater",
            adresse=ADRESSE,
            age_texte=s["age"],
            prix=prix,
            categorie="spectacle",
            source="Schlachthaus Theater",
            url_source=s["url"],
        ))
    return evenements
