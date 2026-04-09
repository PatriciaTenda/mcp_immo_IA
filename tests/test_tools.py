"""
Test des 3 tools MCP sans serveur — appel direct des fonctions Python.
"""
import sys
from pathlib import Path

# Ajouter mcp_immo_IA/ au path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp_server.tools.estimate_tool import estimate_price
from mcp_server.tools.similar_tool import get_similar_properties
from mcp_server.tools.neighborhood_tool import get_neighborhood_diagnostic


print("=" * 60)
print("TEST 1 : Estimation de prix")
print("=" * 60)

result = estimate_price(
    code_postal="75015",
    code_departement="75",
    type_local="Appartement",
    surface_bati=65.0,
    nb_pieces=3,
    surface_terrain=0.0,
    nb_lots=1,
    annee=2024,
    mois=6,
    reg_nom="Ile-de-France",
    dep_nom="Paris",
    population=2133111.0,
    superficie_km2=105.4,
    densite=20237.0,
    latitude=48.8566,
    longitude=2.3522
)
print(result)


print("\n" + "=" * 60)
print("TEST 2 : Biens similaires")
print("=" * 60)

result = get_similar_properties(
    code_postal="75015",
    type_local="Appartement",
    surface=65.0,
    nb_pieces=3,
    top_n=3
)
print(result)


print("\n" + "=" * 60)
print("TEST 3 : Diagnostic quartier")
print("=" * 60)

result = get_neighborhood_diagnostic(code_postal="75015")
print(result)
