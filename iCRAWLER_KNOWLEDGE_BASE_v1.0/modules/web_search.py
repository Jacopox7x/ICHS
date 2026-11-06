import requests
import os
from typing import List, Dict
import re

USER_AGENT = "Mozilla/5.0 (compatible; iCrawler/1.0)"

# Tavily API
TAVILY_URL = "https://api.tavily.com/search"
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "keyless")

def search_web(query: str, max_results: int = 10) -> Dict:
    """
    Cerca su Tavily (con chiave o keyless) o fallback DuckDuckGo
    Restituisce: {"results": [...], "images": [...]}
    """
    # Prova Tavily
    result = _tavily_search(query, max_results)
    if result and result.get("results"):
        return result
    
    # Fallback DuckDuckGo
    print("ℹ️ Uso fallback DuckDuckGo")
    duck_results = _duckduckgo_search(query, max_results)
    return {"results": duck_results, "images": []}

def _tavily_search(query: str, max_results: int = 5) -> Dict:
    """
    Ricerca su Tavily API con supporto immagini
    """
    try:
        payload = {
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_images": True      # <-- ATTIVA LE IMMAGINI
        }
        
        if TAVILY_API_KEY == "keyless":
            headers = {
                "Content-Type": "application/json",
                "X-Tavily-Access-Mode": "keyless"
            }
            print("🔍 Ricerca Tavily (keyless)...")
        else:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TAVILY_API_KEY}"
            }
            print("🔍 Ricerca Tavily (con chiave)...")
        
        r = requests.post(
            TAVILY_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if r.status_code == 200:
            data = r.json()
            results = []
            for item in data.get("results", [])[:max_results]:
                results.append({
                    "title": item.get("title", "Senza titolo"),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "pubdate": "",
                    "score": item.get("score", 0)
                })
            images = data.get("images", [])[:5]  # Max 5 immagini
            if results:
                print(f"✅ {len(results)} risultati, {len(images)} immagini da Tavily")
                return {"results": results, "images": images}
            else:
                print("⚠️ Nessun risultato da Tavily")
                return {"results": [], "images": []}
        else:
            print(f"⚠️ Tavily: {r.status_code}")
            return {"results": [], "images": []}
            
    except Exception as e:
        print(f"⚠️ Tavily: {e}")
        return {"results": [], "images": []}

def _duckduckgo_search(query: str, max_results: int) -> List[Dict]:
    """
    Fallback: ricerca su DuckDuckGo
    """
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            results = []
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", query),
                    "url": data.get("AbstractURL", ""),
                    "content": data.get("AbstractText", "")
                })
            for topic in data.get("RelatedTopics", [])[:max_results-1]:
                if "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:80],
                        "url": topic.get("FirstURL", ""),
                        "content": topic.get("Text", "")
                    })
            return results
        return []
    except:
        return []

def get_trending_hashtags(topic: str, limit: int = 5) -> List[str]:
    """
    Genera hashtag da topic + risultati di ricerca
    """
    # Cerca hashtag nel contenuto dei risultati
    result = search_web(f"{topic} hashtag", max_results=10)
    results = result.get("results", [])
    hashtags = []
    for r in results:
        content = r.get("content", "") + r.get("title", "")
        found = re.findall(r'#\w+', content)
        hashtags.extend(found[:2])

    # Se non trova, genera da topic
    if not hashtags:
        words = re.findall(r'[A-Za-z]{3,}', topic)
        if not words:
            return ['#Evento', '#Innovazione', '#2026']
        base = ''.join(w.capitalize() for w in words[:2])
        hashtags = [f'#{base}', f'#{base}2026', f'#{base}Event']

    # Deduplica e limita
    seen = set()
    unique = []
    for h in hashtags:
        if h not in seen:
            seen.add(h)
            unique.append(h)
    return unique[:limit]
