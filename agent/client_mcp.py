"""
Client MCP — Se connecte au serveur MCP et récupère les tools.
Le client utilise langchain-mcp-adapters pour convertir automatiquement
les tools MCP en tools LangChain utilisables par l'agent.
"""
import sys
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient


# chemin vers le dossier mcp_immo_IA/
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE_DIR))
WORKING_DIR = str(BASE_DIR)

# Configuration du serveur MCP
MCP_SERVERS = {
    "immo_ia_server_mcp":{
        "transport": "stdio",
        "command": "python",
        "args":     [str(BASE_DIR/"mcp_server"/"main_server.py")],
        "cwd":      WORKING_DIR,
    }
}

# Création du client MCP
def get_mcp_client():
    """Fonction pour créer et retourner un client MCP connecté au serveur."""
    return MultiServerMCPClient(MCP_SERVERS)
