import random
from typing import List
from pathlib import Path
import config

class HashtagEngine:
    def __init__(self):
        self.cache_dir = Path(config.CACHE_DIR)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.pools = {
            "food": {"primary": ["#food", "#cucina", "#ristorante", "#gourmet", "#foodie"], "secondary": ["#italianfood", "#cibo", "#sapori"]},
            "tech": {"primary": ["#tech", "#innovazione", "#digitale", "#AI", "#startup"], "secondary": ["#future", "#tecnologia"]},
            "cultura": {"primary": ["#cultura", "#arte", "#mostra", "#museo", "#teatro"], "secondary": ["#culturale", "#artecontemporanea"]},
            "sport": {"primary": ["#sport", "#fitness", "#competizione", "#allenamento", "#atleta"], "secondary": ["#motivation", "#running"]},
            "moda": {"primary": ["#moda", "#style", "#fashion", "#outfit", "#tendenza"], "secondary": ["#luxury", "#design"]},
            "musica": {"primary": ["#musica", "#concerto", "#live", "#artist", "#performance"], "secondary": ["#music", "#festival"]},
            "beneficenza": {"primary": ["#beneficenza", "#solidarietà", "#donazioni", "#volontariato"], "secondary": ["#aiuto", "#causa"]},
            "business": {"primary": ["#business", "#imprenditoria", "#networking", "#leadership"], "secondary": ["#crescita", "#professionisti"]},
            "default": {"primary": ["#evento", "#social", "#community", "#engagement"], "secondary": ["#viral", "#trending"]}
        }
        self.niche_tags = ["#innovazione", "#creatività", "#futuro", "#ispirazione"]
    
    def generate_pool_for_prompt(self, topic: str, category: str) -> List[str]:
        pool = self.pools.get(category, self.pools["default"])
        hashtags = pool.get("primary", []) + pool.get("secondary", [])
        hashtags += random.sample(self.niche_tags, min(2, len(self.niche_tags)))
        
        seen = set()
        hashtags = [h for h in hashtags if not (h in seen or seen.add(h))]
        return hashtags[:12]
