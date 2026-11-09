"""
Hashtag Cloud per iCrawler
- Tenta di ottenere hashtag live da un'API esterna
- Fallback su hashtag locali se l'API non risponde
"""

import requests
import json
from typing import List, Optional
import random

# Configurazione
CLOUD_API_URL = "https://api.example.com/hashtags"  # Da sostituire con la tua API

# Hashtag di fallback (locali)
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
    "default": ["#evento", "#social", "#community", "#engagement", "#viral"]
}

class HashtagCloud:
    def __init__(self, api_url: str = CLOUD_API_URL):
        self.api_url = api_url
        self.cache = {}
    
    def get_hashtags(self, category: str, topic: str = "") -> List[str]:
        """Ottiene hashtag: prima dal cloud, poi fallback locale."""
        
        # 1. Prova a ottenere hashtag live dal cloud
        live_hashtags = self._fetch_from_cloud(category, topic)
        if live_hashtags:
            return live_hashtags
        
        # 2. Fallback: hashtag locali
        return self._get_fallback_hashtags(category)
    
    def _fetch_from_cloud(self, category: str, topic: str) -> Optional[List[str]]:
        """Tenta di ottenere hashtag dall'API cloud (DISABILITATO)."""
        # L'API è un placeholder, ritorniamo None per forzare il fallback locale.
        return None    
    def _get_fallback_hashtags(self, category: str) -> List[str]:
        """Restituisce hashtag locali di fallback."""
        pool = FALLBACK_HASHTAGS.get(category, FALLBACK_HASHTAGS["default"])
        random.shuffle(pool)
        return pool[:5]
    
    def inject_into_prompt(self, brief: str, category: str) -> str:
        """Inietta gli hashtag nel prompt."""
        hashtags = self.get_hashtags(category)
        hashtag_str = ", ".join(hashtags)
        
        return f"""
## HASHTAG AUTORIZZATI (dati dal cloud + fallback)
{hashtag_str}

**REGOLA:** Usa SOLO questi hashtag. NON inventare altri hashtag.
Se il brief contiene hashtag specifici, usali AL POSTO di quelli del cloud.
"""

# Esempio di utilizzo
if __name__ == "__main__":
    cloud = HashtagCloud()
    print("Hashtag per 'food':", cloud.get_hashtags("food"))
    print("Hashtag per 'tech':", cloud.get_hashtags("tech"))
    print("Hashtag per 'default':", cloud.get_hashtags("default"))
