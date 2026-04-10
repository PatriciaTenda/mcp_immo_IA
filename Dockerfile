FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY mcp_immo_IA/mcp_server/ mcp_server/

# Copier le modèle ML (1.8 MB)
COPY mcp_immo_IA/artefacts/ artefacts/

# Le dossier data/ sera monté en volume (CSV trop gros pour l'image)
# Volume attendu : /app/data/dvf_final_2020_2025.csv

EXPOSE 8000

CMD ["python", "mcp_server/main_server.py"]
