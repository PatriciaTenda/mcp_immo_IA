import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
ARTEFACTS_DIR = BASE_DIR / "artefacts"

# Chargement du modèle une seule fois au démarrage
pipeline = joblib.load(ARTEFACTS_DIR / "model.joblib")


def estimate_price(
    code_postal: str,
    code_departement: str,
    type_local: str,
    surface_bati: float,
    nb_pieces: int,
    surface_terrain: float,
    nb_lots: int,
    annee: int,
    mois: int,
    reg_nom: str,
    dep_nom: str,
    population: float,
    superficie_km2: float,
    densite: float,
    latitude: float,
    longitude: float
) -> str:
    """
    Estime le prix d'un bien immobilier via le modèle entraîné.
    """

    # Construire le DataFrame avec les mêmes colonnes que l'entraînement
    input_data = pd.DataFrame([{
        "Surface reelle bati": surface_bati,
        "Nombre pieces principales": nb_pieces,
        "Surface terrain": surface_terrain,
        "Nombre de lots": nb_lots,
        "annee_mutation": annee,
        "mois_mutation": mois,
        "trimestre_mutation": ((mois - 1) // 3) + 1, # division entière arrondie vers le bas pour obtenir le trimestre
        "population": population,
        "superficie_km2": superficie_km2,
        "densite": densite,
        "latitude_centre": latitude,
        "longitude_centre": longitude,
        "Code postal": code_postal,
        "Type local": type_local,
        "Code departement": code_departement,
        "reg_nom": reg_nom,
        "dep_nom": dep_nom,
    }])

    # Prédiction (le modèle prédit en log, on reconvertit en valeur réelle ensuite)
    pred_log = pipeline.predict(input_data)[0]
    prix_estime = round(np.expm1(pred_log), 2) # permet de reconvertir en valeur réelle

    return json.dumps({
        "prix_estime": prix_estime,
        "unite": "EUR",
        "modele": "HistGradientBoostingRegressor"
    }, ensure_ascii=False)