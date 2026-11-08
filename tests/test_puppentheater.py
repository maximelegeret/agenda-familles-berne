"""Tests du lecteur Berner Puppen Theater, sur des pages enregistrées le 8 nov. 2026."""

from datetime import datetime
from pathlib import Path

from agenda.lecteurs.puppentheater import lire_fiche, lire_prix_enfants, lire_spielplan
from agenda.modele import Evenement
from agenda.regulier import separer

PAGES = Path(__file__).parent / "pages" / "puppentheater"


def page(nom):
    return (PAGES / nom).read_text(encoding="utf-8")


def test_seances_enfants_seulement():
    seances, prix = lire_spielplan(page("spielplan.html"))
    assert seances[0] == {
        "debut": datetime(2026, 11, 8, 11, 0),
        "titre": "Kalif Storch",
        "age": "Ab 5 Jahren",
        "url": "https://www.berner-puppentheater.ch/kinderprogramm/?act=12",
    }
    # Le programme du soir (« Der kleine Prinz » pour adultes) est ignoré
    assert all("/kinderprogramm" in s["url"] for s in seances)
    assert prix == "18–25 CHF"


def test_mois_suivant():
    seances, _ = lire_spielplan(page("spielplan.html"))
    noel = [s for s in seances if s["titre"].startswith("Wiehnachte")]
    assert noel and noel[0]["debut"] == datetime(2026, 12, 5, 15, 0)


def test_texte_du_spectacle():
    assert lire_fiche(page("kalif-storch.html")).startswith("Der junge Kalif von Bagdad")


def test_prix_absent():
    assert lire_prix_enfants("rien ici") == "inconnu"


def test_spectacle_jamais_range_dans_chaque_semaine():
    # Kalif Storch se joue chaque samedi : il doit rester dans la liste des jours
    seances = [Evenement(id=f"p-{d}", titre="Kalif Storch", debut=d, lieu_nom="BPT", source="BPT",
                         url_source="https://x", categorie="spectacle")
               for d in ("2026-11-14T15:00", "2026-11-21T15:00")]
    dates, offres = separer(seances)
    assert len(dates) == 2 and offres == []


def test_ordre_chronologique_apres_regroupement():
    # Un spectacle à plusieurs dates ne doit pas faire passer le 21 avant le 9
    def evt(titre, debut, categorie):
        return Evenement(id=f"{titre}-{debut}", titre=titre, debut=debut, lieu_nom="L", source="S",
                         url_source=f"https://x/{titre}", categorie=categorie)
    dates, _ = separer([
        evt("Kalif Storch", "2026-11-08T11:00", "spectacle"),
        evt("Kalif Storch", "2026-11-21T15:00", "spectacle"),
        evt("Märli-Zyt", "2026-11-09T14:00", "conte"),
    ])
    assert [d.debut for d in dates] == ["2026-11-08T11:00", "2026-11-09T14:00", "2026-11-21T15:00"]
