"""
Petits outils de lecture de texte, partagés par plusieurs lecteurs.
"""

import re

MOTS_GRATUIT = ("gratis", "kostenlos", "eintritt frei", "freier eintritt", "free admission", "gratuit")


def lire_prix(texte):
    """
    « Gratis » -> 'gratuit' ; « CHF 5,- pro Kind » -> '5 CHF' ;
    « Regulärer Eintritt plus Ticket zu CHF 5.- » -> 'entrée + 5 CHF' ; rien -> 'inconnu'.
    """
    if not texte:
        return "inconnu"
    bas = texte.lower()
    if any(mot in bas for mot in MOTS_GRATUIT):
        return "gratuit"
    # « Im normalen Eintritt inbegriffen » : rien à payer en plus du billet d'entrée
    if "inbegriffen" in bas or "im eintritt enthalten" in bas:
        return "compris dans l'entrée"
    # Fourchette de prix : « CHF 10 - 37 » -> '10–37 CHF'
    fourchette = re.search(r"(\d+)\s*[-–]\s*(\d+)", texte)
    if fourchette:
        return f"{fourchette.group(1)}–{fourchette.group(2)} CHF"
    nombre = re.search(r"(\d+(?:[.,]\d+)?)", texte)
    if nombre:
        # « 90.00 » -> « 90 » ; « 7.50 » reste « 7.5 »
        montant = f"{float(nombre.group(1).replace(',', '.').rstrip('.')):g}"
        # Un supplément au billet d'entrée du musée
        if "eintritt" in bas and ("plus" in bas or "zusätzlich" in bas):
            return f"entrée + {montant} CHF"
        return f"{montant} CHF"
    return texte  # texte inattendu : on le garde tel quel


def lire_inscription(texte):
    """Vrai si le texte demande une inscription, Faux s'il dit le contraire, None sinon."""
    bas = texte.lower()
    if "ohne anmeldung" in bas or "keine anmeldung" in bas:
        return False
    if "anmeldung" in bas:
        return True
    return None


def raccourcir(texte, longueur=200):
    """Coupe un texte trop long au dernier mot entier, avec « … »."""
    texte = " ".join(texte.split())
    if len(texte) <= longueur:
        return texte
    return texte[: longueur - 3].rsplit(" ", 1)[0] + "…"
