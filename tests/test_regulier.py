"""Tests du repérage des offres régulières. Lancement : pytest"""

from agenda.modele import Evenement
from agenda.regulier import resumer_horaires, separer


def seance(debut, fin=None, titre="Familienmorgen", url="https://x/familienmorgen"):
    return Evenement(id=f"t-{debut}", titre=titre, debut=debut, fin=fin,
                     lieu_nom="Creaviva", source="Creaviva", url_source=url)


def test_hebdomadaire_devient_offre():
    evts = [seance("2026-11-08T10:15", "2026-11-08T11:30"), seance("2026-11-15T10:15", "2026-11-15T11:30")]
    dates, offres = separer(evts)
    assert dates == []
    assert len(offres) == 1
    o = offres[0]
    assert o.type == "offre régulière"
    assert o.repetition == "dimanche 10:15–11:30"
    assert o.debut == "2026-11-08T10:15"  # la prochaine séance


def test_mensuel_reste_date():
    evts = [seance("2026-11-11T14:15"), seance("2026-12-09T14:15")]
    dates, offres = separer(evts)
    assert len(dates) == 2 and offres == []


def test_evenement_unique_reste_date():
    dates, offres = separer([seance("2026-11-13T19:00", titre="Erzählnacht", url="https://x/e")])
    assert len(dates) == 1 and offres == []


def test_resume_plusieurs_jours():
    seances = []
    for jour in ("10", "11", "12", "13"):        # du mardi au vendredi
        seances += [seance(f"2026-11-{jour}T14:00", f"2026-11-{jour}T15:00"),
                    seance(f"2026-11-{jour}T16:00", f"2026-11-{jour}T17:00")]
    for jour in ("14", "15"):                    # samedi et dimanche
        seances += [seance(f"2026-11-{jour}T12:00", f"2026-11-{jour}T13:00")]
    assert resumer_horaires(seances) == (
        "du mardi au vendredi 14:00–15:00, 16:00–17:00 · samedi et dimanche 12:00–13:00"
    )
