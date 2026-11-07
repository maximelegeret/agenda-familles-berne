"""Tests du tri enfants, de la lecture de l'âge et de la catégorie. Lancement : pytest"""

import pytest

from agenda.filtre_enfants import completer, extraire_age, trier
from agenda.modele import Evenement


# Textes réels relevés sur kob.ch le 7 nov. 2026
@pytest.mark.parametrize("texte, attendu", [
    ("ab fünf Jahren", (5, None)),
    ("Ab 4 Jahren", (4, None)),
    ("ab vier Jahren, in Begleitung", (4, None)),
    ("für Kinder ab drei Jahren", (3, None)),
    ("ab ca. 4 Jahren, in Begleitung auch für Jüngere", (4, None)),
    ("sechs bis zehn Jahre", (6, 10)),
    ("acht bis 14 Jahre", (8, 14)),
    ("6 Monate bis 4 Jahre in Begleitung", (0.5, 4)),
    ("ab ca. 6 Monaten bis 4 Jahre", (0.5, 4)),
    ("bis ca. vier Jahre in Begleitung", (None, 4)),
    ("bis 4 Jahre", (None, 4)),
    ("1. bis 3. Klasse", (6, 9)),
    ("Ab 12 Jahren", (12, None)),
    ("14+", (14, None)),
    ("für Kids ab 4 Jahren, Regenbogenfamilien und ihre Freund:innen", (4, None)),
    ("dès 8 ans", (8, None)),                   # français (ateliers Cocoriki)
    ("de 4 à 8 ans", (4, 8)),
    ("à partir de 18 mois", (1.5, None)),
    ("ages 3 to 6 years", (3, 6)),              # anglais
    ("", (None, None)),
    ("Wir freuen uns auf euch", (None, None)),
    ("von 14 bis 16 Uhr", (None, None)),   # des heures, pas un âge
])
def test_extraire_age(texte, attendu):
    assert extraire_age(texte) == attendu


def evt(titre, description="", age_texte=""):
    return Evenement(id="t", titre=titre, description_courte=description, age_texte=age_texte,
                     debut="2026-11-10T10:00", lieu_nom="Lieu", source="Test", url_source="https://x")


def test_age_trouve_dans_la_description():
    e = completer(evt("Lesung", "Die Geschichten richten sich an Menschen ab fünf Jahren."))
    assert (e.age_min, e.age_source) == (5, "fourni")


@pytest.mark.parametrize("titre, categorie", [
    ("Märli-Zyt", "conte"),
    ("Schweizer Erzählnacht – «Stimmen»", "conte"),
    ("Gschichte-Zyt u Baschtle", "conte"),          # le premier thème trouvé l'emporte
    ("Erzähl- und Bastelstunde", "conte"),
    ("Familienführung im Historischen Museum", "visite"),
    ("Peter und der Wolf – Familienkonzert", "musique"),
    ("Schachkurse für Kinder", "atelier"),
    ("Queerlesen", "conte"),
    ("Spielabend", None),
])
def test_categorie(titre, categorie):
    assert completer(evt(titre)).categorie == categorie


def test_tri():
    # Trop âgé : écarté, même dans une source pour enfants
    assert trier(completer(evt("Spielabend", age_texte="Ab 12 Jahren")), source_enfants=True)[0] is False
    # Âge compatible : gardé
    assert trier(completer(evt("Lesung", age_texte="ab 4 Jahren")))[0] is True
    # Pas d'âge, mais mot enfant : gardé
    assert trier(evt("Familienkonzert"))[0] is True
    # Rien d'enfant dans une source générale : écarté
    assert trier(evt("Sinfoniekonzert Brahms"))[0] is False
    # Rien d'enfant, mais source pour enfants : gardé
    assert trier(evt("Cocoriki – Talemo"), source_enfants=True)[0] is True
    # Public adulte explicite : écarté
    assert trier(evt("Lesung nur für Erwachsene"), source_enfants=True)[0] is False
