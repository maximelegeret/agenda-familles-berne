"""
Outils communs pour télécharger des pages et des API, poliment.
"""

import time

import requests

# On s'identifie auprès des sites (bonne pratique)
ENTETES = {"User-Agent": "AgendaFamillesBerne/0.1 (agenda familial personnel, 1 lecture par jour)"}


def telecharger(url, params=None, pause=1.0):
    """
    Télécharge une URL et renvoie la réponse.
    `pause` : secondes d'attente après la requête, pour ne pas surcharger le site.
    Lève une erreur si le site répond par une erreur (404, 500…).
    """
    reponse = requests.get(url, params=params, headers=ENTETES, timeout=30)
    reponse.raise_for_status()
    time.sleep(pause)
    return reponse
