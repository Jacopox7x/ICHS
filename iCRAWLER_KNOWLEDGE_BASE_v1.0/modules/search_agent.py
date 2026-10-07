import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from collections import Counter

from modules.web_search import search_web


class SearchAgent:
    def __init__(self, cache_ttl_seconds: int = 3600):
        self.cache = {}
        self.cache_ttl = cache_ttl_seconds

    def _cache_key(self, query: str) -> str:
        return query.lower().strip()

    def _get_cached(self, key: str):
        entry = self.cache.get(key)
        if entry and (time.time() - entry['timestamp'] < self.cache_ttl):
            return entry['data']
        return None

    def _set_cache(self, key: str, data):
        self.cache[key] = {'data': data, 'timestamp': time.time()}

    def search(self, query: str, max_results: int = 5) -> Dict:
        """Cerca con cache, restituisce dict con results e images."""
        key = self._cache_key(query)
        cached = self._get_cached(key)
        if cached is not None:
            return cached

        result = search_web(query, max_results=max_results)

        # Normalizza il risultato
        if isinstance(result, dict) and "results" in result:
            normalized = result
        elif isinstance(result, list):
            normalized = {"results": result, "images": []}
        else:
            normalized = {"results": [], "images": []}

        self._set_cache(key, normalized)
        return normalized

    def generate_queries(self, facts: Dict) -> List[str]:
        event = facts.get('event_name', 'evento')
        location = facts.get('location', '')
        topic = facts.get('topic', '')
        date = facts.get('date', '')
        objective = facts.get('objective', '')

        queries = []

        base_query = f"{event} {location} {date}".strip()
        if base_query:
            queries.append(base_query)

        if location and topic:
            queries.append(f"eventi {topic} {location}")
            queries.append(f"{topic} {location} {date}")

        if event:
            queries.append(f"eventi simili a {event}")

        if topic:
            queries.append(f"{topic} tendenze 2026")
            queries.append(f"come organizzare {topic} {location}")

        if objective:
            words = re.findall(r'\b\w{3,}\b', objective)
            if words:
                queries.append(f"strategie per {' '.join(words[:3])} evento")

        # Deduplica
        unique = []
        for q in queries:
            if len(q.split()) > 2 and q not in unique:
                unique.append(q)

        return unique[:6]

    def fetch_all(self, queries: List[str]) -> Dict[str, Dict]:
        results_map = {}
        with ThreadPoolExecutor(max_workers=min(len(queries), 5)) as executor:
            future_to_query = {
                executor.submit(self.search, q, 5): q for q in queries
            }
            for future in as_completed(future_to_query):
                q = future_to_query[future]
                try:
                    result = future.result()
                    if isinstance(result, dict) and "results" in result:
                        results_map[q] = result
                    elif isinstance(result, list):
                        results_map[q] = {"results": result, "images": []}
                    else:
                        results_map[q] = {"results": [], "images": []}
                except Exception as e:
                    print(f"⚠️ Errore per query '{q}': {e}")
                    results_map[q] = {"results": [], "images": []}
        return results_map

    def extract_insights(self, results_map: Dict[str, Dict]) -> Dict:
        all_texts = []
        news = []
        hashtags = set()
        keywords = Counter()
        competitors = set()
        related_events = set()
        all_images = []

        event_keywords = ['evento', 'fiera', 'sagra', 'convegno', 'festival', 'mostra', 'spettacolo']

        for query, data in results_map.items():
            # 🔧 Assicuriamoci che data sia un dict
            if not isinstance(data, dict):
                continue

            results = data.get("results", [])
            images = data.get("images", [])

            if isinstance(images, list):
                all_images.extend(images[:5])

            if not isinstance(results, list):
                continue

            for item in results:
                if not isinstance(item, dict):
                    continue

                title = item.get('title', '')
                content = item.get('content', '')
                url = item.get('url', '')
                pubdate = item.get('pubdate', '')

                full_text = f"{title} {content}".lower()
                all_texts.append(full_text)

                if any(k in full_text for k in event_keywords):
                    news.append({
                        'title': title[:120],
                        'snippet': content[:200],
                        'url': url,
                        'source': url.split('/')[2] if url else 'web',
                        'date': pubdate
                    })

                found = re.findall(r'#\w+', full_text)
                hashtags.update([h[:30] for h in found])

                if 'simile' in query or 'competitor' in query:
                    matches = re.findall(r'([A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+)', title)
                    for m in matches:
                        competitors.add(m)

                if 'eventi' in query or 'fiera' in query:
                    for kw in event_keywords:
                        pattern = rf'([A-Z][a-z]+(?: [A-Z][a-z]+)?)\s+{kw}'
                        for match in re.finditer(pattern, full_text):
                            related_events.add(match.group(0))

        # Keyword frequenti
        stopwords = {'di', 'del', 'della', 'e', 'per', 'con', 'su', 'da', 'il', 'lo', 'la', 'le', 'un', 'una', 'a', 'in'}
        words = re.findall(r'\b[a-z]{3,}\b', ' '.join(all_texts))
        for w in words:
            if w not in stopwords and len(w) > 2:
                keywords[w] += 1

        if len(hashtags) < 3:
            for word, _ in keywords.most_common(5):
                hashtags.add(f"#{word.capitalize()}")

        top_keywords = [w for w, _ in keywords.most_common(10)]
        top_hashtags = list(hashtags)[:10]

        if not news:
            for query, data in results_map.items():
                if not isinstance(data, dict):
                    continue
                for item in data.get("results", [])[:2]:
                    if isinstance(item, dict) and item.get('title') and len(item['title']) > 10:
                        news.append({
                            'title': item['title'][:120],
                            'snippet': item.get('content', '')[:200],
                            'url': item.get('url', ''),
                            'source': 'web'
                        })
                        if len(news) >= 3:
                            break

        unique_images = list(dict.fromkeys(all_images))[:5]

        return {
            'news': news[:5],
            'trending_hashtags': top_hashtags,
            'keywords': top_keywords,
            'competitors': list(competitors)[:3],
            'related_events': list(related_events)[:3],
            'images': unique_images,
            'raw_results': results_map
        }

    def analyze(self, facts: Dict) -> Dict:
        queries = self.generate_queries(facts)
        if not queries:
            print("⚠️ Nessuna query generata")
            return {}
        print(f"🔍 Esecuzione di {len(queries)} query live...")
        results_map = self.fetch_all(queries)
        insights = self.extract_insights(results_map)
        print(f"✅ {len(insights.get('news', []))} notizie, {len(insights.get('trending_hashtags', []))} hashtag, {len(insights.get('images', []))} immagini live")
        return insights


def get_live_insights(facts: Dict) -> Dict:
    agent = SearchAgent()
    return agent.analyze(facts)
