import re
from dataclasses import dataclass, field
from typing import List

@dataclass
class Topic:
    main_topic: str
    category: str
    keywords: List[str] = field(default_factory=list)
    confidence: float = 0.0

class TopicExtractor:
    def __init__(self):
        self.category_keywords = {
            "food": ["cena", "ristorante", "cibo", "vino", "gourmet", "food"],
            "tech": ["tech", "digitale", "software", "AI", "innovazione", "startup"],
            "cultura": ["mostra", "museo", "arte", "cultura", "teatro", "letteratura"],
            "sport": ["sport", "corsa", "calcio", "fitness", "gara", "atleta"],
            "moda": ["moda", "stile", "tendenza", "sfilata", "abbigliamento"],
            "musica": ["concerto", "musica", "live", "festival", "DJ", "rock", "jazz"],
            "beneficenza": ["beneficenza", "solidarietà", "donazioni", "volontariato"],
            "business": ["business", "imprenditoria", "networking", "conferenza"],
            "default": ["evento"]
        }
    
    def extract(self, text: str) -> Topic:
        text_lower = text.lower()
        category = "default"
        keywords = []
        max_score = 0
        
        for cat, words in self.category_keywords.items():
            matched = [w for w in words if re.search(r'\b' + re.escape(w.lower()) + r'\b', text_lower)]
            score = len(matched)
            if score > max_score:
                max_score = score
                category = cat
                keywords = matched
        
        words = text_lower.split()[:20]
        main_topic = " ".join(words[:3]) if words else "evento"
        
        return Topic(
            main_topic=main_topic,
            category=category,
            keywords=keywords,
            confidence=min(1.0, max_score / 5)
        )
