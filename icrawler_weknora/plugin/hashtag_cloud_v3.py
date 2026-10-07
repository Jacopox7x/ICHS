"""
Hashtag Cloud per iCrawler v3
- SearXNG per hashtag live, MA con filtri anti-rumore
- Blacklist hashtag generici/irrilevanti
- Whitelist hashtag "core" per categoria (garantisce output sensato)
- Filtro di coerenza semantica
- Tracking JSONL per il loop di apprendimento
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import re
import random
from typing import List, Optional, Dict, Tuple, Set
from datetime import datetime
from pathlib import Path

SEARXNG_URL = "http://localhost:8888/search"
TRACKING_FILE = Path.home() / "Documents/ICHS/icrawler_weknora/tracking/hashtag_tracking.jsonl"

FALLBACK_HASHTAGS = {
    "food": ["#food", "#cucina", "#ristorante", "#gourmet", "#foodie", "#italianfood"],
    "tech": ["#tech", "#innovazione", "#digitale", "#AI", "#startup", "#future"],
    "cultura": ["#cultura", "#arte", "#mostra", "#museo", "#teatro", "#culturale"],
    "sport": ["#sport", "#fitness", "#competizione", "#allenamento", "#atleta"],
    "moda": ["#moda", "#style", "#fashion", "#outfit", "#tendenza", "#luxury"],
    "musica": ["#musica", "#concerto", "#live", "#artist", "#performance"],
    "beneficenza": ["#beneficenza", "#solidarieta", "#donazioni", "#volontariato"],
    "business": ["#business", "#imprenditoria", "#networking", "#leadership"],
    "networking": ["#networking", "#business", "#crescita", "#professionisti"],
    "sociale": ["#cooperazione", "#terzosettore", "#inclusione", "#comunita", "#solidarieta"],
    "default": ["#evento", "#social", "#community", "#engagement"]
}

BLACKLIST = {
    "#fyp", "#viral", "#explore", "#explorepage", "#trending", "#foryou",
    "#foryoupage", "#follow", "#followme", "#like", "#likeforlike",
    "#instagood", "#photooftheday", "#picoftheday", "#instadaily",
    "#bhfyp", "#reels", "#reelsinstagram", "#reelsvideo", "#reelitfeelit",
    "#love", "#instalove", "#amor", "#amore", "#beautiful", "#favorite",
    "#happy", "#cute", "#life", "#lifestyle", "#motivation",
    "#bali", "#balinese", "#brasil", "#brazil", "#usa", "#uk",
    "#fashionfood", "#fitnessmotivation", "#fitness", "#workout",
    "#bodybuilding", "#weightloss", "#diet", "#keto",
    "#eat", "#eating", "#delish", "#delicious", "#breakfast",
    "#college", "#collegefest", "#collegefestival", "#collegelife",
    "#bird", "#birds", "#cat", "#cats", "#dog", "#dogs",
    "#alibi", "#freakedout", "#covid",
    "#nba", "#nfl", "#soccer", "#football",
}

COHERENCE_KEYWORDS = {
    "cultura": ["cultur", "art", "arte", "mostr", "muse", "teatr", "libr", "cinem", "music", "stori", "patrimon", "festival"],
    "sociale": ["social", "inclus", "migran", "comun", "cooper", "solidar", "diritt", "accogli", "integraz", "volontar", "terzosettore", "ong"],
    "food": ["food", "cucin", "cibo", "ristor", "gust", "sapor", "ricett", "italian", "tradiz", "bio", "km0", "solidal"],
    "tech": ["tech", "digit", "innov", "startup", "ai", "softwar", "dat", "code", "future"],
    "sport": ["sport", "fitness", "allen", "competi", "atlet", "corr", "calci", "basket"],
    "musica": ["music", "concert", "live", "artist", "band", "song", "perform"],
    "beneficenza": ["benefic", "solidar", "donaz", "volontar", "charity", "aiut", "sostegn"],
    "business": ["business", "imprend", "network", "leadership", "market", "aziend"],
    "networking": ["network", "business", "cresc", "profession", "event", "incontr"],
    "moda": ["moda", "style", "fashion", "outfit", "tendenz", "abbigliam"],
    "default": [],
}

MIN_HASHTAG_LENGTH = 4
MAX_HASHTAG_LENGTH = 30
MIN_ALPHA_RATIO = 0.5
MAX_LIVE_HASHTAGS = 8
TOTAL_TARGET = 12


class HashtagCloud:
    def __init__(self, use_searxng=True, tracking_enabled=True):
        self.use_searxng = use_searxng
        self.tracking_enabled = tracking_enabled
        self.tracking_file = TRACKING_FILE
        if tracking_enabled:
            self.tracking_file.parent.mkdir(parents=True, exist_ok=True)

    def get_hashtags(self, category, topic="", brief_context=""):
        live_raw = []
        if self.use_searxng:
            live_raw = self._fetch_from_searxng(category, topic) or []

        live_filtered, filter_stats = self._filter_hashtags(live_raw, category)
        live_filtered = live_filtered[:MAX_LIVE_HASHTAGS]

        core = self._get_core_hashtags(category)
        combined = self._merge_unique(core + live_filtered, TOTAL_TARGET)

        if self.tracking_enabled:
            self._log_suggestion(category, topic, brief_context,
                                 live_raw, live_filtered, core, combined, filter_stats)

        return {
            "live": live_filtered,
            "core": core,
            "combined": combined,
            "stats": {
                "live_raw": len(live_raw),
                "live_filtered": len(live_filtered),
                "core": len(core),
                "combined": len(combined),
                **filter_stats,
            },
        }

    def _fetch_from_searxng(self, category, topic):
        try:
            query = f"hashtag instagram {category} {topic} italia"
            params = urllib.parse.urlencode({"q": query, "format": "json"})
            url = f"{SEARXNG_URL}?{params}"
            with urllib.request.urlopen(url, timeout=8) as response:
                if response.status != 200:
                    print(f"WARN SearXNG HTTP {response.status}")
                    return None
                data = json.loads(response.read().decode("utf-8"))
            return self._extract_hashtags(data.get("results", []))
        except urllib.error.URLError as e:
            print(f"WARN SearXNG non raggiungibile: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            print(f"WARN Errore parsing SearXNG: {e}")
            return None

    def _extract_hashtags(self, results):
        pattern = re.compile(r"#[A-Za-z\u00C0-\u00FF][A-Za-z0-9_\u00C0-\u00FF]{2,29}")
        seen = set()
        for r in results[:15]:
            title = r.get("title", "") or ""
            content = r.get("content", "") or ""
            text = f"{title} {content}"
            for tag in pattern.findall(text):
                seen.add(tag.lower())
        return sorted(seen)

    def _filter_hashtags(self, hashtags, category):
        stats = {
            "rejected_blacklist": 0,
            "rejected_length": 0,
            "rejected_alpha": 0,
            "rejected_coherence": 0,
        }
        keywords = COHERENCE_KEYWORDS.get(category, [])
        filtered = []
        for tag in hashtags:
            if tag in BLACKLIST:
                stats["rejected_blacklist"] += 1
                continue
            if len(tag) < MIN_HASHTAG_LENGTH or len(tag) > MAX_HASHTAG_LENGTH:
                stats["rejected_length"] += 1
                continue
            alpha_count = sum(1 for c in tag[1:] if c.isalnum())
            if len(tag) > 1 and alpha_count / (len(tag) - 1) < MIN_ALPHA_RATIO:
                stats["rejected_alpha"] += 1
                continue
            if keywords:
                tag_lower = tag.lower()
                if not any(kw in tag_lower for kw in keywords):
                    stats["rejected_coherence"] += 1
                    continue
            filtered.append(tag)
        return filtered, stats

    def _get_core_hashtags(self, category):
        pool = list(FALLBACK_HASHTAGS.get(category, FALLBACK_HASHTAGS["default"]))
        random.shuffle(pool)
        return pool

    def _merge_unique(self, items, limit):
        seen = set()
        result = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
                if len(result) >= limit:
                    break
        return result

    def _log_suggestion(self, category, topic, brief_context,
                        live_raw, live_filtered, core, combined, filter_stats):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "version": "v3",
            "category": category,
            "topic": topic,
            "brief_context": brief_context[:200],
            "live_raw_count": len(live_raw),
            "live_filtered_count": len(live_filtered),
            "core_count": len(core),
            "combined": combined,
            "live_raw": live_raw[:30],
            "live_filtered": live_filtered,
            "core": core,
            "filter_stats": filter_stats,
        }
        try:
            with open(self.tracking_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"WARN Errore scrittura tracking: {e}")


if __name__ == "__main__":
    cloud = HashtagCloud(use_searxng=True, tracking_enabled=True)
    print("=" * 60)
    print("TEST HashtagCloud v3 - con filtri anti-rumore")
    print("=" * 60)
    tests = [
        ("cultura", "evento culturale cooperativa"),
        ("sociale", "inclusione migranti"),
        ("food", "cena solidale"),
    ]
    for category, topic in tests:
        print()
        print("-" * 60)
        print(f"Category: {category} | Topic: {topic}")
        print("-" * 60)
        result = cloud.get_hashtags(category, topic)
        stats = result["stats"]
        print()
        print("Statistiche:")
        print(f"   Live raw (SearXNG):    {stats['live_raw']}")
        print(f"   Live filtrati:         {stats['live_filtered']}")
        print(f"   Core (garantiti):      {stats['core']}")
        print(f"   Combined finale:       {stats['combined']}")
        print()
        print(f"   Scartati blacklist:    {stats['rejected_blacklist']}")
        print(f"   Scartati lunghezza:    {stats['rejected_length']}")
        print(f"   Scartati alfanum:      {stats['rejected_alpha']}")
        print(f"   Scartati coerenza:     {stats['rejected_coherence']}")
        print()
        print("COMBINED (output finale):")
        print(f"   {', '.join(result['combined'])}")
    print()
    print("=" * 60)
    print(f"Tracking: {TRACKING_FILE}")
    print("=" * 60)
