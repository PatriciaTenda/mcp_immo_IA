import json
from mcp_server.services.similar_properties import find_similar_properties


def get_similar_properties(
    code_postal: str,
    type_local: str,
    surface: float,
    nb_pieces: int,
    top_n: int = 5
) -> str:
    """
    Tool MCP : Trouve les biens similaires récemment vendus.
    """
    results = find_similar_properties(
        code_postal=code_postal,
        type_local=type_local,
        surface=surface,
        nb_pieces=nb_pieces,
        top_n=top_n
    )

    if not results:
        return json.dumps({"message": "Aucun bien similaire trouvé pour ces critères."}, ensure_ascii=False)

    return json.dumps({
        "nb_resultats": len(results),
        "biens_similaires": results
    }, ensure_ascii=False)