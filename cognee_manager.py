import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Carichiamo le variabili d'ambiente per Cognee
load_dotenv(".env.cognee")

try:
    import cognee
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False
    print("⚠️ Cognee non installato o non importabile.")

async def _get_cognee_context_async(brief: str, cliente: str) -> str:
    if not COGNEE_AVAILABLE:
        return ""
    try:
        # Disattiviamo i test di connessione che causano timeout
        os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"
        
        query = f"Riassumi in massimo 2 frasi chi è {cliente}, qual è il suo tono di voce e quali sono i suoi obiettivi principali."
        results = await cognee.search(
            query_text=query,
            query_type=cognee.SearchType.GRAPH_COMPLETION
        )
        
        if results and isinstance(results[0], dict) and 'search_result' in results[0]:
            return results[0]['search_result'][0]
        return ""
    except Exception as e:
        print(f"⚠️ Errore Cognee: {e}")
        return ""

def get_cognee_context(brief: str, cliente: str) -> str:
    """Restituisce il contesto da Cognee, o stringa vuota se fallisce."""
    print(f"🕸️ Interrogo Cognee per: {cliente}...")
    try:
        # Usiamo asyncio.run in modo sicuro
        context = asyncio.run(_get_cognee_context_async(brief, cliente))
        if context and len(context) > 20:
            print(f"✅ Contesto Cognee trovato.")
            return f"[CONTESTO DA COGNEE]\n{context}\n"
        return ""
    except Exception as e:
        print(f"⚠️ Timeout o errore Cognee: {e}")
        return ""
