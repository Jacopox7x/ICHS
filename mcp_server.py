from fastmcp import FastMCP
import memory

mcp = FastMCP("iCrawler")
_crawler = None
_summarizer = None

def _get_crawler():
    global _crawler
    if _crawler is None:
        from icrawler_simple import ICrawler
        _crawler = ICrawler()
    return _crawler

@mcp.tool
def genera_piano_social(brief: str, cliente: str = "cosper", mode: str = "social") -> str:
    """Genera un piano social a partire da un brief."""
    try:
        return _get_crawler().generate_strategy(brief, mode=mode, sandbox=cliente)
    except Exception as e:
        return f"❌ Errore: {type(e).__name__}: {e}"

@mcp.tool
def cerca_brief_simili(brief: str, cliente: str = "cosper", top_k: int = 2) -> list[dict]:
    """Cerca brief simili nella memoria."""
    try:
        return [{"brief": b[:200], "score": round(float(s), 3)} for b, _, s in memory.find_similar(brief, cliente, top_k)]
    except Exception as e:
        return [{"errore": f"{type(e).__name__}: {e}"}]

if __name__ == "__main__":
    mcp.run()
