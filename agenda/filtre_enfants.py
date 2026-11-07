"""
Tri « enfants et familles », lecture de l'âge et choix de la catégorie, par mots-clés.

- extraire_age(texte)  : « ab vier Jahren » -> (4, None) ; « 6 Monate bis 4 Jahre » -> (0.5, 4)
- completer(evenement) : remplit age_min / age_max / categorie quand c'est possible
- trier(evenement, source_enfants) : décide si on garde l'événement, et pourquoi

Plus tard, les cas flous pourront être envoyés à l'API Claude (étape à décider).
"""

import re

# Tranche d'âge visée par le site (cadrage : 0–10 ans)
AGE_MAX_VISE = 10

# Nombres écrits en lettres (allemand) -> chiffres
NOMBRES = {
    "zwei": 2, "drei": 3, "vier": 4, "fünf": 5, "sechs": 6, "sieben": 7,
    "acht": 8, "neun": 9, "zehn": 10, "elf": 11, "zwölf": 12,
}

# Unités d'âge en allemand, français et anglais
UNITE = r"(monat\w*|jahr\w*|j\.|ans?\b|mois|years?|months?)"
RE_INTERVALLE = re.compile(r"(\d+)\s*" + UNITE + r"?\s*(?:bis|-|–)\s*(\d+)\s*" + UNITE)
RE_CLASSES = re.compile(r"(\d+)\.\s*(?:bis|-|–)\s*(\d+)\.\s*klasse")
RE_DES = re.compile(r"\bab\s*(\d+)\s*" + UNITE)
RE_JUSQUA = re.compile(r"\bbis\s*(\d+)\s*" + UNITE)
RE_PLUS = re.compile(r"\b(\d+)\s*\+")

# Mots qui signalent un public d'enfants ou de familles
MOTS_ENFANTS = [
    "kinder", "kind ", "kids", "familie", "familien", "märli", "märchen", "gschicht",
    "geschichtenzeit", "bilderbuch", "värsli", "kasperli", "chaschperli",
    "junges publikum", "kleinkind", "baby", "enfants", "famille", "children", "family",
]
# Mots qui signalent un public adulte
MOTS_ADULTES = ["nur für erwachsene", "für erwachsene ", "senioren", "60+"]

# Catégorie selon les mots trouvés ; la première qui correspond l'emporte
MOTS_CATEGORIES = [
    ("visite", ["führung", "rundgang", "guided tour", "visite"]),
    ("spectacle", ["theater", "puppen", "figurentheater", "zirkus", "tanz", "spectacle", "kasperli", "chaschperli"]),
    ("musique", ["konzert", "musik", "singen", "lieder", "värsli", "concert"]),
    ("conte", ["geschicht", "gschicht", "märli", "märchen", "erzähl", "lesung", "lesen", "vorlese", "bilderbuch", "liest", "conte"]),
    ("atelier", ["workshop", "atelier", "basteln", "baschtle", "bastel", "kurs", "malen", "gestalten"]),
    ("nature", ["natur", "wald", "garten", "tierpark", "draussen"]),
    ("sport", ["sport", "turnen", "schach", "bewegung"]),
    ("fête", ["fest", "fasnacht", "party", "feier", "fête"]),
]


def _normaliser(texte):
    """Minuscules, nombres en chiffres, sans « ca. »."""
    t = texte.lower().replace("ca.", " ").replace("circa", " ")
    for mot, chiffre in NOMBRES.items():
        t = re.sub(rf"\b{mot}\b", str(chiffre), t)
    t = re.sub(r"\bein(em|en)?\s+jahr", "1 jahr", t)
    # Français et anglais ramenés aux mots allemands : « dès 4 ans » -> « ab 4 ans »
    t = re.sub(r"\b(dès|à partir de|from|ages?)\b", "ab", t)
    t = re.sub(r"(\d)\s*(à|to)\s*(\d)", r"\1 bis \3", t)
    return t


def _en_annees(nombre, unite):
    """Convertit en années : 6 mois -> 0.5. Sans unité, on considère des années."""
    valeur = float(nombre)
    if unite and unite.startswith(("monat", "mois", "month")):
        valeur = round(valeur / 12, 2)
    return int(valeur) if valeur == int(valeur) else valeur


def extraire_age(texte):
    """
    Cherche une tranche d'âge dans un texte allemand.
    Renvoie (age_min, age_max) ; None quand l'information manque.
    """
    if not texte:
        return None, None
    t = _normaliser(texte)

    m = RE_INTERVALLE.search(t)
    if m:
        n1, u1, n2, u2 = m.groups()
        return _en_annees(n1, u1 or u2), _en_annees(n2, u2)
    m = RE_CLASSES.search(t)
    if m:  # 1re classe ≈ 6 ans
        return int(m.group(1)) + 5, int(m.group(2)) + 6
    m = RE_DES.search(t)
    if m:
        age_min = _en_annees(*m.groups())
        m2 = RE_JUSQUA.search(t, m.end())
        return age_min, (_en_annees(*m2.groups()) if m2 else None)
    m = RE_JUSQUA.search(t)
    if m:
        return None, _en_annees(*m.groups())
    m = RE_PLUS.search(t)
    if m:
        return int(m.group(1)), None
    return None, None


def _contient(texte, mots):
    return next((mot for mot in mots if mot in texte), None)


def completer(evenement):
    """Remplit l'âge et la catégorie quand ils manquent. Modifie l'événement directement."""
    if evenement.age_min is None and evenement.age_max is None:
        # D'abord le champ âge de la source, puis le titre et la description
        for texte in (evenement.age_texte, evenement.titre, evenement.description_courte):
            age_min, age_max = extraire_age(texte)
            if age_min is not None or age_max is not None:
                evenement.age_min, evenement.age_max = age_min, age_max
                evenement.age_source = "fourni"  # écrit par la source, pas deviné
                break

    if evenement.categorie is None:
        # Le titre compte en premier, la description ensuite
        for texte in (evenement.titre, evenement.description_courte):
            texte = texte.lower()
            for categorie, mots in MOTS_CATEGORIES:
                if _contient(texte, mots):
                    evenement.categorie = categorie
                    break
            if evenement.categorie:
                break
    return evenement


def trier(evenement, source_enfants=False):
    """
    Décide si l'événement est pour les enfants de 0 à 10 ans.
    `source_enfants` : vrai si la source (ou son lecteur) ne donne déjà que des activités pour enfants.
    Renvoie (garder: bool, raison: str).
    """
    if evenement.age_min is not None and evenement.age_min > AGE_MAX_VISE:
        return False, f"dès {evenement.age_min} ans"

    # Un âge compatible indiqué par la source l'emporte sur les mots-clés
    if evenement.age_min is not None or evenement.age_max is not None:
        return True, "âge indiqué"

    texte = " ".join([evenement.titre, evenement.description_courte, evenement.age_texte]).lower() + " "
    mot_adulte = _contient(texte, MOTS_ADULTES)
    if mot_adulte:
        return False, f"mot adulte « {mot_adulte.strip()} »"
    mot_enfant = _contient(texte, MOTS_ENFANTS)
    if mot_enfant:
        return True, f"mot enfant « {mot_enfant.strip()} »"
    if source_enfants:
        return True, "source pour enfants"
    return False, "rien n'indique un public d'enfants"
