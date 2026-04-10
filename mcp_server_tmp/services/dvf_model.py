import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import sys

from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# import matplotlib.pyplot as plt

# =========================
# 1. Chargement des données
# =========================
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
sys.path.insert(0, str(BASE_DIR /"mcp_server"/"services"/"dvf_model.py"))

df = pd.read_csv(
    DATA_DIR / "dvf_final_2020_2025.csv",
    low_memory=False,
    dtype={
        "Code postal": str,
        "Code departement": str,
        "Code commune": str,
        "code_insee": str
    }
)


# =========================
# 1.1 Analyse exploratoire
# =========================

"""print("=== TAUX DE VALEURS MANQUANTES ===")
print(df.isna().mean().sort_values(ascending=False))

df["Valeur fonciere"].hist(bins=100)
plt.show()

print(df.shape)
print(df.dtypes)"""


# =========================
# 1.2 Filtrage des outliers
# =========================

# Supprime les biens à prix extrême (< 10k€ ou > 1.5M€)
df = df[(df["Valeur fonciere"] >= 10_000) & (df["Valeur fonciere"] <= 1_500_000)]
print(f"Lignes après filtrage outliers : {len(df)}")

# =========================
# 2. Préparation des données
# =========================

# Target
# Target transformée en log
y = np.log1p(df["Valeur fonciere"])

# Features (on enlève les fuites de données)
X = df.drop(columns=[
    "Valeur fonciere",
    "prix_m2",          # ⚠️ fuite de données
    "Date mutation",
    "code_insee",
    "Section",
    "No plan"
])

# =========================
# 3. Colonnes
# =========================

numeric_features = [
    "Surface reelle bati",
    "Nombre pieces principales",
    "Surface terrain",
    "Nombre de lots",
    "annee_mutation",
    "mois_mutation",
    "trimestre_mutation",
    "population",
    "superficie_km2",
    "densite",
    "latitude_centre",
    "longitude_centre"
]

categorical_features = [
    "Code postal",
    "Type local",
    "Code departement",
    "reg_nom",
    "dep_nom"
]


# =========================
# 4. Imputation
# =========================
numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))
])

# =========================
# 4. Preprocessing
# =========================

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ]
)

# =========================
# 5. Modèle
# =========================

model = HistGradientBoostingRegressor(
    max_iter=500,
    max_depth=12,
    learning_rate=0.03,
    min_samples_leaf=20,
    random_state=42
)

# Pipeline complète
pipeline = Pipeline([
    ("preprocessing", preprocessor),
    ("model", model)
])

# =========================
# 6. Train / Test split
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# 7. Entraînement
# =========================

print("Entraînement du modèle...")
pipeline.fit(X_train, y_train)
print("Modèle entraîné.")
# =========================
# 8. Prédictions
# =========================

# Prédiction sur l'échelle log
y_pred_log = pipeline.predict(X_test)

# Retour à l'échelle réelle des prix
y_pred = np.expm1(y_pred_log)
y_test_real = np.expm1(y_test)

# =========================
# 9. Évaluation
# =========================

mae = mean_absolute_error(y_test_real, y_pred)
rmse = np.sqrt(mean_squared_error(y_test_real, y_pred))
r2 = r2_score(y_test_real, y_pred)

print("===== Résultats du modèle =====")
print(f"MAE  : {mae:.2f} €")
print(f"RMSE : {rmse:.2f} €")
print(f"R2   : {r2:.4f}")

# =========================
# 10. Sauvegarde modèle
# =========================

artefacts_dir = BASE_DIR/"artefacts"
artefacts_dir.mkdir(exist_ok=True)
joblib.dump(pipeline, artefacts_dir / "model.joblib")

print("Modèle sauvegardé sous artefacts/model.joblib")

if __name__ == "__main__":
    print("Ce script a été exécuté directement.")