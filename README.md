# MCP Immo IA – Plateforme d’IA immobilière

## Présentation

Ce projet propose une plateforme d’IA immobilière basée sur le protocole MCP (Model Context Protocol).  
Il expose un modèle d’estimation DVF via un serveur FastMCP, des outils d’analyse (estimation, biens similaires, diagnostic marché) et un agent LangChain pour répondre en langage naturel à des questions immobilières.

---

## 1. Traitement et préparation des données

- **Sources** : Données DVF 2020-2025 (fichiers CSV bruts dans `data/raw_csv/`)
- **Nettoyage** : Scripts Python (`mcp_server/services/dvf_cleaning.py`) pour filtrer, convertir et agréger les transactions immobilières.
- **Enrichissement** : Ajout de données INSEE, démographie, géolocalisation (`mcp_server/services/dvf_enrichment.py`).
- **Export** : Génération d’un dataset propre et enrichi : `data/dvf_final_2020_2025.csv`

---

## 2. Modélisation et IA

- **Modèle ML** : Entraînement d’un modèle de régression (HistGradientBoostingRegressor) pour estimer le prix des biens immobiliers (`mcp_server/services/dvf_model.py`).
- **Export du modèle** : Le pipeline ML est sauvegardé dans `artefacts/model.joblib`.

---

## 3. Serveur MCP et outils

- **Serveur FastMCP** : Expose le modèle et les outils via API SSE (`mcp_server/main_server.py`).
- **Outils MCP** :
  - `estimate_price` : estimation de prix
  - `get_similar_properties` : recherche de biens similaires
  - `get_neighborhood_diagnostic` : diagnostic quartier
- **Tests unitaires** : `tests/test_tools_unit.py` (pytest)

---

## 4. Agent IA LangChain

- **Agent LangChain** : Se connecte au serveur MCP, récupère dynamiquement les tools, et répond en langage naturel via MistralAI (`agent/langchain_agent_ia.py`).
- **Client MCP** : Conversion automatique des tools MCP en tools LangChain (`agent/client_mcp.py`).

---

## 5. Dockerisation

- **Dockerfile** : Image Python 3.10, installation des dépendances, copie du code et du modèle.
- **Build local** :
  ```sh
  docker build -t mcp_immo_ia .
  ```
- **Exécution locale** :
  ```sh
  docker run -p 8000:8000 -v $(pwd)/data:/app/data mcp_immo_ia
  ```

---

## 6. CI/CD GitHub Actions

- **Workflow** : `.github/workflows/docker-mcp_image.yml`
- **Fonctionnement** :
  - Build automatique de l’image Docker à chaque push sur `main`
  - Push de l’image sur GitHub Container Registry (GHCR)
  - Génération d’un fichier `version.json` pour le suivi des builds

---

## 7. Déploiement K3s sur Datalab

1. **Créer un namespace** :
   ```sh
   kubectl create namespace mcp-immo-ia-patricia-promise
   ```

2. **Créer un secret pour GHCR** :
   ```sh
   kubectl create secret docker-registry ghcr-secret \
     --docker-server=ghcr.io \
     --docker-username=<utilisateur-github> \
     --docker-password=<PAT-github> \
     --docker-email=<email>
   ```

3. **Déployer le serveur** :
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: mcp-immo-ia-patricia-promise
     namespace: mcp-immo-ia-patricia-promise
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: mcp-immo-ia
     template:
       metadata:
         labels:
           app: mcp-immo-ia
       spec:
         containers:
         - name: mcp-immo-ia
           image: ghcr.io/patriciatenda/mcp_immo_ia:main
           ports:
           - containerPort: 8000
           volumeMounts:
           - name: data
             mountPath: /app/data
         imagePullSecrets:
         - name: ghcr-secret
         volumes:
         - name: data
           hostPath:
             path: /chemin/vers/data
   ```

4. **Exposer le service** :
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: mcp-immo-ia-service
     namespace: mcp-immo-ia-patricia-promise
   spec:
     type: NodePort
     selector:
       app: mcp-immo-ia
     ports:
       - protocol: TCP
         port: 8000
         targetPort: 8000
         nodePort: 30800
   ```

5. **Déployer** :
   ```sh
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml
   ```

---
---

## 8. Lancer le serveur MCP

**En local (hors Docker)**

```sh
python -m mcp_server
```
ou
```sh
python mcp_server/main_server.py
```

Le serveur MCP expose les outils sur http://localhost:8000/sse

**En Docker**

```sh
docker run -p 8000:8000 -v $(pwd)/data:/app/data mcp_immo_ia
```
## 9. Structure du projet

```
mcp_immo_IA/
├── agent/                        # Agent LangChain, client MCP
│   ├── langchain_agent_ia.py
│   ├── client_mcp.py
│   └── llm_agent.py
├── artefacts/                    # Modèle ML (joblib)
│   └── model.joblib
├── data/                         # Données (CSV, non incluses dans l’image)
│   ├── dvf_final_2020_2025.csv
│   ├── communes_france_2025.csv
│   └── raw_csv/                  # Données brutes annuelles
├── mcp_server/                   # Serveur FastMCP, outils, services
│   ├── main_server.py
│   ├── __main__.py
│   ├── tools/
│   │   ├── estimate_tool.py
│   │   ├── similar_tool.py
│   │   └── neighborhood_tool.py
│   ├── services/
│   │   ├── dvf_cleaning.py
│   │   ├── dvf_enrichment.py
│   │   ├── dvf_model.py
│   │   ├── neighborhood_diag.py
│   │   └── similar_properties.py
│   └── README_mcp.md
├── tests/                        # Tests unitaires et d’intégration
│   ├── test_tools.py
│   └── test_tools_unit.py
├── Dockerfile                    # Image Docker du serveur
├── requirements.txt              # Dépendances Python
├── .github/
│   └── workflows/
│       └── docker-mcp_image.yml
├── docker-compose.yml            # (optionnel) Lancement multi-services
├── README.md                     # Documentation projet (ce fichier)
├── docs/                         # Documentation additionnelle (optionnel)
├── k8s/                          # Manifests Kubernetes (optionnel)
└── ...                           # Autres dossiers/fichiers éventuels
```

---

## 10. Stack technique utilisée

- **Python 3.10**
- **Pandas, scikit-learn, joblib** (traitement, ML)
- **FastMCP** (serveur MCP SSE)
- **LangChain** (agent IA, orchestration)
- **MistralAI** (LLM)
- **Docker** (containerisation)
- **GitHub Actions** (CI/CD)
- **K3s** (Kubernetes léger)
- **Datalab** (plateforme de déploiement)

---

## 11. Bonnes pratiques appliquées

- Gestion des secrets (PAT) via GitHub et Kubernetes
- Nettoyage de l’historique git en cas de fuite de secret
- Respect de la casse des dossiers pour compatibilité Linux/Docker
- Build reproductible et traçable (version.json)
- Tests unitaires et d’intégration

---
## 12. Conclusion
Ce projet démontre la mise en place d’une plateforme d’IA immobilière complète, de la préparation des données à la modélisation, en passant par l’exposition via MCP et le déploiement en cluster Kubernetes.
