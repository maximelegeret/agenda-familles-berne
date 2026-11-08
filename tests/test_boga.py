"""Tests du lecteur Botanischer Garten Bern, sur des pages enregistrées le 8 nov. 2026."""

from datetime import datetime
from pathlib import Path

from agenda.lecteurs.boga import lire_agenda, lire_fiche

PAGES = Path(__file__).parent / "pages" / "boga"


def page(nom):
    return (PAGES / nom).read_text(encoding="utf-8")


def test_agenda_enfants_seulement():
    dates = lire_agenda(page("agenda.html"))
    rubriques = {d["rubrique"] for d in dates}
    assert rubriques == {"Zaubergarten (Kinderfreizeit)", "Thementage"}   # pas de visites pour adultes
    zaubergarten = dates[0]
    assert zaubergarten["titre"] == "Von Schamanenzauber und Göttertrank"
    assert (zaubergarten["debut"], zaubergarten["fin"]) == (datetime(2026, 11, 25, 14, 0), datetime(2026, 11, 25, 16, 0))


def test_fiche():
    texte, inscription, gratuit = lire_fiche(page("zaubergarten.html"))
    assert texte.startswith("Unser Zauberjahr neigt sich langsam dem Ende zu")
    assert inscription is True
    assert gratuit is False   # « kostenpflichtig » : payant, montant non indiqué
