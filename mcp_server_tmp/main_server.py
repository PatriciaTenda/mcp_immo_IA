from pathlib import Path
import sys

# Ajouter le dossier parent (mcp_immo_IA/) au path AVANT les imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastmcp import FastMCP
from mcp_server_tmp.tools.estimate_tool import estimate_price
from mcp_server_tmp.tools.similar_tool import get_similar_properties
from mcp_server_tmp.tools.neighborhood_tool import get_neighborhood_diagnostic


mcp = FastMCP("Immo IA Server MCP")

# Enregistrement des 3 tools
mcp.tool(estimate_price)
mcp.tool(get_similar_properties)
mcp.tool(get_neighborhood_diagnostic)

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)