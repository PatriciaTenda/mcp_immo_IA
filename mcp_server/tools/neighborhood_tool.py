import json
from mcp_immo_IA.mcp_server.services.neighborhood_diag import diagnose_neighborhood


def get_neighborhood_diagnostic(code_postal: str) -> str:
    """
    Tool MCP : Diagnostic immobilier complet d'un quartier.
    """
    diagnostic = diagnose_neighborhood(code_postal=code_postal)

    return json.dumps(diagnostic, ensure_ascii=False, default=str)