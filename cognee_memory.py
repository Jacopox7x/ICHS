import asyncio
import os
from dotenv import load_dotenv

load_dotenv(".env.cognee")
import cognee

async def _async_get_context(cliente: str) -> str:
    query = f"Riassumi in massimo 2 frasi chi è {cliente}, qual è il suo tono di voce e a chi si rivolge."
    try:
        results = await cognee.search(
            query_text=query,
            query_type=cognee.SearchType.GRAPH_COMPLETION
        )
        if results and isinstance(results[0], dict) and 'search_result' in results[0]:
            return results[0]['search_result'][0]
        return ""
    except Exception as e:
        print(f"⚠️ Errore Cognee (get_context): {e}")
        return ""

def get_client_context(cliente: str) -> str:
    """Restituisce il contesto del cliente interrogando Cognee."""
    print(f"🕸️ Interrogo il Knowledge Graph per il cliente: {cliente}...")
    context = asyncio.run(_async_get_context(cliente))
    if context:
        print(f"✅ Contesto trovato da Cognee: {context[:80]}...")
        return f"\nCONTESTO AZIENDALE (da Knowledge Graph):\n{context}\n"
    return ""
