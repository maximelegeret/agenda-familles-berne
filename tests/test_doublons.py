"""Tests de la fusion des doublons, sur des cas construits. Lancement : pytest"""

from agenda.doublons import fusionner_doublons, lieux_compatibles, titres_proches
from agenda.modele import Evenement


def evt(source, titre="Peter und der Wolf", debut="2026-11-08T16:00", lieu="Yehudi Menuhin Forum", **autres):
    return Evenement(id=f"{source}-1", titre=titre, debut=debut, lieu_nom=lieu,
                     source=source, url_source=f"https://{source}.ch/evt", **autres)


def test_meme_concert_dans_deux_sources():
    menuhin = evt("menuhin", prix="gratuit", adresse="Helvetiaplatz 6, 3005 Bern")
    eventfrog = evt("eventfrog", titre="Peter und der Wolf – Familienkonzert", debut="2026-11-08T16:00",
                    lieu="Menuhin Forum Bern", age_min=4, age_source="fourni")
    resultat, nb = fusionner_doublons([menuhin, eventfrog])
    assert nb == 1 and len(resultat) == 1
    e = resultat[0]
    # La fiche gardée est complétée par l'autre : prix + adresse + âge
    assert (e.prix, e.age_min) == ("gratuit", 4)
    assert e.adresse == "Helvetiaplatz 6, 3005 Bern"
    # Le lien de l'autre source est conservé
    assert len(e.autres_sources) == 1
    assert e.autres_sources[0]["url_source"] in ("https://menuhin.ch/evt", "https://eventfrog.ch/evt")


def test_heure_legerement_differente():
    # Une source arrondit : 16:00 contre 16:15
    resultat, nb = fusionner_doublons([evt("a"), evt("b", debut="2026-11-08T16:15")])
    assert nb == 1


def test_pas_de_fusion_si_autre_jour_ou_autre_heure():
    _, nb = fusionner_doublons([evt("a"), evt("b", debut="2026-11-09T16:00")])
    assert nb == 0
    _, nb = fusionner_doublons([evt("a"), evt("b", debut="2026-11-08T19:30")])
    assert nb == 0


def test_pas_de_fusion_dans_une_meme_source():
    # La même Erzählnacht dans deux bibliothèques, à la même heure : deux événements distincts
    a = evt("kob", titre="Schweizer Erzählnacht", debut="2026-11-13T19:00", lieu="Bibliothek Holligen")
    b = evt("kob", titre="Schweizer Erzählnacht", debut="2026-11-13T19:00", lieu="Bibliothek Münchenbuchsee")
    _, nb = fusionner_doublons([a, b])
    assert nb == 0


def test_pas_de_fusion_si_lieux_differents():
    a = evt("a", titre="Märchenstunde", lieu="Bibliothek Bümpliz")
    b = evt("b", titre="Märchenstunde", lieu="Alpines Museum")
    _, nb = fusionner_doublons([a, b])
    assert nb == 0


def test_titres_et_lieux():
    assert titres_proches("Der kleine Prinz", "Der kleine Prinz – 1. Familienkonzert")
    assert titres_proches("Märli-Zyt", "Märli Zyt!")
    assert not titres_proches("Märli-Zyt", "Spielabend")
    assert lieux_compatibles("Yehudi Menuhin Forum", "Menuhin Forum Bern")
    assert lieux_compatibles("Stadttheater", "")            # lieu manquant : on ne bloque pas
    assert not lieux_compatibles("Vidmar 1", "Stadttheater")
