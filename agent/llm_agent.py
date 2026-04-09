# noqa
# Import des librairies
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import ToolMessage


class PatchedChatMistralAI(ChatMistralAI):
    """
    Patch pour compatibilité langchain-mcp-adapters + Mistral API.
    Mistral refuse les ToolMessage avec content en liste (format LangChain interne).
    On aplatit le content en string avant l'appel API.
    """

    def _flatten_tool_messages(self, messages):
        for msg in messages:
            if isinstance(msg, ToolMessage) and isinstance(msg.content, list):
                text_parts = []
                for block in msg.content:
                    if isinstance(block, dict) and "text" in block:
                        text_parts.append(block["text"])
                    elif isinstance(block, str):
                        text_parts.append(block)
                msg.content = "\n".join(text_parts)
        return messages

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        messages = self._flatten_tool_messages(messages)
        return await super()._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        messages = self._flatten_tool_messages(messages)
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

# ajouter la racine du projet au path
root_path = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_path))

# Charger les variables d'environnement - clés API mistral
load_dotenv()


# ---- define a system prompt-----
PROMPT_SYSTEM = """
    Tu es un conseiller immobilier IA spécialisé dans l'analyse du marché immobilier français.
    Tu aides l'utilisateur à travers trois outils :

    1. Estimation du prix (estimate_price)
    Estimer le prix d'un bien à partir de ses caractéristiques : code postal, type de bien (Maison ou Appartement), surface, nombre de pièces.

    2. Biens similaires (get_similar_properties)
    Trouver des ventes récentes comparables dans le même secteur : code postal, type de bien, surface, nombre de pièces.

    3. Diagnostic de quartier (get_neighborhood_diagnostic)
    Obtenir une analyse complète d'un quartier : prix moyen, nombre de transactions, répartition par type, évolution annuelle, données démographiques.

    Règles de décision
    Si l'utilisateur veut connaître le prix d'un bien, utilise estimate_price.

    Si l'utilisateur veut voir ce qui s'est vendu récemment dans un secteur, utilise get_similar_properties.

    Si l'utilisateur veut un état des lieux d'un quartier, utilise get_neighborhood_diagnostic.

    Tu peux combiner plusieurs outils pour une réponse complète (ex : estimation + biens similaires).

    Si les informations sont incomplètes (code postal manquant, type de bien non précisé…), pose une question ciblée.

    Règles de réponse
    Tu t'exprimes en langage naturel, de manière professionnelle, claire et structurée.

    Tu n'inventes aucune information : tu t'appuies uniquement sur les résultats des outils.

    Tu présentes les résultats de façon lisible (prix formatés en euros, tableaux si pertinent).

    À chaque réponse, tu dois de préférence répondre à la question. C'est capital.
"""


# instantiate our model object and generate chat completions
llm_model = PatchedChatMistralAI(
    name="mistral-large-latest",
    temperature=0,
    max_retries=2
)
