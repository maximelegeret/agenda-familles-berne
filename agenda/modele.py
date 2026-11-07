"""
Format commun d'un événement.

Chaque lecteur de source transforme ce qu'il lit en objets `Evenement`.
Le reste du projet (filtres, doublons, page web) ne connaît que ce format.
Les champs suivent le « Modèle de données » du document de cadrage.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional

# Listes fermées : toute autre valeur est refusée
CATEGORIES = ["atelier", "conte", "spectacle", "musique", "nature", "sport", "fête"]
TYPES = ["événement", "offre régulière"]


@dataclass
class Evenement:
    # --- Obligatoires ---
    id: str                 # source + identifiant d'origine, ex. "kob-lorenz-pauli-2026-11-07"
    titre: str              # dans la langue d'origine
    debut: str              # date et heure ISO, heure de Berne, ex. "2026-11-17T10:00"
    lieu_nom: str
    source: str             # nom de la source, ex. "Kornhausbibliotheken"
    url_source: str         # lien vers la fiche d'origine (toujours affiché)

    # --- Facultatifs (vides si inconnus) ---
    description_courte: str = ""
    fin: Optional[str] = None
    adresse: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    age_min: Optional[float] = None     # en années, ex. 1.5
    age_max: Optional[float] = None
    age_source: Optional[str] = None    # "fourni" (écrit par la source) ou "déduit" (deviné)
    age_texte: str = ""                 # l'âge tel qu'écrit par la source, ex. « ab vier Jahren, in Begleitung »
    prix: str = "inconnu"               # "gratuit", "15 CHF" ou "inconnu"
    inscription_requise: Optional[bool] = None
    categorie: Optional[str] = None     # une valeur de CATEGORIES
    type: str = "événement"             # une valeur de TYPES
    repetition: str = ""                # pour une offre régulière, ex. "chaque dimanche 10:15"
    ville: str = "Berne"
    licence: str = ""
    # Autres sources du même événement (rempli par la fusion des doublons)
    autres_sources: list = field(default_factory=list)

    def __post_init__(self):
        """Vérifie les valeurs dès la création, pour repérer tôt les erreurs d'un lecteur."""
        datetime.fromisoformat(self.debut)  # erreur si la date est mal écrite
        if self.fin:
            datetime.fromisoformat(self.fin)
        if self.categorie is not None and self.categorie not in CATEGORIES:
            raise ValueError(f"Catégorie inconnue : {self.categorie!r} (possibles : {CATEGORIES})")
        if self.type not in TYPES:
            raise ValueError(f"Type inconnu : {self.type!r} (possibles : {TYPES})")
        if self.age_source not in (None, "fourni", "déduit"):
            raise ValueError(f"age_source doit être 'fourni' ou 'déduit', pas {self.age_source!r}")

    def date_debut(self) -> datetime:
        """La date de début sous forme d'objet datetime (pratique pour trier et filtrer)."""
        return datetime.fromisoformat(self.debut)

    def en_dict(self) -> dict:
        """Version dictionnaire, prête à être écrite dans events.json."""
        return asdict(self)
