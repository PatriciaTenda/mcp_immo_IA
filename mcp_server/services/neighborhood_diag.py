import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


def diagnose_neighborhood(code_postal: str) -> dict:
    """
    Diagnostic immobilier d'un quartier/commune.

    Retourne :
    - prix médian, moyen, min, max
    - prix au m² médian
    - nombre de transactions
    - répartition par type de bien
    - évolution annuelle des prix
    - infos démographiques (population, densité)
    """

    df = pd.read_csv(
        DATA_DIR / "dvf_final_2020_2025.csv",
        dtype={"Code postal": str, "Code departement": str, "code_insee": str}
    )

    # Filtre sur le code postal
    zone = df[df["Code postal"] == code_postal].copy()

    if zone.empty:
        return {"erreur": f"Aucune donnée trouvée pour le code postal {code_postal}"}

    # --- Stats de prix ---
    stats_prix = {
        "prix_median": round(zone["Valeur fonciere"].median(), 2),
        "prix_moyen": round(zone["Valeur fonciere"].mean(), 2),
        "prix_min": round(zone["Valeur fonciere"].min(), 2),
        "prix_max": round(zone["Valeur fonciere"].max(), 2),
        "prix_m2_median": round(zone["prix_m2"].median(), 2),
    }

    # --- Volume de transactions ---
    nb_transactions = len(zone)

    # --- Répartition par type de bien ---
    repartition = zone["Type local"].value_counts().to_dict()

    # --- Évolution annuelle des prix médians ---
    evolution = (
        zone.groupby("annee_mutation")["Valeur fonciere"]
        .median()
        .round(2)
        .to_dict()
    )

    # --- Infos démographiques (prend la première ligne non nulle) ---
    demo = zone[["nom_standard", "population", "densite", "superficie_km2", "reg_nom", "dep_nom"]].dropna().iloc[0].to_dict() if not zone[["population"]].dropna().empty else {}

    return {
        "code_postal": code_postal,
        "nb_transactions": nb_transactions,
        "stats_prix": stats_prix,
        "repartition_types": repartition,
        "evolution_annuelle": evolution,
        "demographie": demo
    }