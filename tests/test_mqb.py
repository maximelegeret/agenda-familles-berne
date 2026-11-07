"""
Tests du lecteur MuseumsQuartier, sur des pages enregistrées le 7 nov. 2026 (tests/pages/mqb).
"""

from pathlib import Path

from agenda.lecteurs.mqb import analyser_fiche, liens_evenements
from agenda.textes import lire_prix

PAGES = Path(__file__).parent / "pages" / "mqb"
URL = "https://www.mqb.ch/en/agenda/tiergeschichten-aus-dem-naturlabor"


def lire_page(nom):
    return (PAGES / nom).read_text(encoding="utf-8")


def test_liens_sans_doublon():
    # La page liste deux dates du même événement : une seule fiche à lire
    assert liens_evenements(lire_page("agenda-enfants.html")) == [URL]


def test_fiche_toutes_les_seances():
    evts = analyser_fiche(lire_page("tiergeschichten.html"), URL)
    assert [(e.debut, e.fin) for e in evts] == [
        ("2026-11-29T11:00", "2026-11-29T11:40"),
        ("2026-11-29T13:30", "2026-11-29T14:10"),
        ("2026-12-26T14:00", "2026-12-26T14:40"),
        ("2026-12-26T15:30", "2026-12-26T16:10"),
    ]


def test_fiche_details():
    e = analyser_fiche(lire_page("tiergeschichten.html"), URL)[0]
    assert e.titre == "Tiergeschichten aus dem Naturlabor"
    assert e.lieu_nom == "The Natural History Museum of Bern"
    assert e.prix == "entrée + 5 CHF"
    assert e.inscription_requise is False          # « Keine Anmeldung möglich »
    assert e.description_courte.startswith("Was für ein Theater")


def test_prix_supplement():
    assert lire_prix("Regulärer Eintritt plus Ticket zu CHF 5.- pro Person") == "entrée + 5 CHF"
