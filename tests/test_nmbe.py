"""Tests du lecteur Naturhistorisches Museum Bern, sur des pages enregistrées le 8 nov. 2026."""

from pathlib import Path

from agenda.lecteurs.nmbe import lire_calendrier, lire_fiche

PAGES = Path(__file__).parent / "pages" / "nmbe"


def page(nom):
    return (PAGES / nom).read_text(encoding="utf-8")


def test_calendrier_familles():
    seances = lire_calendrier(page("calendrier-familles.html"))
    premier = seances[0]
    # L'attribut datetime dit « 14:00Z » mais c'est l'heure de Berne affichée : on garde 14:00
    assert (premier["debut"], premier["fin"]) == ("2026-11-25T14:00", "2026-11-25T16:00")
    assert premier["titre"] == "Tierzeichnen"
    # Une activité à deux créneaux le même jour donne deux séances
    tiergeschichten = [s for s in seances if s["titre"].startswith("Tiergeschichten") and s["debut"].startswith("2026-11-29")]
    assert [s["debut"][11:] for s in tiergeschichten] == ["11:00", "13:30"]


def test_fiche():
    infos = lire_fiche(page("tierzeichnen.html"))
    assert infos["Alter"] == "Ab 6 Jahren"
    assert infos["Kosten"].startswith("CHF 5.00 pro Person")
    assert infos["Anmeldung"].startswith("obligatorisch")
    assert infos["texte"].startswith("Für alle, die gerne zeichnen")
