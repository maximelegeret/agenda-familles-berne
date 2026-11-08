"""Tests du lecteur Schlachthaus Theater, sur des pages enregistrées le 8 nov. 2026."""

from datetime import date, datetime
from pathlib import Path

from agenda.lecteurs.schlachthaus import annee_probable, lire_fiche, lire_programme

PAGES = Path(__file__).parent / "pages" / "schlachthaus"


def page(nom):
    return (PAGES / nom).read_text(encoding="utf-8")


def programme():
    return lire_programme(page("programme.html"), aujourd_hui=date(2026, 11, 8))


def test_representations_enfants():
    s = programme()
    assert len(s) == 28
    premier = s[0]
    assert premier["debut"] == datetime(2026, 11, 8, 15, 0)
    assert premier["titre"] == "Munterbunt (Theater für die Allerjüngsten)"
    assert premier["age"] == "Ab 1 Jahren"


def test_pas_de_seance_scolaire_ni_ado():
    s = programme()
    # « Käfer » a des séances scolaires en semaine à 10:00 : elles sont écartées
    assert not any(x["titre"].startswith("Käfer") and x["debut"].hour == 10 for x in s)
    assert all(x["age"] for x in s)  # chaque séance gardée indique un âge


def test_annee_des_dates_sans_annee():
    assert annee_probable(10, 1, date(2026, 11, 8)) == 2027   # janvier prochain
    assert annee_probable(20, 11, date(2026, 11, 8)) == 2026
    assert annee_probable(15, 9, date(2026, 11, 8)) == 2026   # tout récent : même année


def test_fiche_prix_et_texte():
    prix, texte = lire_fiche(page("im-haerz.html"))
    assert prix == "5–33 CHF"
    assert texte.startswith("Ein Kind muss am Herzen operiert werden")
    _, texte_munterbunt = lire_fiche(page("munterbunt.html"))
    assert texte_munterbunt.startswith("Wie fliegt es?")
