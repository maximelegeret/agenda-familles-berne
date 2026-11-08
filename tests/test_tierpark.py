"""Tests du lecteur Tierpark Bern, sur des pages enregistrées le 8 nov. 2026."""

from datetime import datetime
from pathlib import Path

from agenda.filtre_enfants import completer, extraire_age
from agenda.lecteurs.tierpark import lire_calendrier, lire_fiche, vers_evenement
from agenda.textes import lire_prix

PAGES = Path(__file__).parent / "pages" / "tierpark"


def page(nom):
    return (PAGES / nom).read_text(encoding="utf-8")


def test_seulement_les_activites_pour_enfants():
    activites = lire_calendrier(page("calendrier.html"))
    titres = [a["titre"] for a in activites]
    assert "Märli lose und Tierli baschtle" in titres
    assert "Angstseminar gegen Spinnenphobie" not in titres   # pas marqué pour enfants
    assert "Abendführung im Vivarium" not in titres


def test_complet_retire_du_titre():
    activites = lire_calendrier(page("calendrier.html"))
    nuit = next(a for a in activites if "Übernachtung" in a["titre"])
    assert nuit["complet"] and not nuit["titre"].startswith("Ausverkauft")


def test_fiche_complete():
    activite = lire_calendrier(page("calendrier.html"))[0]
    e = completer(vers_evenement(activite, lire_fiche(page("maerli-lose.html"))))
    assert (e.debut, e.fin) == ("2026-11-11T14:00", "2026-11-11T15:30")
    assert e.lieu_nom == "Tierpark Dählhölzli" and e.adresse.startswith("Tierparkweg 1")
    assert (e.age_min, e.age_max) == (4, 6)          # « Für Kinder von 4 bis 6 Jahren. »
    assert e.prix == "45 CHF"
    assert e.categorie == "conte"
    assert activite["debut"] == datetime(2026, 11, 11, 14, 0)


def test_regles_partagees():
    assert lire_prix("Im normalen Eintritt inbegriffen") == "compris dans l'entrée"
    assert lire_prix("90.00 CHF") == "90 CHF"
    assert extraire_age("Für Mädchen und Buben zwischen 7 und 10 Jahren") == (7, 10)
