"""
Lieux permanents (onglet « Sortir ») : lecture de lieux.yaml et calcul des horaires.

Pour que la page reste simple, le calcul difficile se fait ici, chaque nuit :
pour chacun des 14 prochains jours, on écrit les plages d'ouverture réelles du lieu
(saison, jour de la semaine, jours fériés bernois, fermetures). La page n'a plus qu'à
comparer l'heure actuelle à ces plages pour dire « Ouvert jusqu'à 17:00 » ou « Fermé ».
"""

import re
from datetime import date, timedelta

import yaml

TYPES = ["animaux", "nature", "musee", "piscine", "jeux", "bibliotheque", "rencontre"]
JOURS = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]
EQUIPEMENTS = ["langer", "poussette", "cafe", "wc", "jeux"]
OBLIGATOIRES = ["id", "nom", "type", "dedans", "adresse", "lat", "lng", "prix", "resume", "horaires", "url", "verifie_le"]
RE_PLAGE = re.compile(r"^\d{2}:\d{2}-\d{2}:\d{2}$")
RE_JOUR_MOIS = re.compile(r"^\d{2}-\d{2}$")


# --- Calendrier bernois ---

def paques(annee):
    """Date de Pâques (calcul grégorien classique, dit « de Meeus »)."""
    a, b, c = annee % 19, annee // 100, annee % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mois = (h + l - 7 * m + 114) // 31
    jour = (h + l - 7 * m + 114) % 31 + 1
    return date(annee, mois, jour)


def fetes_mobiles(annee):
    """Fêtes qui changent de date chaque année -> {nom: date}."""
    p = paques(annee)
    novembre = date(annee, 11, 1)
    premier_lundi = novembre + timedelta(days=(7 - novembre.weekday()) % 7)
    return {
        "vendredi_saint": p - timedelta(days=2),
        "paques": p,
        "lundi_paques": p + timedelta(days=1),
        "ascension": p + timedelta(days=39),
        "pentecote": p + timedelta(days=49),
        "lundi_pentecote": p + timedelta(days=50),
        "zibelemarit": premier_lundi + timedelta(weeks=3),  # 4e lundi de novembre (pas un jour férié)
    }


def jours_feries(annee):
    """Jours fériés officiels du canton de Berne."""
    mobiles = fetes_mobiles(annee)
    fixes = [date(annee, 1, 1), date(annee, 1, 2), date(annee, 8, 1), date(annee, 12, 25), date(annee, 12, 26)]
    return set(fixes) | {mobiles[n] for n in ("vendredi_saint", "lundi_paques", "ascension", "lundi_pentecote")}


# --- Contrôle de lieux.yaml ---

def _verifier_plages(texte, ou):
    for plage in str(texte).split(","):
        if not RE_PLAGE.match(plage.strip()):
            raise ValueError(f"{ou} : plage horaire mal écrite « {plage.strip()} » (attendu HH:MM-HH:MM)")


def verifier(lieu):
    """Lève une erreur claire si la fiche est incomplète ou mal écrite."""
    nom = lieu.get("id", "?")
    manquants = [c for c in OBLIGATOIRES if lieu.get(c) in (None, "")]
    if manquants:
        raise ValueError(f"{nom} : champs manquants {manquants}")
    if lieu["type"] not in TYPES:
        raise ValueError(f"{nom} : type inconnu « {lieu['type']} »")
    if lieu["dedans"] not in (True, False, "mixte"):
        raise ValueError(f"{nom} : dedans doit valoir true, false ou mixte")
    inconnus = set(lieu.get("equipements", [])) - set(EQUIPEMENTS)
    if inconnus:
        raise ValueError(f"{nom} : équipements inconnus {sorted(inconnus)}")
    if lieu["horaires"] != "toujours":
        for periode in lieu["horaires"]:
            for borne in ("du", "au"):
                if borne in periode and not RE_JOUR_MOIS.match(str(periode[borne])):
                    raise ValueError(f"{nom} : « {borne} » doit être au format MM-JJ")
            for jour in JOURS:
                if jour in periode:
                    _verifier_plages(periode[jour], f"{nom} ({jour})")
        feries = str(lieu.get("feries", "ferme"))
        if feries not in ("ferme", "normal"):
            _verifier_plages(feries, f"{nom} (feries)")
    mobiles = set(fetes_mobiles(2026))
    for f in lieu.get("fermetures", []):
        if not (RE_JOUR_MOIS.match(str(f)) or f in mobiles):
            raise ValueError(f"{nom} : fermeture inconnue « {f} »")


# --- Horaires d'un jour donné ---

def _dans_periode(jour, periode):
    """Vrai si la date tombe dans la période « du »–« au » (qui peut passer le Nouvel An)."""
    if "du" not in periode:
        return True
    mj = (jour.month, jour.day)
    du = tuple(int(x) for x in periode["du"].split("-"))
    au = tuple(int(x) for x in periode["au"].split("-"))
    return du <= mj <= au if du <= au else (mj >= du or mj <= au)


def _plages(texte):
    return [p.strip() for p in str(texte).split(",")]


def plages_du_jour(lieu, jour):
    """Plages d'ouverture d'un lieu pour une date : ["09:00-17:00"], [] si fermé, None si accès libre."""
    if lieu["horaires"] == "toujours":
        return None
    mobiles = fetes_mobiles(jour.year)
    for f in lieu.get("fermetures", []):
        if f in mobiles and mobiles[f] == jour:
            return []
        if RE_JOUR_MOIS.match(str(f)) and jour.strftime("%m-%d") == f:
            return []
    periode = next((p for p in lieu["horaires"] if _dans_periode(jour, p)), None)
    if periode is None:
        return []  # hors saison
    if jour in jours_feries(jour.year):
        feries = str(lieu.get("feries", "ferme"))
        if feries == "ferme":
            return []
        if feries != "normal":
            return _plages(feries)
    texte = periode.get(JOURS[jour.weekday()])
    return _plages(texte) if texte else []


# --- Lecture et sortie pour la page ---

def charger(chemin, aujourd_hui=None, nb_jours=14):
    """
    Lit lieux.yaml, vérifie chaque fiche et ajoute les plages des prochains jours.
    Renvoie (lieux, erreurs) : une fiche mal écrite est écartée avec un message, sans bloquer les autres.
    """
    aujourd_hui = aujourd_hui or date.today()
    with open(chemin, encoding="utf-8") as f:
        donnees = yaml.safe_load(f) or {}
    lieux, erreurs, vus = [], [], set()
    for lieu in donnees.get("lieux", []):
        try:
            verifier(lieu)
            if lieu["id"] in vus:
                raise ValueError(f"{lieu['id']} : identifiant en double")
        except ValueError as erreur:
            erreurs.append(str(erreur))
            continue
        vus.add(lieu["id"])
        sortie = {k: v for k, v in lieu.items() if k not in ("horaires", "feries", "fermetures")}
        sortie["verifie_le"] = str(lieu["verifie_le"])
        sortie["toujours_ouvert"] = lieu["horaires"] == "toujours"
        if not sortie["toujours_ouvert"]:
            sortie["ouverture"] = {
                (aujourd_hui + timedelta(days=n)).isoformat(): plages_du_jour(lieu, aujourd_hui + timedelta(days=n))
                for n in range(nb_jours + 1)
            }
        lieux.append(sortie)
    return lieux, erreurs
