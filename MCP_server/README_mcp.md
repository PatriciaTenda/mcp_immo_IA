
# MCP Server - Guide d'Utilisation

## 📋 Vue d'ensemble

Ce document décrit l'intégration et l'utilisation du serveur MCP (Model Context Protocol) dans le projet immobilier IA.

## 🚀 Démarrage rapide

### Prérequis
- Node.js 16+
- npm ou yarn

### Installation
```bash
npm install
npm start
```

## 🔧 Configuration

Configurez les variables d'environnement dans `.env` :
```
MCP_PORT=3000
MCP_API_KEY=your_key_here
```

## 📚 Utilisation

### Connection au serveur
```javascript
const mcp = require('./mcp-server');
mcp.connect();
```

### Endpoints principaux
- `POST /api/data` - Envoyer des données
- `GET /api/status` - Vérifier le statut

## 🗂️ Structure du projet

```
MCP_server/
├── src/
├── config/
├── tests/
└── README_mcp.md
```

## 📝 Logs et debugging

Les logs sont disponibles dans `./logs/`

## 🤝 Support

Pour toute question, consultez la documentation officielle MCP.
