"""
Lecteur du Yehudi Menuhin Forum (salle de concert, Helvetiaplatz).

La page « Konzertkalender » (extension WordPress EventON) contient tous les concerts à venir.
Chaque concert y porte :
- data-time : début et fin en secondes depuis 1970 (heure universelle) ;
- un titre et un sous-titre (ex. « Peter und der Wolf » / « Familienkonzert ») ;
- une description complète (données schema.org), où l'on trouve le prix.

L'agenda est généraliste : on ne garde que les concerts dont le titre ou le sous-titre
parle de famille ou d'enfants. Une seule page à lire, pas de fiche détaillée.
"""

import json
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

from agenda.modele import Evenement
from agenda.textes import lire_prix, raccourcir
from agenda.web import telecharger

CALENDRIER = "https://menuhinforum.ch/konzertkalender/"
FUSEAU = ZoneInfo("Europe/Zurich")
# Mots cherchés dans le titre et le sous-titre seulement (la description parle parfois
# de « Kinderhilfswerk » ou de « Jugend musiziert » pour des concerts tout public)
MOTS_FAMILLE = ("familie", "kinder", "kids", "famille", "enfants")
# Au-delà, l'heure de fin n'est pas fiable (EventON met souvent 23:50 par défaut)
DUREE_MAX_HEURES = 5
RE_PRIX = re.compile(r"(eintritt[^.]{0,60}|kollekte[^.]{0,30}|chf\s*\d+[^.]{0,30})", re.IGNORECASE)


def _heure_locale(secondes):
    """Secondes depuis 1970 (UTC) -> datetime à l'heure de Berne."""
    return datetime.fromtimestamp(int(secondes), timezone.utc).astimezone(FUSEAU)


def analyser_calendrier(page_html):
    """Lit la page du calendrier et renvoie les concerts famille."""
    soupe = BeautifulSoup(page_html, "html.parser")
    evenements = []
    for bloc in soupe.select(".eventon_list_event[data-time]"):
        titre = bloc.select_one(".evcal_event_title")
        sous_titre = bloc.select_one(".evcal_event_subtitle")
        titre = titre.get_text(" ", strip=True) if titre else ""
        sous_titre = sous_titre.get_text(" ", strip=True) if sous_titre else ""
        if not any(mot in f"{titre} {sous_titre}".lower() for mot in MOTS_FAMILLE):
            continue

        debut_s, fin_s = bloc["data-time"].split("-")
        debut, fin = _heure_locale(debut_s), _heure_locale(fin_s)
        if (fin - debut).total_seconds() > DUREE_MAX_HEURES * 3600:
            fin = None

        # Description complète et lien, dans les données schema.org du bloc
        description, chapeau, url = "", "", CALENDRIER
        donnees = bloc.find("script", type="application/ld+json")
        if donnees and donnees.string:
            infos = json.loads(donnees.string, strict=False)
            contenu = BeautifulSoup(infos.get("description", ""), "html.parser")
            description = contenu.get_text(" ", strip=True)
            # Le chapeau : premier intertitre h3 (ex. « Sergei Prokofiews Musikmärchen mit … »)
            premier_h3 = contenu.find("h3")
            chapeau = premier_h3.get_text(" ", strip=True) if premier_h3 else ""
            # « …/peter-und-der-wolf/var/ri-0.l-L2 » -> « …/peter-und-der-wolf/ »
            url = re.sub(r"var/.*$", "", infos.get("url", CALENDRIER))
        trouve = RE_PRIX.search(description)

        # Résumé : le chapeau s'il existe, sinon le début de la description (sans le sous-titre répété)
        resume = chapeau or (description[len(sous_titre):].strip() if description.startswith(sous_titre) else description)
        evenements.append(Evenement(
            id=f"menuhin-{bloc.get('data-event_id')}-{debut:%Y%m%d%H%M}",
            titre=titre,
            description_courte=raccourcir(f"{sous_titre} – {resume}" if sous_titre else resume),
            debut=debut.strftime("%Y-%m-%dT%H:%M"),
            fin=fin.strftime("%Y-%m-%dT%H:%M") if fin else None,
            lieu_nom="Yehudi Menuhin Forum",
            adresse="Helvetiaplatz 6, 3005 Bern",
            prix=lire_prix(trouve.group(1)) if trouve else "inconnu",
            categorie="musique",
            source="Yehudi Menuhin Forum",
            url_source=url,
        ))
    return evenements


def lire(source):
    """Point d'entrée appelé par recuperer.py."""
    return analyser_calendrier(telecharger(CALENDRIER).text)
