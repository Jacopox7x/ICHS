import logging
import requests
from knowledge_base import get_context_for_brief
from cognee_manager import get_cognee_context

logger = logging.getLogger(__name__)

SEARXNG_URL = "http://127.0.0.1:8888/search"

def _search_searxng(query: str, max_results: int = 3) -> str:
    """Esegue una ricerca web tramite SearXNG locale."""
    try:
        response = requests.get(
            SEARXNG_URL,
            params={"q": query, "format": "json", "language": "it"},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        if not results:
            return ""
            
        # Formattiamo i primi risultati
        formatted = []
        for r in results[:max_results]:
            title = r.get("title", "")
            content = r.get("content", "")
            url = r.get("url", "")
            formatted.append(f"- {title}: {content} (Fonte: {url})")
            
        return "\n".join(formatted)
    except Exception as e:
        logger.warning(f"⚠️ SearXNG non disponibile: {e}")
        return ""

def retrieve_context(brief: str, cliente: str = "cosper", usa_contesto: bool = True) -> dict:
    """
    Cascading RAG con gerarchia:
    1. Cognee (Knowledge Graph avanzato)
    2. SearXNG (Ricerca Web Locale)
    3. Memoria Locale (SQLite)
    """
    if not usa_contesto:
        return {"fonte": "nessuna", "risultati": [], "percorso": "contesto_disattivato"}

    # 1. Cognee
    cognee_ctx = get_cognee_context(brief, cliente)
    if cognee_ctx:
        return {
            "fonte": "cognee",
            "risultati": [{"testo": cognee_ctx}],
            "percorso": "cognee_rag"
        }

    # 2. SearXNG (Web)
    logger.info("🌐 Cognee non disponibile, provo SearXNG...")
    web_ctx = _search_searxng(brief)
    if web_ctx:
        return {
            "fonte": "web",
            "risultati": [{"testo": web_ctx}],
            "percorso": "searxng_rag"
        }

    # 3. Memoria Locale (SQLite)
    local_ctx = get_context_for_brief(brief, cliente)
    if local_ctx:
        return {
            "fonte": "locale",
            "risultati": [{"testo": local_ctx}],
            "percorso": "memoria_locale"
        }

    # Nessun risultato
    return {
        "fonte": "nessuna",
        "risultati": [],
        "percorso": "nessun_risultato"
    }


def get_trending_hashtags(query: str) -> str:
    """Estrae e filtra gli hashtag di tendenza tramite SearXNG."""
    import re
    try:
        search_query = f"hashtag trending {query} site:instagram.com OR site:tiktok.com"
        results = _search_searxng(search_query, max_results=5)
        
        if not results or "Nessun risultato" in results:
            return "Nessun hashtag specifico trovato."
            
        hashtags = re.findall(r'#\w+', results)
        
        if hashtags:
            unique_hashtags = list(dict.fromkeys(hashtags))
            
            # Lista nera degli hashtag spazzatura più comuni
            blacklist = ['#follow', '#like', '#instagood', '#f4f', '#l4l', '#follow4follow', '#like4like', '#viral', '#trending', '#explore', '#love', '#photooftheday']
            
            valid_hashtags = [h for h in unique_hashtags if h.lower() not in blacklist and len(h) > 4]
            
            if valid_hashtags:
                return ", ".join(valid_hashtags[:8])
            
        return "Nessun hashtag pertinente trovato."
    except Exception as e:
        return f"Errore ricerca hashtag: {str(e)}"
