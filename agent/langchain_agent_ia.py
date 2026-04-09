"""
Agent IA — Utilise Mistral via LangChain pour répondre aux questions immobilières.
Se connecte au serveur MCP, récupère les tools, et laisse l'agent décider lequel appeler.
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from llm_agent import PROMPT_SYSTEM, llm_model
from client_mcp import get_mcp_client

# Charger les variables d'environnement
load_dotenv()

# ----- enable automated tracing of your model calls, set the LangSmith API key ------
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
if "LANGSMITH_API_KEY" not in os.environ:
   raise ValueError("La variable d'environnement LANGSMITH_API_KEY est introuvable.")
os.environ["LANGSMITH_TRACING"] = "true"

async def run_agent():
    """Fonction principale de l'agent IA."""
   
    # 1. set le llm_model et le prompt system pour l'agent
    llm = llm_model
    
    # 2. Set les tools en récupérant les tools du serveur MCP via le client
    mcp_client = get_mcp_client()

    # 3.Récupérer les tools du serveur MCP convertis en tools LangChain
    tools = await mcp_client.get_tools()
    print(f"tools récupérés du serveur MCP : {[t.name for t in tools]}")

    # 4. Créer l'agent LangChain
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=PROMPT_SYSTEM
    )

    print("\n===Agent immobilier IA prêt à répondre aux questions===")
    print("Posez vos questions sur l'immobilier (tapez 'quit', 'exit' ou 'quitter')\n")
    
    # 5. Boucle de conversation avec l'utilisateur
    while True:
        user_input = input("\nVous: ")
        if user_input.lower() in ["quit", "exit", "quitter"]:
            print("Fin de la conversation. Au revoir!")
            break
        
        # 6. Envoyer la question de l'utilisateur à l'agent,
        # laisser l'agent décider quel tool utiliser et générer une réponse
        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": user_input}]}
        )

        # 7. Afficher la réponse de l'agent
        last_message = response["messages"][-1].content
        print(f"\nAgent IA: {last_message}\n")

# point d'entrée
if __name__ == "__main__":
    asyncio.run(run_agent())
