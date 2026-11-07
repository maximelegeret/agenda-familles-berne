"""
Tests du lecteur Menuhin Forum, sur la page du calendrier enregistrée le 7 nov. 2026.
"""

from pathlib import Path

from agenda.lecteurs.menuhin import analyser_calendrier

PAGE = (Path(__file__).parent / "pages" / "menuhin" / "konzertkalender.html").read_text(encoding="utf-8")


def test_seulement_les_concerts_famille():
    # 30 concerts dans le calendrier, un seul concert famille
    evts = analyser_calendrier(PAGE)
    assert [e.titre for e in evts] == ["Peter und der Wolf"]


def test_peter_und_der_wolf():
    e = analyser_calendrier(PAGE)[0]
    assert e.debut == "2026-11-08T16:00"   # 15:00 UTC = 16:00 à Berne
    assert e.fin is None                   # la fin 23:50 donnée par le site n'est pas fiable
    assert e.prix == "gratuit"             # « Eintritt frei - Kollekte … »
    assert e.url_source == "https://menuhinforum.ch/events/peter-und-der-wolf/"
    assert e.description_courte == ("Familienkonzert – Sergei Prokofiews Musikmärchen mit dem "
                                    "Anemoi Holzbläserquintett und der Schauspielerin Katharina Lienhard als Sprecherin")
