"""Tests des lieux permanents (lieux.yaml) et du calcul des horaires. Lancement : python -m pytest"""

from datetime import date
from pathlib import Path

import pytest

from agenda.lieux import charger, fetes_mobiles, jours_feries, paques, plages_du_jour, verifier

FICHIER = Path(__file__).parent.parent / "lieux.yaml"


def lieux_par_id():
    lieux, erreurs = charger(FICHIER, aujourd_hui=date(2026, 11, 9))
    assert erreurs == []
    return {l["id"]: l for l in lieux}


def fiche(identifiant):
    """La fiche brute de lieux.yaml (avec ses horaires)."""
    import yaml
    donnees = yaml.safe_load(FICHIER.read_text(encoding="utf-8"))
    return next(l for l in donnees["lieux"] if l["id"] == identifiant)


def test_calendrier_bernois():
    assert paques(2026) == date(2026, 4, 5)
    assert paques(2027) == date(2027, 3, 28)
    assert fetes_mobiles(2026)["zibelemarit"] == date(2026, 11, 23)
    assert date(2026, 12, 26) in jours_feries(2026)
    assert date(2026, 4, 6) in jours_feries(2026)  # lundi de Pâques


def test_fichier_lieux_valide():
    lieux = lieux_par_id()
    assert len(lieux) >= 15
    assert lieux["baerenpark"]["toujours_ouvert"] is True
    assert "ouverture" not in lieux["baerenpark"]


def test_musee_lundi_et_zibelemarit():
    nmbe = fiche("nmbe")
    assert plages_du_jour(nmbe, date(2026, 11, 9)) == ["14:00-17:00"]   # lundi après-midi
    assert plages_du_jour(nmbe, date(2026, 11, 23)) == []               # Zibelemärit : fermé
    assert plages_du_jour(nmbe, date(2026, 12, 26)) == ["10:00-17:00"]  # férié : horaire spécial
    assert plages_du_jour(nmbe, date(2026, 12, 25)) == []


def test_ferme_le_lundi_sauf_ferie():
    mfk = fiche("mfk")
    assert plages_du_jour(mfk, date(2026, 11, 9)) == []                 # lundi ordinaire
    assert plages_du_jour(mfk, date(2027, 3, 29)) == ["10:00-17:00"]    # lundi de Pâques


def test_saisons():
    tierpark = fiche("tierpark")
    assert plages_du_jour(tierpark, date(2026, 11, 15)) == ["09:00-17:00"]  # hiver
    assert plages_du_jour(tierpark, date(2027, 7, 1)) == ["09:00-18:00"]    # été
    assert plages_du_jour(tierpark, date(2028, 2, 29)) == ["09:00-17:00"]   # année bissextile
    # Horaires d'hiver seulement relevés pour la piscine : hors saison = fermé
    assert plages_du_jour(fiche("weyermannshaus"), date(2027, 7, 4)) == []
    assert plages_du_jour(fiche("weyermannshaus"), date(2026, 11, 15)) == ["07:00-18:00"]


def test_fiche_mal_ecrite():
    mauvaise = dict(fiche("mfk"), horaires=[{"mar": "10h-17h"}])
    with pytest.raises(ValueError, match="plage horaire mal écrite"):
        verifier(mauvaise)
    with pytest.raises(ValueError, match="type inconnu"):
        verifier(dict(fiche("mfk"), type="zoo"))
