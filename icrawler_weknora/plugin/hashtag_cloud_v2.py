"""
Hashtag Cloud per iCrawler v2
- Chiama SearXNG locale per hashtag trending reali
- Fallback su hashtag locali se SearXNG non risponde
- Traccia quali hashtag suggerisce per il loop di apprendimento
"""

import requests
import json
import re
import random
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from pathlib import Path

# Configurazione
SEARXNG_URL = "http://localhost:8888/search"
TRACKING_FILE = Path.home() / "Documents/ICHS/icrawler_weknora/tracking/hashtag_tracking.jsonl"

FALLBACK_HASHTAGS = {
    "food": ["#food", "#cucina", "#ristorante", "#gourmet", "#foodie", "#italianfood"],
    "tech": ["#tech", "#innovazione", "#digitale", "#AI", "#startup", "#future"],
    "cultura": ["#cultura", "#arte", "#mostra", "#museo", "#teatro", "#culturale"],
    "sport": ["#sport", "#fitness", "#competizione", "#allenamento", "#atleta"],
    "moda": ["#moda", "#style", "#fashion", "#outfit", "#tendenza", "#luxury"],
    "musica": ["#musica", "#concerto", "#live", "#artist", "#performance"],
    "beneficenza": ["#beneficenza", "#solidarietà", "#donazioni", "#volontariato"],
    "business": ["#business", "#imprenditoria", "#networking", "#leadership"],
    "networking": ["#networking", "#business", "#crescita", "#professionisti"],
    "sociale": ["#cooperazione", "#terzosettore", "#inclusione", "#comunità", "#solidarietà"],
    "default": ["#evento", "#social", "#community", "#engagement", "#viral"]
}


class HashtagCloud:
    def __init__(self, use_searxng: bool = True, tracking_enabled: bool = True):
        self.use_searxng = use_searxng
        self.tracking_enabled = tracking_enabled
        self.cache: Dict[str, Tuple[List[str], datetime]] = {}
        self.tracking_file = TRACKING_FILE
        if tracking_enabled:
            self.tracking_file.parent.mkdir(parents=True, exist_ok=True)

    def get_hashtags(
        self,
        category: str,
        topic: str = "",
        brief_context: str = ""
    ) -> Dict[str, List[str]]:
        """
        Ottiene hashtag da SearXNG + fallback locale.
        Ritorna dict con:
          - 'live': hashtag da SearXNG (o vuoto)
          - 'fallback': hashtag locali garantiti
          - 'combined': lista finale (deduplicata, max 15)
        """
        live: List[str] = []
        if self.use_searxng:
            live = self._fetch_from_searxng(category, topic) or []

        fallback = self._get_fallback_hashtags(category)
        combined = list(dict.fromkeys(live + fallback))[:15]

        if self.tracking_enabled:
            self._log_suggestion(
                category=category,
                topic=topic,
                brief_context=brief_context,
                live=live,
                fallback=fallback,
                combined=combined,
            )

        return {
            "live": live,
            "fallback": fallback,
            "combined": combined,
        }

    def _fetch_from_searxng(self, category: str, topic: str) -> Optional[List[str]]:
        """Chiama SearXNG per trovare hashtag trending nel settore."""
        try:
            # Query mirata: cerca hashtag trending del settore
            query = f"hashtag trending {category} {topic} instagram 2026"
            response = requests.get(
                SEARXNG_URL,
                params={
                    "q": query,
                    "format": "json",
                    "language": "it-IT",
                },
                timeout=5,
            )
            if response.status_code != 200:
                print(f"⚠️  SearXNG HTTP {response.status_code}")
                return None

            data = response.json()
            hashtags = self._extract_hashtags(data.get("results", []))

            if not hashtags:
                print("⚠️  SearXNG: nessun hashtag estratto")
                return None

            print(f"✅ SearXNG: {len(hashtags)} hashtag live trovati")
            return hashtags

        except requests.exceptions.RequestException as e:
            print(f"⚠️  SearXNG non raggiungibile: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            print(f"⚠️  Errore parsing SearXNG: {e}")
            return None

    def _extract_hashtags(self, results: list) -> List[str]:
        """Estrae hashtag validi da titoli e contenuti dei risultati."""
        # Pattern: # + almeno 3 caratteri alfanumerici
        pattern = re.compile(r'#[A-Za-zÀ-ÿ][A-Za-z0-9_À-ÿ]{2,29}')

        seen = set()
        for r in results[:15]:
            title = r.get("title", "") or ""
            content = r.get("content", "") or ""
            text = f"{title} {content}"
            for tag in pattern.findall(text):
                # Filtro: almeno 4 caratteri totali, non solo numeri
                if len(tag) >= 4 and not tag[1:].isdigit():
                    seen.add(tag.lower())

        return sorted(seen)[:15]

    def _get_fallback_hashtags(self, category: str) -> List[str]:
        """Restituisce hashtag locali di fallback (shuffled)."""
        pool = list(FALLBACK_HASHTAGS.get(category, FALLBACK_HASHTAGS["default"]))
        random.shuffle(pool)
        return pool[:5]

    def inject_into_prompt(
        self,
        brief: str,
        category: str,
        topic: str = ""
    ) -> str:
        """Inietta gli hashtag nel prompt LLM."""
        result = self.get_hashtags(category, topic, brief_context=brief[:200])
        combined = result["combined"]

        if not combined:
            return ""

        hashtag_str = ", ".join(combined)

        return f"""
## HASHTAG AUTORIZZATI
{hashtag_str}

**REGOLA:** Usa SOLO questi hashtag. NON inventarne altri.
Se il brief contiene hashtag specifici, usali AL POSTO di quelli suggeriti.
Se un hashtag suggerito non è pertinente al brief, non usarlo.
"""

    def _log_suggestion(
        self,
        category: str,
        topic: str,
        brief_context: str,
        live: List[str],
        fallback: List[str],
        combined: List[str],
    ) -> None:
        """Registra il suggerimento per il tracking (append a JSONL)."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "topic": topic,
            "brief_context": brief_context,
            "live_hashtags": live,
            "fallback_hashtags": fallback,
            "combined_hashtags": combined,
            "n_live": len(live),
            "n_combined": len(combined),
        }
        try:
            with open(self.tracking_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️  Errore scrittura tracking: {e}")


# ─────────────────────────────────────────────
# Test rapido
# ─────────────────────────────────────────────
if __name__ == "__main__":
    cloud = HashtagCloud(use_searxng=True, tracking_enabled=True)

    print("═" * 50)
    print("TEST HashtagCloud v2 con SearXNG")
    print("═" * 50)

    for category, topic in [
        ("cultura", "evento culturale cooperativa"),
        ("sociale", "inclusione migranti"),
        ("food", "cena solidale"),
    ]:
        print(f"\n📌 Category: {category} | Topic: {topic}")
        result = cloud.get_hashtags(category, topic)

        print(f"   🔴 Live (SearXNG): {len(result['live'])}")
        if result["live"]:
            print(f"      {', '.join(result['live'][:8])}")

        print(f"   🟡 Fallback: {len(result['fallback'])}")
        print(f"      {', '.join(result['fallback'])}")

        print(f"   🟢 Combined: {len(result['combined'])}")
        print(f"      {', '.join(result['combined'])}")

    print("\n" + "═" * 50)
    print(f"📁 Tracking salvato in: {TRACKING_FILE}")
    print("═" * 50)
