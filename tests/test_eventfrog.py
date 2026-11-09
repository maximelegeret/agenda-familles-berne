"""Tests du lecteur Eventfrog, sur des réponses de l'API enregistrées le 9 nov. 2026."""

import json
from pathlib import Path

import pytest

from agenda.lecteurs import eventfrog
from agenda.lecteurs.eventfrog import heure_de_berne, lire_evenements, lire_lieux, texte_langue

PAGES = Path(__file__).parent / "pages" / "eventfrog"


def donnees(nom):
    return json.loads((PAGES / nom).read_text(encoding="utf-8"))


def evenements():
    return lire_evenements(donnees("evenements.json"), lire_lieux(donnees("lieux.json")), ["CityQuest"])


def test_lieux():
    lieux = lire_lieux(donnees("lieux.json"))
    matte = lieux["24993"]
    assert matte["nom"] == "Theater Matte"
    assert matte["adresse"] == "Mattenenge 1, 3011 Bern"
    assert round(matte["lat"], 3) == 46.949


def test_cityquest_ecarte():
    assert not any("Otter" in e.titre or "ARBIE" in e.titre for e in evenements())


def test_spectacle_theater_matte():
    pica = next(e for e in evenements() if e.titre == "Pica & Poco")
    assert pica.debut == "2026-11-14T14:00"
    assert pica.lieu_nom == "Theater Matte"
    assert pica.adresse == "Mattenenge 1, 3011 Bern"
    assert pica.age_min == 3  # « für alle Menschen ab 3 Jahren »
    assert pica.prix == "inconnu"  # simple annonce, sans billetterie Eventfrog
    assert pica.url_source.startswith("https://eventfrog.")
    assert pica.source == "Eventfrog"


def test_categorie():
    titres = {e.titre: e.categorie for e in evenements()}
    assert titres["Märli mit Martin: Das Waldhaus & Hans im Glück"] == "conte"  # mot-clé « Märli »
    assert titres["Triplette: «Ei Ei Ei»"] == "spectacle"  # rien dans le texte : rubrique Kindertheater


def test_prix_et_heures():
    lachyoga = next(e for e in evenements() if e.titre.startswith("Lachyoga"))
    assert lachyoga.prix == "gratuit"
    assert (lachyoga.debut, lachyoga.fin) == ("2026-11-11T15:00", "2026-11-11T16:00")
    maerchen = next(e for e in evenements() if e.titre.startswith("Drei Frauen"))
    assert maerchen.prix == "dès 10 CHF"


def test_outils():
    assert texte_langue({"de": None, "en": None, "fr": "Bonjour"}) == "Bonjour"
    # Une heure d'été UTC+2 reste l'heure de Berne
    assert heure_de_berne("2026-07-01T08:00:00Z") == "2026-07-01T10:00"


def test_jeton_absent(monkeypatch):
    monkeypatch.delenv("EVENTFROG_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="EVENTFROG_TOKEN"):
        eventfrog.lire({})
