from pathlib import Path
import config
from hashtag_cloud import HashtagCloud
from hashtag_suggester import HashtagSuggester

class PromptBuilder:
    def __init__(self):
        self.prompt_file = Path(config.PROMPT_DIR) / "strategist.txt"
        self.hashtag_cloud = HashtagCloud()
        self.suggester = HashtagSuggester()
    
    def build(self, brief: str, topic, hashtag_pool: list, platforms: list = None) -> str:
        if self.prompt_file.exists():
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        else:
            system_prompt = "Sei uno strategist social media. Crea un piano social in JSON."
        
        # Estrai dati strutturati dal brief
        brief_data = {}
        for line in brief.split('\n'):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if "evento" in key or "nome" in key:
                    brief_data["nome_evento"] = value
                elif "data" in key:
                    brief_data["data"] = value
                elif "luogo" in key:
                    brief_data["luogo"] = value
                elif "target" in key:
                    brief_data["target"] = value
                elif "hashtag" in key:
                    brief_data["hashtag"] = value
                elif "descrizione" in key:
                    brief_data["descrizione"] = value
        
        # Ottieni hashtag dal cloud (fallback)
        cloud_hashtags = self.hashtag_cloud.get_hashtags(topic.category, topic.main_topic)
        
        # Genera suggerimenti hashtag dal brief
        suggestions = self.suggester.suggest(brief_data, count=8)
        
        # Costruisci una lista di hashtag consigliati (suggerimenti + cloud)
        if suggestions:
            suggested_str = ", ".join(suggestions)
        else:
            suggested_str = "Nessun suggerimento disponibile"
        
        # Sostituisci nel prompt
        prompt = system_prompt.replace("{brief}", brief)
        prompt = prompt.replace("{hashtag_suggestions}", suggested_str)
        prompt = prompt.replace("{cloud_hashtags}", ", ".join(cloud_hashtags[:10]))
        
        return prompt
