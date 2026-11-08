"""Tests du lecteur Dampfzentrale, sur des pages enregistrées le 8 nov. 2026."""

from datetime import datetime
from pathlib import Path

from agenda.filtre_enfants import completer, trier
from agenda.lecteurs.dampfzentrale import lire_fiche, lire_programme
from agenda.modele import Evenement

PAGES = Path(__file__).parent / "pages" / "dampfzentrale"


def page(nom):
    return (PAGES / nom).read_text(encoding="utf-8")


def test_programme_sans_doublon():
    dates = lire_programme(page("accueil.html"))
    discochugle = next(d for d in dates if d["titre"] == "Unger dr Discochugle")
    assert discochugle["debut"] == datetime(2026, 11, 8, 11, 0)
    # « Wild Card » du 8.11 à 13:30 est listé deux fois sur le site : gardé une fois
    assert len([d for d in dates if d["titre"].startswith("Wild Card") and d["debut"] == datetime(2026, 11, 8, 13, 30)]) == 1


def test_fiche_enfants():
    fiche = lire_fiche(page("discochugle.html"))
    assert fiche["rubrique"] == "Junges Publikum"
    assert fiche["prix"] == "10 CHF"
    assert fiche["age"] == "zwischen 5 und 10 Jahren"
    assert fiche["texte"].startswith("Zusammen Geschichten lauschen")


def test_autres_rubriques_et_ados():
    assert lire_fiche(page("lazy-club.html"))["rubrique"] == "Listening"   # pas pour enfants
    zentrale = lire_fiche(page("die-zentrale.html"))
    assert zentrale["age"] == "von 13 bis 16 Jahren"
    e = completer(Evenement(id="z", titre="Die Zentrale", debut="2026-11-21T00:00", lieu_nom="DZ",
                            source="DZ", url_source="https://x", age_texte=zentrale["age"]))
    assert trier(e)[0] is False   # 13–16 ans : écarté par le tri général
