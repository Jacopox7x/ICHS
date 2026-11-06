import asyncio
import os
from dotenv import load_dotenv

load_dotenv(".env.cognee")
import cognee

async def _async_get_context(cliente: str) -> str:
    # Prompt iper-specifico per Qwen: niente inglese, niente "Got it", solo i fatti.
    query = f"Leggi il knowledge graph. Scrivi una descrizione in italiano di {cliente}. Indica 1. Identità, 2. Tono di voce, 3. Target. Massimo 3 frasi. NON rispondere in inglese. NON dire 'Got it'."
    try:
        results = await cognee.search(
            query_text=query,
            query_type=cognee.SearchType.GRAPH_COMPLETION
        )
        if results and isinstance(results[0], dict) and 'search_result' in results[0]:
            testo = results[0]['search_result'][0]
            # Filtro di sicurezza: se risponde "Got it" o è troppo corto, scartiamo
            if len(testo) < 20 or "Got it" in testo:
                return ""
            return testo
        return ""
    except Exception as e:
        print(f"⚠️ Errore Cognee (get_context): {e}")
        return ""

def get_client_context(cliente: str) -> str:
    print(f"🕸️ Interrogo il Knowledge Graph per il cliente: {cliente}...")
    context = asyncio.run(_async_get_context(cliente))
    if context:
        print(f"✅ Contesto trovato da Cognee: {context[:80]}...")
        return f"\nCONTESTO AZIENDALE (da Knowledge Graph):\n{context}\n"
    print("⚠️ Cognee non ha restituito un contesto valido, uso il fallback.")
    return ""
