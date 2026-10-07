"""
iCrawler - Inspiration Research Tool
====================================
NON genera hashtag. Trova ispirazione da cooperative, enti e contesti reali.
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import re
from typing import List, Dict
from datetime import datetime
from pathlib import Path

SEARXNG_URL = "http://localhost:8888/search"
RESEARCH_LOG = Path.home() / "Documents/ICHS/icrawler_weknora/tracking/research_log.jsonl"


class InspirationResearch:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        RESEARCH_LOG.parent.mkdir(parents=True, exist_ok=True)

    def find_similar_coops(self, topic: str, location: str = "italia", max_results: int = 10) -> Dict:
        query = f"cooperativa sociale {topic} {location} instagram"
        results = self._search(query, max_results)
        all_text = " ".join(f"{r.get('title','')} {r.get('content','')}" for r in results)
        hashtags = self._extract_hashtags(all_text)
        output = {
            "type": "similar_coops",
            "query": query,
            "topic": topic,
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "hashtags_trovati": hashtags,
        }
        self._log(output)
        return output

    def find_local_hashtags(self, city: str, topic: str = "", max_results: int = 10) -> Dict:
        if topic:
            query = f"hashtag instagram #{city} {topic}"
        else:
            query = f"hashtag instagram #{city}"
        results = self._search(query, max_results)
        all_text = " ".join(f"{r.get('title','')} {r.get('content','')}" for r in results)
        hashtags = self._extract_hashtags(all_text)
        city_lower = city.lower()
        local_hashtags = [tag for tag in hashtags if city_lower in tag.lower()]
        output = {
            "type": "local_hashtags",
            "query": query,
            "city": city,
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "hashtags_locali": local_hashtags,
            "hashtags_altri": [h for h in hashtags if h not in local_hashtags],
            "results": results,
        }
        self._log(output)
        return output

    def find_viral_events(self, topic: str, max_results: int = 10) -> Dict:
        query = f"evento {topic} virale instagram successo cooperativa"
        results = self._search(query, max_results)
        all_text = " ".join(f"{r.get('title','')} {r.get('content','')}" for r in results)
        hashtags = self._extract_hashtags(all_text)
        formati = self._detect_formats(all_text)
        output = {
            "type": "viral_events",
            "query": query,
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "examples": results,
            "hashtags_usati": hashtags,
            "formati_suggeriti": formati,
        }
        self._log(output)
        return output

    def analyze_coop_social(self, coop_name: str, max_results: int = 10) -> Dict:
        query = f'"{coop_name}" instagram OR facebook OR linkedin'
        results = self._search(query, max_results)
        all_text = " ".join(f"{r.get('title','')} {r.get('content','')}" for r in results)
        hashtags = self._extract_hashtags(all_text)
        platforms = []
        for p in ["instagram", "facebook", "linkedin", "tiktok", "youtube"]:
            if p in all_text.lower():
                platforms.append(p)
        output = {
            "type": "coop_analysis",
            "query": query,
            "coop_name": coop_name,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "platforms": platforms,
            "hashtags": hashtags,
        }
        self._log(output)
        return output

    def _search(self, query: str, max_results: int = 10) -> List[Dict]:
        try:
            params = urllib.parse.urlencode({"q": query, "format": "json"})
            url = f"{SEARXNG_URL}?{params}"
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                if response.status != 200:
                    print(f"WARN SearXNG HTTP {response.status}")
                    return []
                data = json.loads(response.read().decode("utf-8"))
            raw = data.get("results", [])[:max_results]
            return [self._clean_result(r) for r in raw]
        except urllib.error.URLError as e:
            print(f"WARN SearXNG non raggiungibile: {e}")
            return []
        except (KeyError, json.JSONDecodeError) as e:
            print(f"WARN Errore parsing: {e}")
            return []

    def _clean_result(self, raw: Dict) -> Dict:
        return {
            "title": (raw.get("title") or "").strip(),
            "url": raw.get("url") or "",
            "content": (raw.get("content") or "").strip()[:300],
            "engine": raw.get("engine") or "",
        }

    def _extract_hashtags(self, text: str) -> List[str]:
        pattern = re.compile(r'#[A-Za-z\u00C0-\u00FF][A-Za-z0-9_\u00C0-\u00FF]{2,29}')
        seen = set()
        for tag in pattern.findall(text):
            seen.add(tag.lower())
        return sorted(seen)

    def _detect_formats(self, text: str) -> List[str]:
        text_lower = text.lower()
        formats = []
        mapping = {
            "reel": "Reel/Video breve",
            "carousel": "Carousel",
            "carosello": "Carousel",
            "stories": "Stories",
            "story": "Stories",
            "live": "Live",
            "video": "Video",
        }
        for keyword, format_name in mapping.items():
            if keyword in text_lower and format_name not in formats:
                formats.append(format_name)
        return formats

    def _log(self, output: Dict) -> None:
        log_entry = {
            "timestamp": output["timestamp"],
            "type": output["type"],
            "query": output["query"],
            "n_results": len(output.get("results", [])),
        }
        for key in ["hashtags_trovati", "hashtags_locali", "hashtags_usati", "hashtags"]:
            if key in output:
                log_entry[key] = output[key]
                break
        try:
            with open(RESEARCH_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"WARN errore log: {e}")


def _print_results(results: List[Dict], limit: int = 5) -> None:
    for i, r in enumerate(results[:limit], 1):
        print(f"   [{i}] {r['title'][:80]}")
        if r["content"]:
            print(f"       {r['content'][:120]}...")
        if r["url"]:
            print(f"       {r['url']}")
        print()


if __name__ == "__main__":
    research = InspirationResearch()

    print("=" * 70)
    print("TEST Inspiration Research Tool")
    print("=" * 70)

    print()
    print("-" * 70)
    print("TEST 1: find_similar_coops")
    print("-" * 70)
    print("Cerco: cooperative sociali che comunicano 'inclusione migranti' in Italia")
    print()
    result = research.find_similar_coops("inclusione migranti", location="italia")
    print(f"Trovati {len(result['results'])} risultati")
    print(f"Hashtag menzionati: {len(result['hashtags_trovati'])}")
    if result["hashtags_trovati"]:
        print(f"   {', '.join(result['hashtags_trovati'][:15])}")
    print()
    print("Prime 5 fonti:")
    _print_results(result["results"])

    print()
    print("-" * 70)
    print("TEST 2: find_local_hashtags")
    print("-" * 70)
    print("Cerco: hashtag locali per Cremona + cultura")
    print()
    result = research.find_local_hashtags("cremona", "cultura")
    print(f"Hashtag locali trovati: {len(result['hashtags_locali'])}")
    if result["hashtags_locali"]:
        print(f"   {', '.join(result['hashtags_locali'])}")
    print(f"Altri hashtag: {len(result['hashtags_altri'])}")
    print()
    print("Prime 5 fonti:")
    _print_results(result["results"])

    print()
    print("-" * 70)
    print("TEST 3: find_viral_events")
    print("-" * 70)
    print("Cerco: esempi di cene solidali di successo")
    print()
    result = research.find_viral_events("cena solidale")
    print(f"Trovati {len(result['examples'])} esempi")
    print(f"Hashtag usati: {len(result['hashtags_usati'])}")
    if result["hashtags_usati"]:
        print(f"   {', '.join(result['hashtags_usati'][:15])}")
    print(f"Formati rilevati: {result['formati_suggeriti']}")
    print()
    print("Prime 5 fonti:")
    _print_results(result["examples"])

    print()
    print("=" * 70)
    print(f"Log: {RESEARCH_LOG}")
    print("=" * 70)
