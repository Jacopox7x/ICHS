import asyncio
import os
import threading
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(".env.cognee")

try:
    import cognee
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False
    print("⚠️ Cognee non installato o non importabile.")


async def _search_chunks(query: str, dataset: str) -> str:
    """Search CHUNKS (robusto, anche con grafo parziale)."""
    try:
        results = await cognee.search(
            query_text=query,
            datasets=[dataset],
            query_type=cognee.SearchType.CHUNKS,
        )
        if not results:
            return ""
        chunks = []
        for r in results[:3]:
            text = r.get("text", r) if isinstance(r, dict) else str(r)
            text = str(text).strip()
            if text and len(text) > 30:
                chunks.append(text[:600])
        return "\n\n".join(chunks)
    except Exception as e:
        print(f"⚠️ Search CHUNKS fallita: {e}")
        return ""


async def _search_graph_completion(query: str, dataset: str) -> str:
    """Search GRAPH_COMPLETION (più ricco se grafo pronto)."""
    try:
        results = await cognee.search(
            query_text=query,
            datasets=[dataset],
            query_type=cognee.SearchType.GRAPH_COMPLETION,
        )
        if results and isinstance(results[0], dict) and "search_result" in results[0]:
            sr = results[0]["search_result"]
            if isinstance(sr, list) and sr:
                return str(sr[0])
            return str(sr)
        if results and isinstance(results, list):
            return str(results[0])
        return ""
    except Exception as e:
        print(f"⚠️ Search GRAPH_COMPLETION fallita: {e}")
        return ""


async def _get_cognee_context_async(brief: str, cliente: str) -> str:
    """Recupera il contesto del brand dal dataset 'cosper' (o nome cliente lowercase)."""
    if not COGNEE_AVAILABLE:
        return ""

    os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

    dataset = (cliente or "cosper").strip().lower()

    query_chunks = f"linee guida brand {cliente} tono di voce regole divieti"
    context = await _search_chunks(query_chunks, dataset)

    if len(context) < 80:
        query_graph = f"Riassumi chi è {cliente}, il suo tono di voce e gli obiettivi principali."
        graph_ctx = await _search_graph_completion(query_graph, dataset)
        if graph_ctx and len(graph_ctx) > len(context):
            context = graph_ctx

    return context


def _is_in_event_loop() -> bool:
    """True se siamo dentro un event loop in esecuzione (es. FastAPI)."""
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


def get_cognee_context(brief: str, cliente: str) -> str:
    """Restituisce il contesto da Cognee, o stringa vuota se fallisce.
    Thread-safe: usa un thread separato se chiamato dentro un event loop (FastAPI)."""
    print(f"🕸️ Interrogo Cognee per: {cliente}...")
    try:
        if _is_in_event_loop():
            # Siamo dentro FastAPI → thread separato con suo event loop
            result = [""]
            def _runner():
                result[0] = asyncio.run(_get_cognee_context_async(brief, cliente))
            t = threading.Thread(target=_runner)
            t.start()
            t.join()
            context = result[0]
        else:
            # Contesto sincrono (es. CLI)
            context = asyncio.run(_get_cognee_context_async(brief, cliente))

        if context and len(context) > 30:
            print(f"✅ Contesto Cognee trovato ({len(context)} char).")
            return f"[CONTESTO DA COGNEE — dataset '{(cliente or 'cosper').lower()}']\n{context}\n"
        print(f"⚠️ Cognee: nessun contesto trovato per '{cliente}'.")
        return ""
    except Exception as e:
        print(f"⚠️ Timeout o errore Cognee: {e}")
        return ""
