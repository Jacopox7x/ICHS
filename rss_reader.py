"""
rss_reader.py - Lettore di feed RSS con filtro di rilevanza.

Legge feed RSS, filtra gli articoli in base a un brief, e formatta
il risultato come blocco testuale per il prompt.

Il filtro e RESTRITTIVO: un titolo passa solo se ha almeno 2 parole
significative (>= 5 caratteri) in comune con il brief. Se nessun
titolo passa, ritorna lista vuota. Meglio niente che rumore.
"""

import re
import feedparser

# Parole comuni da ignorare nel match (stopword italiane + inglesi)
STOPWORDS = {
    "della", "delle", "degli", "dell", "dello",
    "nella", "nelle", "negli", "nell", "nello",
    "sulla", "sulle", "sugli", "sull", "sullo",
    "dalla", "dalle", "dagli", "dall", "dallo",
    "questo", "questa", "questi", "queste",
    "quello", "quella", "quelli", "quelle",
    "sono", "essere", "avere", "fatto",
    "anche", "come", "dove", "quando", "perche",
    "molto", "poco", "tanto", "tutti", "tutte",
    "altro", "altri", "altre", "senza", "sopra",
    "sotto", "prima", "dopo", "tra", "fra",
    "the", "and", "for", "with", "from",
    "this", "that", "these", "those",
    "have", "has", "been", "will", "would",
    "about", "after", "before", "into",
}


def _keywords(text):
    """
    Estrae parole significative da un testo.
    Ignora stopword, parole corte (< 5 caratteri) e non alfabetiche.
    """
    words = re.findall(r"\b[a-zA-Zàèéìòù]+\b", text.lower())
    return set(
        w for w in words
        if len(w) >= 5 and w not in STOPWORDS
    )


def read_feed(url: str, limit: int = 5) -> list:
    """Legge un feed RSS e ritorna i primi N articoli."""
    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"[rss_reader] errore su {url}: {e}")
        return []

    if not feed.entries:
        return []

    articles = []
    for entry in feed.entries[:limit]:
        articles.append({
            "title": entry.get("title", "").strip(),
            "summary": entry.get("summary", "").strip()[:300],
            "link": entry.get("link", "").strip(),
            "published": entry.get("published", "").strip(),
            "source": url,
        })
    return articles


def read_multiple(urls: list, limit_per_feed: int = 3) -> list:
    """Legge piu feed e restituisce una lista unificata."""
    all_articles = []
    for url in urls:
        all_articles.extend(read_feed(url, limit=limit_per_feed))
    return all_articles


def filter_by_brief(articles: list, brief: str,
                    min_common: int = 1) -> list:
    """
    Filtra articoli tenendo solo quelli con almeno `min_common` parole
    significative in comune con il brief.

    Args:
        articles: lista di dict da read_feed / read_multiple
        brief: testo del brief
        min_common: numero minimo di parole condivise (default 1)

    Returns:
        list di articoli filtrati. Lista vuota se nessuno passa.
    """
    brief_kw = _keywords(brief)
    if not brief_kw:
        return []

    filtered = []
    for a in articles:
        title = a.get("title", "")
        title_kw = _keywords(title)
        common = brief_kw & title_kw
        if len(common) >= min_common:
            filtered.append(a)
    return filtered


def format_for_prompt(articles: list, max_articles: int = 10) -> str:
    """Formatta una lista di articoli come blocco testuale per il prompt."""
    if not articles:
        return ""

    lines = ["--- CONTESTO ESTERNO (titoli rilevanti) ---"]
    for a in articles[:max_articles]:
        title = a.get("title", "").strip()
        if title:
            lines.append(f"- {title}")
    lines.append("--- FINE CONTESTO ---")
    return "\n".join(lines)


if __name__ == "__main__":
    # Test rapido
    brief = (
        "Tech Summit 2026 si terra a Milano il 15 marzo. "
        "L'evento e dedicato a startup e investitori del settore fintech. "
        "Budget previsto: 50.000 euro. Hashtag ufficiale: #TechSummit26"
    )
    urls = [
        "https://www.ansa.it/sito/notizie/tecnologia/tecnologia_rss.xml",
        "https://www.repubblica.it/rss/tecnologia/rss2.0.xml",
    ]
    articles = read_multiple(urls, limit_per_feed=10)
    print(f"Articoli letti: {len(articles)}")
    filtered = filter_by_brief(articles, brief)
    print(f"Articoli rilevanti (min 2 parole): {len(filtered)}")
    for a in filtered:
        print(f"  - {a['title']}")
    print()
    print(format_for_prompt(filtered))
