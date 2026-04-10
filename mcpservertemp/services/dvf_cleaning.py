import pandas as pd
from pathlib import Path

# Sélection des colonnes importantes pour le dataset
cols_to_keep = [
    "Date mutation",
    "Nature mutation",
    "Valeur fonciere",
    "Code postal",
    "Commune",
    "Code departement",
    "Code commune",
    "Section",
    "No plan",
    "Type local",
    "Surface reelle bati",
    "Nombre pieces principales",
    "Surface terrain",
    "Nombre de lots"
]


# Chargement et nettoyage des données DVF de 2020 à 2025
BASE_DIR = Path(__file__).resolve().parents[2]  # remonte jusqu'à mcp_immo_IA
folder = BASE_DIR / "data"/"raw_csv"
files_dvf = [folder / f"dvf_{year}.csv" for year in range(2020, 2026)]

# Lire et concaténer les fichiers DVF
dfs = []
for file in files_dvf:
    df = pd.read_csv(file, dtype=str, low_memory=False)
    df.columns = df.columns.str.strip()
    dfs.append(df)

# Concaténer tous les DataFrames en un seul DataFrame
dvf = pd.concat(dfs, ignore_index=True)
dvf = dvf[cols_to_keep].copy() # Garder uniquement les colonnes sélectionnées

# Nettoyage et transformation des données
dvf["Date mutation"] = pd.to_datetime(
    dvf["Date mutation"],
    format="%d/%m/%Y",
    errors="coerce"
)

dvf["Valeur fonciere"] = pd.to_numeric(
    dvf["Valeur fonciere"].str.replace(",", ".", regex=False),
    errors="coerce"
)

# Colonnes réellement numériques
numeric_cols = [
    "Surface reelle bati",
    "Nombre pieces principales",
    "Surface terrain",
    "Nombre de lots"
]

for col in numeric_cols:
    dvf[col] = pd.to_numeric(
        dvf[col].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    )

# Colonnes identifiantes à garder en texte
dvf["Code postal"] = pd.to_numeric(dvf["Code postal"], errors="coerce")
dvf["Code commune"] = pd.to_numeric(dvf["Code commune"], errors="coerce")

dvf["Code postal"] = dvf["Code postal"].astype("Int64").astype(str).str.zfill(5)
dvf["Code commune"] = dvf["Code commune"].astype("Int64").astype(str).str.zfill(3)
dvf["Code departement"] = dvf["Code departement"].astype(str).str.zfill(2)


# Filtrer les données pour ne garder que les ventes de maisons et d'appartements avec des valeurs foncières valides
dvf = dvf[dvf["Nature mutation"] == "Vente"].copy() # Garder uniquement les ventes
dvf = dvf[dvf["Valeur fonciere"].notna() & (dvf["Valeur fonciere"] > 0)]
dvf = dvf[dvf["Type local"].isin(["Maison", "Appartement"])]

# Définir les colonnes de regroupement pour éviter les doublons
group_cols = [
    "Date mutation",
    "Valeur fonciere",
    "Code postal",
    "Code departement",
    "Code commune"
]

# Définir les fonctions d'agrégation pour chaque colonne
agg_dict = {
    "Type local": "first",
    "Surface reelle bati": "max",
    "Nombre pieces principales": "max",
    "Surface terrain": "sum",
    "Nombre de lots": "max",
    "Code commune": "first",
    "Section": "first",
    "No plan": "first"
}


# Agréger les données pour éviter les doublons et garder les informations pertinentes
dvf_clean = dvf.groupby(group_cols, dropna=False, as_index=False).agg(agg_dict)
dvf_clean["annee_mutation"] = dvf_clean["Date mutation"].dt.year
dvf_clean["mois_mutation"] = dvf_clean["Date mutation"].dt.month
dvf_clean["trimestre_mutation"] = dvf_clean["Date mutation"].dt.quarter


# Filtrer les transactions avec des surfaces bâties réalistes et des valeurs foncières significatives
dvf_clean = dvf_clean[
    (dvf_clean["Surface reelle bati"] > 9) &
    (dvf_clean["Surface reelle bati"] <= 500) &
    (dvf_clean["Nombre pieces principales"] <= 15) &
    (dvf_clean["Valeur fonciere"] >= 10000) &
    (dvf_clean["Valeur fonciere"] <= 5_000_000)
].copy()


# Calcul du prix au mètre carré
# ⚠️ Attention : prix_m2 uniquement pour analyse (data leakage sinon)
dvf_clean["prix_m2"] = dvf_clean["Valeur fonciere"] / dvf_clean["Surface reelle bati"]


# Enregistrer le dataset nettoyé
dvf_clean = dvf_clean.drop_duplicates()
dvf_clean.to_csv(BASE_DIR / "data" / "dvf_clean_2020_2025.csv", index=False)

if __name__ == "__main__":
    print(f"Dataset DVF nettoyé : {dvf_clean.shape[0]} lignes")