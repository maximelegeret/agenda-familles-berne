"""Tests du flux d'agenda .ics. Lancement : pytest"""

from datetime import datetime
from zoneinfo import ZoneInfo

from icalendar import Calendar

from agenda.calendrier import ecrire_ics
from agenda.modele import Evenement


def test_flux_ics(tmp_path):
    evts = [
        Evenement(id="kob-1-202611111415", titre="Märli-Zyt", debut="2026-11-11T14:15", fin="2026-11-11T14:45",
                  lieu_nom="Bibliothek Münsingen", source="Kornhausbibliotheken", url_source="https://kob.ch/x",
                  description_courte="Märchen für Kinder ab 4."),
        Evenement(id="menuhin-743-202611081600", titre="Peter und der Wolf", debut="2026-11-08T16:00",
                  lieu_nom="Yehudi Menuhin Forum", adresse="Helvetiaplatz 6, 3005 Bern",
                  source="Yehudi Menuhin Forum", url_source="https://menuhinforum.ch/events/peter-und-der-wolf/"),
    ]
    chemin = tmp_path / "agenda.ics"
    n = ecrire_ics(evts, chemin, maintenant=datetime(2026, 11, 8, 5, 0, tzinfo=ZoneInfo("Europe/Zurich")))
    assert n == 2
    cal = Calendar.from_ical(chemin.read_bytes())
    assert any(c.name == "VTIMEZONE" and str(c["tzid"]) == "Europe/Zurich" for c in cal.walk())
    vevents = [c for c in cal.walk() if c.name == "VEVENT"]
    assert [str(v["summary"]) for v in vevents] == ["Märli-Zyt", "Peter und der Wolf"]
    marli = vevents[0]
    assert marli["dtstart"].dt == datetime(2026, 11, 11, 14, 15, tzinfo=ZoneInfo("Europe/Zurich"))
    assert "kob.ch/x" in str(marli["description"])
    # Sans heure de fin : une heure par défaut
    wolf = vevents[1]
    assert (wolf["dtend"].dt - wolf["dtstart"].dt).seconds == 3600
    assert str(wolf["location"]) == "Yehudi Menuhin Forum, Helvetiaplatz 6, 3005 Bern"
