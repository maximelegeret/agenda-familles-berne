"""Tests du lecteur MüZe Muri-Gümligen et des offres régulières fixes (pages du 8 nov. 2026)."""

from datetime import date, datetime
from pathlib import Path

from agenda.ajouts import charger_offres
from agenda.lecteurs.mueze import lire_fiche, lire_liste
from recuperer import FICHIER_OFFRES

PAGES = Path(__file__).parent / "pages" / "mueze"


def page(nom):
    return (PAGES / nom).read_text(encoding="utf-8")


def test_liste_sans_rendez_vous_parents():
    activites = lire_liste(page("veranstaltungen.html"))
    titres = {a["titre"] for a in activites}
    assert {"KREALINO – Kinderbasteln", "Theaternachmittag für Kids", "Samichlaus"} <= titres
    assert not any(m in t for t in titres for m in ("Beratung", "Stilltreffen", "Repair", "Kindercoiffeur"))
    krealino = next(a for a in activites if a["titre"].startswith("KREALINO"))
    assert (krealino["debut"], krealino["fin"]) == (datetime(2026, 11, 11, 14, 0), datetime(2026, 11, 11, 16, 0))


def test_fiche():
    texte, prix, inscription = lire_fiche(page("krealino.html"))
    assert texte.startswith("Basteln für die Kleinen von 2-6 Jahren")
    assert prix == "5 CHF"
    assert inscription is True


def test_offres_fixes(tmp_path):
    offres, erreurs = charger_offres(FICHIER_OFFRES, aujourd_hui=date(2026, 11, 8))
    assert erreurs == []
    punktli = offres[0]
    assert punktli.type == "offre régulière" and "mardi" in punktli.repetition
    # Une offre sans horaires est refusée avec un message clair
    fichier = tmp_path / "offres.yaml"
    fichier.write_text("offres:\n  - titre: Sans horaires\n    lieu_nom: Ici\n", encoding="utf-8")
    offres, erreurs = charger_offres(fichier)
    assert offres == [] and "repetition" in erreurs[0]
