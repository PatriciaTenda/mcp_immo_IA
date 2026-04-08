import pandas as pd
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

# Chargement du dataset DVF nettoyé
dvf = pd.read_csv(DATA_DIR / "dvf_clean_2020_2025.csv")

# Création du code INSEE
dvf["Code commune"] = dvf["Code commune"].astype(str).str.zfill(3)
dvf["Code departement"] = dvf["Code departement"].astype(str).str.zfill(2)

dvf["code_insee"] = dvf["Code departement"] + dvf["Code commune"]

# Chargement des communes
communes = pd.read_csv(DATA_DIR / "communes_france_2025.csv", dtype=str)
communes.columns = communes.columns.str.strip()

# Nettoyage code INSEE
communes["code_insee"] = communes["code_insee"].astype(str).str.zfill(5)

# Sélection des colonnes utiles
communes = communes[[
    "code_insee",
    "nom_standard",
    "population",
    "superficie_km2",
    "densite",
    "latitude_centre",
    "longitude_centre",
    "reg_nom",
    "dep_nom"
]]

# Conversion des types
for col in ["population", "superficie_km2", "densite", "latitude_centre", "longitude_centre"]:
    communes[col] = pd.to_numeric(communes[col], errors="coerce")

# Jointure
dvf_final = dvf.merge(
    communes,
    on="code_insee",
    how="left"
)

# Vérification rapide
print("Taux de valeurs manquantes après jointure :")
print(dvf_final.isna().mean().sort_values(ascending=False).head(10))

# Sauvegarde
dvf_final.to_csv(DATA_DIR / "dvf_final_2020_2025.csv", index=False)

print(f"Dataset final enrichi : {dvf_final.shape[0]} lignes")


if __name__ == "__main__":
    print("Enrichissement DVF terminé. Dataset final sauvegardé dans data/dvf_final_2020_2025.csv")
