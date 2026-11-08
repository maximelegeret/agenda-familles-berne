"""
Flux d'agenda (.ics) de toutes les activités des 14 prochains jours.

Écrit chaque nuit dans docs/agenda.ics. On peut s'y abonner une fois depuis
l'agenda du téléphone (iPhone : Réglages > Calendrier > Comptes > Ajouter un
calendrier avec abonnement ; Google Agenda : « À partir de l'URL ») : les
activités apparaissent et se mettent à jour toutes seules.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event

FUSEAU = ZoneInfo("Europe/Zurich")
DUREE_PAR_DEFAUT = timedelta(hours=1)


def evenement_ics(e, maintenant):
    """Un Evenement du projet -> un VEVENT."""
    debut = datetime.fromisoformat(e.debut).replace(tzinfo=FUSEAU)
    fin = datetime.fromisoformat(e.fin).replace(tzinfo=FUSEAU) if e.fin else debut + DUREE_PAR_DEFAUT
    v = Event()
    v.add("uid", f"{e.id}@agenda-familles-berne")
    v.add("dtstamp", maintenant)
    v.add("dtstart", debut)
    v.add("dtend", fin)
    v.add("summary", e.titre)
    v.add("location", ", ".join(x for x in (e.lieu_nom, e.adresse) if x))
    details = [e.description_courte, f"Source : {e.source}", e.url_source]
    v.add("description", "\n".join(x for x in details if x))
    if e.url_source:
        v.add("url", e.url_source)
    return v


def ecrire_ics(evenements, chemin, maintenant=None):
    """Écrit le flux .ics ; renvoie le nombre d'activités écrites."""
    maintenant = maintenant or datetime.now(FUSEAU)
    cal = Calendar()
    cal.add("prodid", "-//Agenda Familles Berne//FR")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", "Agenda Familles Berne")
    cal.add("x-wr-timezone", "Europe/Zurich")
    # Demande aux agendas abonnés de se rafraîchir deux fois par jour
    cal.add("refresh-interval", timedelta(hours=12), parameters={"VALUE": "DURATION"})
    cal.add("x-published-ttl", "PT12H")
    for e in evenements:
        cal.add_component(evenement_ics(e, maintenant))
    # Décrit le fuseau Europe/Zurich dans le fichier (VTIMEZONE), exigé par certains agendas
    cal.add_missing_timezones()
    chemin.write_bytes(cal.to_ical())
    return len(evenements)
