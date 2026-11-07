"""
Tests du lecteur Creaviva, sur un extrait de l'API enregistré le 7 nov. 2026
(tests/pages/creaviva/seances.json). Aucune connexion internet n'est nécessaire.
"""

import json
from pathlib import Path

from agenda.lecteurs.creaviva import analyser

DONNEES = json.loads((Path(__file__).parent / "pages" / "creaviva" / "seances.json").read_text(encoding="utf-8"))


def lire(espace=18):
    return analyser(DONNEES["seances"], DONNEES["lies"], espace, "Creaviva")


def par_titre(evts, mot):
    return [e for e in evts if mot in e.titre]


def test_seulement_le_creaviva():
    evts = lire()
    assert not par_titre(evts, "Artur")               # Artur = Kunstmuseum (espace 7)
    assert par_titre(lire(espace=7), "Artur")         # … qu'on retrouve avec l'espace 7


def test_cours_adultes_ecartes():
    assert not par_titre(lire(), "Kurse für Erwachsene")


def test_familienmorgen():
    e = par_titre(lire(), "Familienmorgen")[0]
    assert e.debut.endswith("T10:15") and e.fin.endswith("T11:30")
    assert e.prix == "18 CHF"
    assert e.age_texte == "Familien mit Kindern ab 4 J."
    assert e.url_source == "https://zpk.org/de/workshop/mit-roberto-burle-marx-im-atelier"


def test_horaire_taglich_corrige():
    # La Fünfliber-Werkstatt est ouverte « Täglich zwischen 10:00–17:00 »
    e = par_titre(lire(), "Fünfliber")[0]
    assert e.debut.endswith("T10:00") and e.fin.endswith("T17:00")


def test_gratuit_dans_le_texte():
    # « Ab 9 J., kostenlos »
    assert par_titre(lire(), "Creaviva Club")[0].prix == "gratuit"
