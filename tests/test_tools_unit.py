"""
Tests unitaires des 3 tools MCP avec pytest.
Lancer avec : pytest tests/test_tools_unit.py -v
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp_server.tools.estimate_tool import estimate_price
from mcp_server.tools.similar_tool import get_similar_properties
from mcp_server.tools.neighborhood_tool import get_neighborhood_diagnostic


# ============================
# Tests estimate_price
# ============================

def test_estimate_price_returns_dict():
    result = estimate_price(
        code_postal="75015", code_departement="75", type_local="Appartement",
        surface_bati=65.0, nb_pieces=3, surface_terrain=0.0, nb_lots=1,
        annee=2024, mois=6, reg_nom="Ile-de-France", dep_nom="Paris",
        population=2133111.0, superficie_km2=105.4, densite=20237.0,
        latitude=48.8566, longitude=2.3522
    )
    assert isinstance(result, dict)
    assert "prix_estime" in result
    assert "unite" in result


def test_estimate_price_is_positive():
    result = estimate_price(
        code_postal="75015", code_departement="75", type_local="Appartement",
        surface_bati=65.0, nb_pieces=3, surface_terrain=0.0, nb_lots=1,
        annee=2024, mois=6, reg_nom="Ile-de-France", dep_nom="Paris",
        population=2133111.0, superficie_km2=105.4, densite=20237.0,
        latitude=48.8566, longitude=2.3522
    )
    assert result["prix_estime"] > 0


def test_estimate_price_reasonable_range():
    """Un appartement de 65m² à Paris doit coûter entre 100k et 2M€."""
    result = estimate_price(
        code_postal="75015", code_departement="75", type_local="Appartement",
        surface_bati=65.0, nb_pieces=3, surface_terrain=0.0, nb_lots=1,
        annee=2024, mois=6, reg_nom="Ile-de-France", dep_nom="Paris",
        population=2133111.0, superficie_km2=105.4, densite=20237.0,
        latitude=48.8566, longitude=2.3522
    )
    assert 100_000 < result["prix_estime"] < 2_000_000


# ============================
# Tests similar_properties
# ============================

def test_similar_properties_returns_dict():
    result = get_similar_properties(
        code_postal="75015", type_local="Appartement", surface=65.0, nb_pieces=3, top_n=3
    )
    assert isinstance(result, dict)


def test_similar_properties_has_results():
    result = get_similar_properties(
        code_postal="75015", type_local="Appartement", surface=65.0, nb_pieces=3, top_n=3
    )
    assert "biens_similaires" in result
    assert len(result["biens_similaires"]) > 0


def test_similar_properties_respects_top_n():
    result = get_similar_properties(
        code_postal="75015", type_local="Appartement", surface=65.0, nb_pieces=3, top_n=2
    )
    assert result["nb_resultats"] <= 2


def test_similar_properties_no_results():
    """Un code postal inexistant ne doit pas planter."""
    result = get_similar_properties(
        code_postal="99999", type_local="Appartement", surface=65.0, nb_pieces=3
    )
    assert "message" in result or result.get("nb_resultats", 0) == 0


# ============================
# Tests neighborhood_diagnostic
# ============================

def test_neighborhood_returns_dict():
    result = get_neighborhood_diagnostic(code_postal="75015")
    assert isinstance(result, dict)


def test_neighborhood_has_stats():
    result = get_neighborhood_diagnostic(code_postal="75015")
    assert "stats_prix" in result
    assert "nb_transactions" in result
    assert "repartition_types" in result
    assert "evolution_annuelle" in result


def test_neighborhood_prix_median_positive():
    result = get_neighborhood_diagnostic(code_postal="75015")
    assert result["stats_prix"]["prix_median"] > 0


def test_neighborhood_unknown_code_postal():
    """Un code postal inconnu doit retourner une erreur propre."""
    result = get_neighborhood_diagnostic(code_postal="99999")
    assert "erreur" in result
