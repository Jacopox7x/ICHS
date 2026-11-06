from typing import List
import time

def get_hashtags(topic: str, limit: int = 7) -> List[str]:
    """Recupera hashtag popolari da Google Trends (PyTrends) con fallback statico."""
    
    # 1. Prova PyTrends
    try:
        from pytrends.request import TrendReq
        # Aggiungi un ritardo per evitare il rate limit
        time.sleep(1)
        
        pytrends = TrendReq(hl='it-IT', tz=360)
        pytrends.build_payload(kw_list=[topic], timeframe='now 7-d')
        related = pytrends.related_queries()
        
        if topic in related and related[topic] is not None:
            top = related[topic]['top']
            if top is not None and not top.empty:
                hashtags = []
                for query in top['query'].head(limit).tolist():
                    if isinstance(query, str):
                        if not query.startswith('#'):
                            hashtags.append(f"#{query}")
                        else:
                            hashtags.append(query)
                if hashtags:
                    print(f"✅ Hashtag live da Google Trends: {hashtags}")
                    return hashtags
    except Exception as e:
        print(f"⚠️ Errore PyTrends: {e}")
    
    # 2. Fallback statico
    print("🔄 Uso fallback statico")
    base = topic.lower().replace(" ", "")
    return [
        f"#{base}",
        f"#{base}Day",
        f"#{base}Life",
        f"#{base}Style",
        f"#{base}Vibes",
        f"#{base}Love",
        f"#{base}Time",
    ]
