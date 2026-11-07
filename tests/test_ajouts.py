"""Tests des ajouts manuels. Lancement : pytest"""

from datetime import date, datetime

from agenda.ajouts import charger, lire_fiche
from recuperer import FICHIER_AJOUTS


def test_fiche_minimale():
    e = lire_fiche({"titre": "Kasperlitheater", "debut": "2026-11-21 15:00", "lieu_nom": "Rosengarten"})
    assert e.debut == "2026-11-21T15:00"
    assert e.source == "Ajout manuel"
    assert e.url_source == ""
    assert e.id == "manuel-kasperlitheater-202611211500"


def test_formats_de_date():
    base = {"titre": "Test", "lieu_nom": "Ici"}
    assert lire_fiche({**base, "debut": "2026-11-21T15:00"}).debut == "2026-11-21T15:00"
    assert lire_fiche({**base, "debut": "2026-11-21"}).debut == "2026-11-21T00:00"
    # YAML transforme parfois les dates non entre guillemets en objets
    assert lire_fiche({**base, "debut": date(2026, 11, 21)}).debut == "2026-11-21T00:00"
    assert lire_fiche({**base, "debut": datetime(2026, 11, 21, 15, 0)}).debut == "2026-11-21T15:00"


def test_accents_dans_l_identifiant():
    e = lire_fiche({"titre": "Fäger: Zirkus & Spiel", "debut": "2026-11-20 14:00", "lieu_nom": "X"})
    assert e.id == "manuel-fager-zirkus-spiel-202611201400"


def test_erreurs_claires(tmp_path):
    fichier = tmp_path / "ajouts.yaml"
    fichier.write_text(
        "evenements:\n"
        "  - titre: Bon\n"
        "    debut: \"2026-11-20 14:00\"\n"
        "    lieu_nom: Ici\n"
        "  - titre: Sans lieu\n"
        "    debut: \"2026-11-20 14:00\"\n"
        "  - titre: Faute de frappe\n"
        "    debut: \"2026-11-20 14:00\"\n"
        "    lieu_nom: Ici\n"
        "    categori: conte\n"
        "  - titre: Mauvaise date\n"
        "    debut: \"20.11.2026\"\n"
        "    lieu_nom: Ici\n",
        encoding="utf-8",
    )
    evenements, erreurs = charger(fichier)
    assert [e.titre for e in evenements] == ["Bon"]       # les fiches valides passent quand même
    assert len(erreurs) == 3
    assert "lieu_nom" in erreurs[0]
    assert "categori" in erreurs[1]
    assert "Mauvaise date" in erreurs[2]


def test_fichier_illisible(tmp_path):
    fichier = tmp_path / "ajouts.yaml"
    fichier.write_text("evenements:\n  - titre: [pas fermé\n", encoding="utf-8")
    evenements, erreurs = charger(fichier)
    assert evenements == [] and len(erreurs) == 1


def test_fichier_du_projet_valide():
    # Le vrai fichier ajouts_manuels.yaml ne doit contenir aucune erreur
    assert charger(FICHIER_AJOUTS)[1] == []
