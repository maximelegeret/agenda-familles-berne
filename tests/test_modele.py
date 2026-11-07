"""Tests du format commun et de la fenêtre des 14 jours. Lancement : pytest"""

from datetime import datetime

import pytest

from agenda.modele import Evenement
from recuperer import FUSEAU, charger_ajouts_manuels, dans_la_fenetre


def exemple(**changements):
    """Un événement valide, dont on peut modifier quelques champs."""
    donnees = dict(
        id="test-1", titre="Atelier test", debut="2026-11-10T10:00",
        lieu_nom="Bibliothèque", source="Test", url_source="https://exemple.ch",
    )
    donnees.update(changements)
    return Evenement(**donnees)


def test_evenement_valide():
    e = exemple(categorie="atelier", age_min=3, age_source="fourni")
    assert e.en_dict()["ville"] == "Berne"
    assert e.prix == "inconnu"


def test_categorie_inconnue_refusee():
    with pytest.raises(ValueError):
        exemple(categorie="cinéma")


def test_date_mal_ecrite_refusee():
    with pytest.raises(ValueError):
        exemple(debut="10/11/2026")


def test_fenetre_14_jours():
    maintenant = datetime(2026, 11, 7, 13, 0, tzinfo=FUSEAU)
    assert dans_la_fenetre(exemple(debut="2026-11-08T16:00"), maintenant)
    assert dans_la_fenetre(exemple(debut="2026-11-21T10:00"), maintenant)       # dans 14 jours
    assert not dans_la_fenetre(exemple(debut="2026-11-22T10:00"), maintenant)   # trop loin
    assert not dans_la_fenetre(exemple(debut="2026-11-07T10:00", fin="2026-11-07T11:00"), maintenant)  # fini
    assert dans_la_fenetre(exemple(debut="2026-11-07T12:00", fin="2026-11-07T14:00"), maintenant)      # en cours


def test_ajouts_manuels_lisibles():
    # Le fichier ajouts_manuels.yaml doit toujours être valide
    assert all(isinstance(e, Evenement) for e in charger_ajouts_manuels())
