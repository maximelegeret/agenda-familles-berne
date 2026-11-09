"""
Lecteur Eventfrog (API publique, api.eventfrog.net).

1. Le jeton (« Public API-Key », créé par Maxime dans son compte Eventfrog) est lu dans la
   variable d'environnement EVENTFROG_TOKEN : fichier .env sur l'ordinateur, secret GitHub la nuit.
2. /public/v1/events : activités de la rubrique « Kinderveranstaltungen » (906, avec ses
   sous-rubriques) dans un rayon autour de Berne, sur les 14 prochains jours, page par page.
3. /public/v1/locations : nom, adresse et coordonnées des lieux de ces activités.

Conditions d'utilisation d'Eventfrog (CGU § 17, réponse du 9 nov. 2026) : contenus repris tels quels,
lien vers la page Eventfrog de chaque activité, mise à jour quotidienne, pas d'images,
données non transmises à des tiers. Limite : 30 requêtes par minute, 2000 par jour.
"""

import os
import re
import time
from datetime import datetime, timedelta
from html import unescape
from zoneinfo import ZoneInfo

import requests

from agenda.filtre_enfants import completer, extraire_age
from agenda.modele import Evenement
from agenda.textes import raccourcir
from agenda.web import ENTETES

API = "https://api.eventfrog.net/public/v1"
FUSEAU = ZoneInfo("Europe/Zurich")
BERNE = (46.948, 7.447)       # centre de Berne (Zytglogge)
PAR_PAGE = 100
PAGES_MAX = 10
PAUSE = 2.5                   # secondes entre deux requêtes (bien en dessous de 30 par minute)
# Sous-rubriques d'Eventfrog -> type d'activité, utilisé seulement si les mots-clés n'ont rien trouvé
CATEGORIE_PAR_RUBRIQUE = {
    51: "fête",        # Kinderfest
    52: "visite",      # Kinderführung
    54: "spectacle",   # Kindertheater
    55: "spectacle",   # Kinderzirkus
    56: "musique",     # Konzert
    57: "atelier",     # Kurs
    58: "spectacle",   # Puppentheater
}


def texte_langue(valeur):
    """{'de': …, 'fr': …, 'en': …} -> le texte allemand, sinon français, sinon anglais."""
    if isinstance(valeur, dict):
        return next((valeur[l] for l in ("de", "fr", "en") if valeur.get(l)), "")
    return valeur or ""


def sans_html(html):
    """« <p>Bonjour&nbsp;<b>toi</b></p> » -> « Bonjour toi »."""
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html or "")).split())


def heure_de_berne(texte):
    """« 2026-11-14T14:00:00+01:00 » -> « 2026-11-14T14:00 » (heure de Berne)."""
    if not texte:
        return None
    return datetime.fromisoformat(texte).astimezone(FUSEAU).strftime("%Y-%m-%dT%H:%M")


def lire_prix_eventfrog(e):
    """Prix : billetterie Eventfrog -> « gratuit » ou « dès 10 CHF » ; simple annonce -> inconnu."""
    prix = e.get("lowestTicketPrice")
    if e.get("agendaEntryOnly") or prix is None:
        return "inconnu"
    if prix == 0:
        return "gratuit"
    return f"dès {prix:g} CHF"


def lire_lieux(donnees):
    """Réponse de /locations -> {id: {"nom", "adresse", "lat", "lng"}}."""
    lieux = {}
    for l in donnees.get("locations", []):
        ville = " ".join(x for x in (l.get("zip"), l.get("city")) if x)
        lieux[str(l["id"])] = {
            "nom": texte_langue(l.get("title")),
            "adresse": ", ".join(x for x in (l.get("addressLine"), ville) if x),
            "lat": l.get("lat"),
            "lng": l.get("lng"),
        }
    return lieux


def est_exclu(e, organisateurs_exclus):
    """Vrai si l'activité est annulée, cachée, ou vient d'un organisateur écarté (ex. CityQuest)."""
    if e.get("cancelled") or e.get("visible") is False or e.get("published") is False:
        return True
    organisateur = (e.get("organizerName") or "").lower()
    return any(mot.lower() in organisateur for mot in organisateurs_exclus)


def lire_evenements(donnees, lieux, organisateurs_exclus=()):
    """Réponse de /events (+ lieux déjà lus) -> liste d'Evenement."""
    evenements = []
    for e in donnees.get("events", []):
        if est_exclu(e, organisateurs_exclus):
            continue
        lieu = next((lieux[i] for i in e.get("locationIds", []) if i in lieux), {})
        texte_complet = sans_html(texte_langue(e.get("descriptionAsHTML")))
        resume = texte_langue(e.get("shortDescription")) or texte_complet
        # L'âge est souvent plus loin dans le texte que les 200 caractères affichés
        age_min, age_max = extraire_age(f"{resume} {texte_complet}")
        evenement = Evenement(
            id=f"eventfrog-{e['id']}",
            titre=texte_langue(e.get("title")).strip(),
            description_courte=raccourcir(resume),
            debut=heure_de_berne(e["begin"]),
            fin=heure_de_berne(e.get("end")),
            lieu_nom=lieu.get("nom") or texte_langue(e.get("locationAlias")) or e.get("organizerName", ""),
            adresse=lieu.get("adresse", ""),
            latitude=lieu.get("lat"),
            longitude=lieu.get("lng"),
            age_min=age_min,
            age_max=age_max,
            age_source="fourni" if age_min is not None or age_max is not None else None,
            prix=lire_prix_eventfrog(e),
            source="Eventfrog",
            url_source=e["url"],   # exigé par Eventfrog : lien vers la page de l'activité
        )
        # Type d'activité : d'abord les mots-clés (comme les autres sources), sinon la rubrique Eventfrog
        completer(evenement)
        if evenement.categorie is None:
            evenement.categorie = CATEGORIE_PAR_RUBRIQUE.get(e.get("rubricId"))
        evenements.append(evenement)
    return evenements


def appeler(chemin, params, jeton):
    """Une requête à l'API, avec le jeton ; lève une erreur si l'API répond par une erreur."""
    entetes = dict(ENTETES, Authorization=f"Bearer {jeton}")
    reponse = requests.get(f"{API}/{chemin}", params=params, headers=entetes, timeout=30)
    reponse.raise_for_status()
    time.sleep(PAUSE)
    return reponse.json()


def lire(source):
    """Point d'entrée appelé par recuperer.py."""
    jeton = os.environ.get("EVENTFROG_TOKEN", "").strip()
    if not jeton:
        raise RuntimeError("jeton EVENTFROG_TOKEN absent (fichier .env en local, secret GitHub la nuit)")

    aujourd_hui = datetime.now(FUSEAU).date()
    params = {
        "rubId": source.get("rubriques", [906]),
        "lat": BERNE[0],
        "lng": BERNE[1],
        "r": source.get("rayon_km", 15),
        "from": aujourd_hui.isoformat(),
        "to": (aujourd_hui + timedelta(days=15)).isoformat(),
        "perPage": PAR_PAGE,
    }
    bruts = []
    for page in range(1, PAGES_MAX + 1):
        donnees = appeler("events", dict(params, page=page), jeton)
        bruts += donnees.get("events", [])
        if len(bruts) >= donnees.get("totalNumberOfResources", 0) or not donnees.get("events"):
            break

    # Les lieux, en une seule requête (on ne demande que ceux des activités gardées)
    exclus = source.get("organisateurs_exclus", [])
    ids = sorted({i for e in bruts if not est_exclu(e, exclus) for i in e.get("locationIds", [])})
    lieux = lire_lieux(appeler("locations", {"id": ids, "perPage": PAR_PAGE}, jeton)) if ids else {}
    return lire_evenements({"events": bruts}, lieux, exclus)
