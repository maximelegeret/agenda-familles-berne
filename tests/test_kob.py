"""
Tests du lecteur kob.ch, sur des pages enregistrées le 7 nov. 2026 (dossier tests/pages/kob).
Aucune connexion internet n'est nécessaire.
"""

from pathlib import Path

from agenda.lecteurs.kob import analyser_fiche, est_pour_enfants, lire_dates, lire_inscription, lire_prix

PAGES = Path(__file__).parent / "pages" / "kob"


def lire_page(nom):
    return (PAGES / nom).read_text(encoding="utf-8")


def test_dates_simples_et_multiples():
    texte = ("Mittwoch, 11. November 2026, 14:15-14:45 Uhr "
             "Samstag, 12. Dezember 2026, 14:15-14:45 Uhr")
    assert lire_dates(texte) == [
        ("2026-11-11T14:15", "2026-11-11T14:45"),
        ("2026-12-12T14:15", "2026-12-12T14:45"),
    ]


def test_date_sur_deux_jours():
    texte = "Freitag, 13. November 2026 bis Samstag, 14. November 2026, 18:00-08:30 Uhr"
    assert lire_dates(texte) == [("2026-11-13T18:00", "2026-11-14T08:30")]


def test_mois_avec_umlaut():
    assert lire_dates("Mittwoch, 10. März 2027, 14:30-15:00 Uhr") == [("2027-03-10T14:30", "2027-03-10T15:00")]


def test_prix():
    assert lire_prix("Gratis") == "gratuit"
    assert lire_prix("Eintritt frei") == "gratuit"
    assert lire_prix("freier Eintritt") == "gratuit"
    assert lire_prix("CHF 5,- pro Kind") == "5 CHF"
    assert lire_prix("5 Franken") == "5 CHF"
    assert lire_prix(None) == "inconnu"


def test_inscription():
    assert lire_inscription("Anmeldung erforderlich unter …") is True
    assert lire_inscription("Ohne Anmeldung, einfach vorbeikommen") is False
    assert lire_inscription("Wir freuen uns auf euch") is None


def test_fiche_simple():
    evts = analyser_fiche(lire_page("lorenz-pauli.html"), "https://exemple", 49819, "Lorenz Pauli")
    assert len(evts) == 1
    e = evts[0]
    assert e.debut == "2026-11-07T16:00" and e.fin == "2026-11-07T17:00"
    assert e.lieu_nom == "Bibliothek Zollikofen"
    assert e.prix == "5 CHF"
    assert e.age_texte == "ab fünf Jahren"
    assert e.inscription_requise is True
    assert e.id == "kob-49819-202611071600"


def test_fiche_plusieurs_dates():
    evts = analyser_fiche(lire_page("maerli-zyt-plusieurs-dates.html"), "https://exemple", 16370, "Märli-Zyt")
    assert [e.debut for e in evts] == ["2026-11-11T14:15", "2026-12-12T14:15", "2026-12-16T14:15"]
    assert all(e.prix == "gratuit" for e in evts)
    assert len({e.id for e in evts}) == 3  # un identifiant différent par date


def test_fiche_periode():
    evts = analyser_fiche(lire_page("erzaehlnacht-periode.html"), "https://exemple", 50984, "Erzählnacht")
    assert len(evts) == 1
    assert evts[0].fin == "2026-11-14T08:30"


def test_selection_enfants():
    assert est_pour_enfants({"categories": [55], "alter": []})        # Kinderanlass
    assert est_pour_enfants({"categories": [22], "alter": [105]})     # une tranche d'âge
    assert not est_pour_enfants({"categories": [57], "alter": []})    # Sprachcafé
