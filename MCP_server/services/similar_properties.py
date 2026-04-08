import pandas as pd
from pathlib import Path

# Chemin vers les données
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


def find_similar_properties(
    code_postal: str,
    type_local: str,
    surface: float,
    nb_pieces: int,
    top_n: int = 5
) -> list[dict]:
    """
    Trouve les biens similaires vendus récemment.

    Logique :
    1. Filtre par code postal et type de bien
    2. Filtre les surfaces proches (±30%)
    3. Filtre par nombre de pièces (±1)
    4. Trie par date de mutation (les plus récents d'abord)
    5. Retourne les top_n résultats
    """

    df = pd.read_csv(
        DATA_DIR / "dvf_final_2020_2025.csv",
        dtype={"Code postal": str, "Code departement": str, "code_insee": str}
    )

    # Filtre 1 : même zone et même type
    mask = (
        (df["Code postal"] == code_postal) &
        (df["Type local"] == type_local)
    )
    filtered = df[mask].copy()

    # Filtre 2 : surface proche (±30%)
    surface_min = surface * 0.7
    surface_max = surface * 1.3
    filtered = filtered[
        (filtered["Surface reelle bati"] >= surface_min) &
        (filtered["Surface reelle bati"] <= surface_max)
    ]

    # Filtre 3 : nombre de pièces proche (±1)
    filtered = filtered[
        (filtered["Nombre pieces principales"] >= nb_pieces - 1) &
        (filtered["Nombre pieces principales"] <= nb_pieces + 1)
    ]

    # Tri par date (les plus récents en premier)
    filtered = filtered.sort_values("Date mutation", ascending=False)

    # Sélection des colonnes utiles pour le résultat
    result = filtered.head(top_n)[[
        "Date mutation",
        "Valeur fonciere",
        "Surface reelle bati",
        "Nombre pieces principales",
        "Surface terrain",
        "prix_m2",
        "Code postal",
        "Type local",
        "nom_standard"
    ]]

    return result.to_dict(orient="records")