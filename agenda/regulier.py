"""
Repère les offres régulières (ex. Familienmorgen chaque dimanche) parmi les événements datés.

Règle : une même activité (même source, même lien, même titre) qui revient
à 7 jours d'intervalle exactement, à la même heure, est une offre régulière.
Elle sort de la liste jour par jour et devient une seule fiche « Chaque semaine »,
avec un résumé des horaires (ex. « dimanche 10:15–11:30 »).
"""

from collections import defaultdict
from dataclasses import replace
from datetime import timedelta

CATEGORIES_JAMAIS_REGULIERES = {"spectacle"}

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def _horaire(e):
    """« 10:15–11:30 » (ou « 10:15 » sans heure de fin)."""
    debut = e.debut[11:16]
    return f"{debut}–{e.fin[11:16]}" if e.fin and e.fin[:10] == e.debut[:10] else debut


def _est_hebdomadaire(seances):
    """Vrai si deux séances ont lieu à 7 jours d'intervalle exactement."""
    debuts = {s.date_debut() for s in seances}
    return any(d + timedelta(days=7) in debuts for d in debuts)


def _liste_jours(numeros):
    """[1, 2, 3, 4] -> « du mardi au vendredi » ; [5, 6] -> « samedi et dimanche »."""
    numeros = sorted(numeros)
    if len(numeros) == 7:
        return "tous les jours"
    if len(numeros) >= 3 and numeros == list(range(numeros[0], numeros[-1] + 1)):
        return f"du {JOURS[numeros[0]]} au {JOURS[numeros[-1]]}"
    noms = [JOURS[n] for n in numeros]
    return noms[0] if len(noms) == 1 else ", ".join(noms[:-1]) + " et " + noms[-1]


def resumer_horaires(seances):
    """
    Résume les horaires d'une offre, en regroupant les jours qui ont les mêmes heures.
    Ex. « du mardi au vendredi 14:00–15:00, 16:00–17:00 · samedi et dimanche 12:00–13:00, … »
    """
    heures_par_jour = defaultdict(set)
    for s in seances:
        heures_par_jour[s.date_debut().weekday()].add(_horaire(s))
    jours_par_heures = defaultdict(list)
    for jour, heures in heures_par_jour.items():
        jours_par_heures[tuple(sorted(heures))].append(jour)
    morceaux = sorted(jours_par_heures.items(), key=lambda kv: min(kv[1]))
    return " · ".join(f"{_liste_jours(jours)} {', '.join(heures)}" for heures, jours in morceaux)


def separer(evenements):
    """
    Sépare les événements en (événements datés, offres régulières).
    Chaque offre régulière est un Evenement de type « offre régulière » dont le début
    est la prochaine séance et dont `repetition` résume les horaires.
    """
    groupes = defaultdict(list)
    for e in evenements:
        groupes[(e.source, e.url_source, e.titre)].append(e)

    dates, offres = [], []
    for seances in groupes.values():
        # Un spectacle joué plusieurs fois par semaine est une série limitée, pas une
        # offre permanente : il reste visible jour par jour (ex. « Kalif Storch »).
        if seances[0].categorie in CATEGORIES_JAMAIS_REGULIERES:
            dates.extend(seances)
        elif len(seances) >= 2 and _est_hebdomadaire(seances):
            seances.sort(key=lambda s: s.debut)
            prochaine = seances[0]
            offres.append(replace(
                prochaine,
                id=prochaine.id.rsplit("-", 1)[0] + "-regulier",
                type="offre régulière",
                repetition=resumer_horaires(seances),
            ))
        else:
            dates.extend(seances)
    return dates, offres
