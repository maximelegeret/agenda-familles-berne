"""
Tests du lecteur Bühnen Bern, sur des pages enregistrées le 7 nov. 2026 (tests/pages/buehnenbern).
"""

from pathlib import Path

from agenda.filtre_enfants import completer, trier
from agenda.lecteurs.buehnenbern import carte_en_evenement, lire_cartes, lire_fiche
from agenda.textes import lire_prix

PAGES = Path(__file__).parent / "pages" / "buehnenbern"


def lire_page(nom):
    return (PAGES / nom).read_text(encoding="utf-8")


def test_cartes_du_programme():
    cartes = lire_cartes(lire_page("programme.html"))
    assert len(cartes) == 20
    fuehrung = cartes[0]
    assert fuehrung["titre"] == "Führung für Kinder und Familien"
    assert fuehrung["heure"] == "11:00"
    assert fuehrung["infos"] == "Ab 5 Jahren"
    assert fuehrung["url"] == "https://buehnenbern.ch/spielplan/programm/fuhrungen/58255"


def test_filtre_jeune_public_contient_les_ecoles():
    cartes = lire_cartes(lire_page("programme-jeune-public.html"))
    assert any("Schulvorstellung" in c["infos"] for c in cartes)  # à écarter par le lecteur


def test_age_de_la_fiche():
    assert lire_fiche(lire_page("regenbogenvogel.html"))[0] == "4+"
    assert lire_fiche(lire_page("kohlhaas.html"))[0] == "14+"


def test_tri_par_age():
    cartes = {c["titre"]: c for c in lire_cartes(lire_page("programme-jeune-public.html"))}
    regenbogen = completer(carte_en_evenement(cartes["Der letzte Regenbogenvogel"],
                                              *lire_fiche(lire_page("regenbogenvogel.html"))))
    kohlhaas = completer(carte_en_evenement(cartes["Kohlhaas"], *lire_fiche(lire_page("kohlhaas.html"))))
    assert regenbogen.age_min == 4 and trier(regenbogen)[0] is True
    assert kohlhaas.age_min == 14 and trier(kohlhaas)[0] is False


def test_age_de_la_carte_prioritaire():
    carte = lire_cartes(lire_page("programme.html"))[0]
    e = carte_en_evenement(carte, "5+", "")
    assert e.age_texte == "Ab 5 Jahren"
    assert e.prix == "5–8 CHF"


def test_fourchette_de_prix():
    assert lire_prix("CHF 10 - 117") == "10–117 CHF"
    assert lire_prix("CHF 20") == "20 CHF"
    assert lire_prix("CHF 5,- pro Kind") == "5 CHF"
