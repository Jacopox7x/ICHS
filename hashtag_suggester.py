"""
Generatore di suggerimenti hashtag da brief.
"""

import re
import random

class HashtagSuggester:
    def __init__(self):
        self.common_suffixes = {
            "tech": ["Tech", "Innovation", "Digital", "Startup", "Future"],
            "moda": ["Fashion", "Style", "Design", "Luxury", "Wearable"],
            "cibo": ["Food", "Taste", "Wine", "Gourmet", "Cooking"],
            "arte": ["Art", "Culture", "Exhibition", "Gallery", "Creative"],
            "sport": ["Sport", "Running", "Fitness", "Training", "Active"],
            "business": ["Business", "Strategy", "Leadership", "Growth", "Entrepreneur"],
            "green": ["Green", "Sustainability", "Eco", "Future", "Planet"],
            "musica": ["Music", "Festival", "Beat", "Live", "Sound"],
        }
    
    def suggest(self, brief: dict, count: int = 5) -> list:
        """Genera hashtag suggeriti dal brief."""
        suggestions = []
        
        # 1. Hashtag dal nome evento
        if "nome_evento" in brief:
            name_words = re.findall(r'\b\w{3,}\b', brief["nome_evento"])
            for word in name_words[:3]:
                suggestions.append(f"#{word}")
        
        # 2. Hashtag dal luogo
        if "luogo" in brief:
            luogo_words = re.findall(r'\b\w{3,}\b', brief["luogo"])
            for word in luogo_words[:2]:
                suggestions.append(f"#{word}")
        
        # 3. Hashtag da parole chiave del target
        if "target" in brief:
            target_words = re.findall(r'\b\w{4,}\b', brief["target"])
            for word in target_words[:3]:
                suggestions.append(f"#{word}")
        
        # 4. Hashtag da categoria (se identificata)
        if "categoria" in brief:
            categoria = brief["categoria"].lower()
            for key, suffixes in self.common_suffixes.items():
                if key in categoria or categoria in key:
                    for suffix in suffixes[:2]:
                        suggestions.append(f"#{suffix}")
        
        # 5. Hashtag da descrizione (parole lunghe)
        if "descrizione" in brief:
            desc_words = re.findall(r'\b\w{5,}\b', brief["descrizione"])
            for word in desc_words[:3]:
                suggestions.append(f"#{word}")
        
        # Pulisci e rendi unici
        suggestions = [re.sub(r'[^a-zA-Z0-9]', '', s) for s in suggestions]
        suggestions = list(dict.fromkeys(suggestions))  # mantiene ordine
        
        # Se ci sono hashtag dichiarati nel brief, li includiamo
        if "hashtag" in brief:
            declared = brief["hashtag"].split()
            suggestions = declared + [s for s in suggestions if s not in declared]
        
        # Limita il numero
        return suggestions[:count]
